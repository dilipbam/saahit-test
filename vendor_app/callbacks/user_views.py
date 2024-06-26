import asyncio
import logging
import re
import string, random
from datetime import datetime, timedelta

import flask_jwt_extended
import jwt
from flask import request, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, verify_jwt_in_request
from itsdangerous import Serializer, URLSafeTimedSerializer
from marshmallow import validate
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from utilities.mixins import VendorLoginRequiredMixin
from vendor_app.callbacks.user_validators import RegisterSchema, LoginSchema, VendorProfileSchema
from vendor_app.config import EMAIL, EMAIL_APP_PASSWORD
from vendor_app.utils.email_util import send_verification_email, send_password_reset_email
from vendor_app.utils.authentication_utils import load_current_user
from vendor_app.utils.image_utils import save_image
from utilities.db_getter import get_session

from utilities.responses import *
from utilities.dobato import DobatoApi  # TODO: change to dobato api for vendors as well

from utilities.schemas.models import User, VendorProfile, UserLogs


class Register(DobatoApi):
    """this view is for the vendor registration process"""

    def post(self):
        """
        API endpoint for user registration.

        Methods:
            post(): Handle POST requests for user registration.

        Usage:
            Send a POST request to '/vendor-api/register' with JSON payload containing
            'fullname', 'password', 'confirm_password', 'email', and 'phone_number' fields.

        Returns:
            JSON response with registration status and message.
        """
        data = request.json
        if 'phone_number' in data:
            data['phone_number'] = str(data['phone_number'])

        registration_schema = RegisterSchema()
        try:
            validated_data = registration_schema.load(data)
        except validate.ValidationError as err:
            return bad_request_error(msg=f"Validation Error {err}")

        password = validated_data.get('password')
        confirm_password = validated_data.get('confirm_password')
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')

        if password != confirm_password:
            return bad_request_error(msg="Passwords didn't match")

        self.password_validation(password)
        # check validation for email and phone number.
        errors = list()
        existing_user = self.db.query(User).filter(or_(User.email == email, User.phone_number == phone_number)).first()
        if existing_user:
            if existing_user.email == email:
                errors.append({"email": "Email already exists in the system."})
            if existing_user.phone_number == phone_number:
                errors.append({"phone_number": "Phone number already used for registration"})

        if errors:
            return conflict_error(
                msg="Registration failed",
                errors=errors
            )

        # generate verification mail
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # set new validated input for registration
        hashed_password = generate_password_hash(password)
        validated_data['password'] = hashed_password
        validated_data['user_type_id'] = self.get_vendor_type_id()
        validated_data['verification_code'] = verification_code
        validated_data['is_verified'] = False
        dt = datetime.now()
        validated_data['created_at'] = dt.strftime('%Y-%m-%d %H:%M:%S')
        validated_data.pop('confirm_password')

        try:
            new_user = User(**validated_data)
            self.db.add(new_user)
            self.db.commit()
            # Send verification email
            asyncio.run(self.send_message({'event': 'SEND_VERIFICATION_EMAIL',
                                           'params': {'sender_email': EMAIL,
                                                      'receiver_email': email,
                                                      'verification_code': verification_code,
                                                      'password': EMAIL_APP_PASSWORD}}, port=8888))
            return success_response('User registered successfully')
        except Exception as e:
            print(e)
            self.db.rollback()
            return server_error("Server Error Occurred while registering user")
        finally:
            self.db.close()

    def password_validation(self, password):
        if len(password) < 8:
            return bad_request_error('Password must be at least 8 characters long.')
        if not re.search(r'\d', password):
            return bad_request_error('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return bad_request_error('Password must contain at least one special character.')


class VerifyEmail(DobatoApi):
    def post(self):
        """
        API endpoint for user email verification.
        Methods:
            post(): Handle POST requests for user registration.

        Usage:
            Send a post request to '/vendor-api/verify-email' with JSON payload containing
            'email', 'verification_code' fields.
        Returns:
            JSON response with verification message.
        """
        data = request.json
        email = data.get('email')
        verification_code = data.get('verification_code')

        user = self.db.query(User).filter_by(email=email).first()
        if not user:
            return bad_request_error("Invalid user")

        if user.is_verified:
            return conflict_error(msg='Email already verified')
        elif not self.is_vendor(user.user_type_id):
            return bad_request_error(msg='User not registered as a vendor.')
        elif user.verification_code == verification_code:
            user.is_verified = True
            user.verification_code = None
            self.db.commit()
            self.db.close()
            return success_response(msg='Email verified successfully')
        else:
            return bad_request_error('Invalid verification code')


class VendorLogin(DobatoApi):
    def post(self):
        """
        API endpoint for vendor login.
        Methods:
            post(): Handle POST requests for user login.

        Usage:
            Send a POST request to '/vendor-api/login' with JSON payload containing
            'email', 'password' fields.

        Returns:
            JSON response with access_token, refresh_token and success message.
        """
        data = request.json
        login_schema = LoginSchema()
        try:
            validated_data = login_schema.load(data)
        except validate.ValidationError as err:
            return bad_request_error(msg=f"Validation Error {err}")

        email = validated_data.get('email')
        password = validated_data.get('password')

        dt = datetime.now()
        date_now = dt.strftime('%Y-%m-%d %H:%M:%S')

        user = self.db.query(User).filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return unauthorized_response(msg='Invalid username or password')

        if not self.is_vendor(user.user_type_id):
            return bad_request_error(msg='User not registered as a vendor.')

        if not user.is_verified:
            return unauthorized_response(msg='Email not verified yet.')

        user_log = {
            'action_performed': 'Logged-In',
            'action_time': datetime.now(),
            'user_id': user.id
        }
        try:
            new_log = UserLogs(**user_log)
            self.db.add(new_log)
            self.db.commit()
            # TODO: token expiry to be looked into.
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(1))
            refresh_token = create_refresh_token(identity=user.id, expires_delta=timedelta(1))
            data = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            return success_response(msg='User Logged-in successfully.', data=data)
        except Exception as e:
            self.db.rollback()
            return server_error("Server Error Occurred while logging in")
        finally:
            self.db.close()


class VendorLogout(DobatoApi):
    def post(self):
        """
        API endpoint for vendor logout.

        Methods:
            post(): Handle POST requests for vendor logout.

        Usage:
            Send a POST request to '/vendor-api/logout' with logged-in user

        Returns:
            JSON response with success message.
        """

        user = self.user
        if not user:
            return bad_request_error("Unauthorized user.")

        if not self.is_vendor(user.user_type_id):
            return bad_request_error(msg='User not registered as a vendor.')
        user_log = {
            'action_performed': 'Logged-Out',
            'action_time': datetime.now(),
            'user_id': user.id
        }
        try:
            new_log = UserLogs(**user_log)
            self.db.add(new_log)
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()
            return server_error("Server Error Occurred while logging out")
        finally:
            self.db.close()
        return success_response(msg=f"User logged out successfully")


# forgot password vendor
class ForgotPassword(DobatoApi):
    def post(self):
        """
        API endpoint for forgot-password.

        Methods:
            post(): Handle POST requests for password-forgot.

        Usage:
            Send a POST request to '/vendor-api/forgot-password' with JSON payload containing
            'email', 'reset_url' field.

        Returns:
            JSON response with success message.
        """
        email = request.json.get('email')
        reset_url = request.json.get('reset_url')
        user = self.db.query(User).filter_by(email=email).first()
        if user:
            if not self.is_vendor(user.user_type_id):
                return bad_request_error(msg='User not registered as a vendor.')
            reset_token = user.generate_reset_token()
            asyncio.run(self.send_message({'event': 'SEND_PASSWORD_RESET_LINK',
                                           'params': {'sender_email': EMAIL,
                                                      'receiver_email': email,
                                                      'password': EMAIL_APP_PASSWORD,
                                                      'token': reset_token,
                                                      'reset_url': reset_url
                                                      }}, port=8888))
            return success_response(msg='Password reset link sent to your email')
        else:
            return not_found_error(msg='Email not found')


# reset password vendor
class ResetPassword(DobatoApi):
    def post(self, token):
        """
        API endpoint for password-reset.

        Methods:
            post(): Handle POST requests for password-reset.

        Usage:
            Send a POST request to '/vendor-api/reset-password/<token>' with JSON payload containing
            'password' and 'confirm_password' fields.

        Returns:
            JSON response with success message.
        """
        s = URLSafeTimedSerializer(current_app.secret_key)
        try:
            user_token = s.loads(token, max_age=180)
            user = self.db.query(User).filter_by(id=user_token['user_id']).first()
            if not self.is_vendor(user.user_type_id):
                return bad_request_error(msg='User not registered as a vendor.')
            data = request.json
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            if password == confirm_password:
                new_password = generate_password_hash(password)
                user.password = new_password
                self.db.commit()
                self.db.close()
                return success_response(msg='Password reset successful')
            else:
                return bad_request_error(msg='Password and Confirm password did not match')
        except Exception:
            return forbidden_error(msg=f'Reset Password token expired')


class RefreshTokenApi(DobatoApi):
    def post(self):
        """
        API endpoint for user token refresh.

        Methods:
            post(): Handle POST requests for user token refresh.

        Usage:
            Send a POST request to '/vendor-api/refresh-token' with logged-in user

        Returns:
            JSON response with success message and new access and refresh token.
        """
        try:
            _, data = verify_jwt_in_request(refresh=True)
            user = self.db.query(User) \
                .filter(User.id == data['sub']) \
                .first()

            if user is None:
                return unauthorized_response(msg='User Not Found')
        except (jwt.exceptions.PyJWTError, flask_jwt_extended.exceptions.JWTExtendedException) as e:
            logging.exception('Failed to verify JWT Token')
            return unauthorized_response(msg='Invalid Refresh token')
        finally:
            self.db.close()

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return success_response(msg='Success', data={'access_token': access_token, 'refresh_token': refresh_token})


class ResendOTP(DobatoApi):

    def post(self):
        """
        API endpoint for resend otp for user email verification.

        Methods:
            post(): Handle POST requests for user registration.

        Usage:
            Send a post request to '/vendor-api/resend-otp' with json payload containing 'email'.

        Returns:
            JSON response with success message.
        """
        email = request.json.get('email')
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        try:
            user = self.db.query(User).filter_by(email=email).first()
            if not user:
                return bad_request_error(msg="User doesn't exists")
            if not self.is_vendor(user.user_type_id):
                return bad_request_error(msg='User not registered as a vendor.')
            if user.is_verified:
                return bad_request_error(msg="Email already verified.")
            # Send verification email
            send_verification_email(email, verification_code)
            user.verification_code = verification_code
            self.db.commit()
        except Exception as e:
            return server_error(e)
        finally:
            self.db.close()
        return success_response(msg="OTP sent successfully")


# VENDORS Profile-SECTION
class VendorProfileApi(DobatoApi):
    """
        API endpoint for managing vendor profiles.

        This class provides GET and POST methods to retrieve and create vendor profiles.
    """
    def post(self):
        """
        API endpoint for vendor profile creation.

        Methods:
            post(): Handle POST requests for vendor profile creation.

        Usage:
            Send a POST request to '/vendor-api/profile' with from-data containing
            'vendor_type', 'industry_id', 'profile_image', 'estd_date', 'location','pan_number',
            'pan_image', 'pan_holder_citizenship', 'pan_holder_photo' fields.

        Returns:
            JSON response with success status and message.
        """

        user = load_current_user()
        if user is None:
            return bad_request_error(msg='Invalid user or no authorization.')

        user_profile = self.db.query(VendorProfile).filter(VendorProfile.user_id == user.id).first()
        vendor_user_profile_schema = VendorProfileSchema()
        # TODO: validate data using marshmallow first and then save whatever is validated
        if user_profile:
            return bad_request_error(msg="Vendor profile already exists")

        data = request.form.to_dict()
        file_data = request.files.to_dict()

        # merging form_data and image data into a single dictionary
        data.update(file_data)
        # prepare data for the new profile

        try:
            validated_vendor_data = vendor_user_profile_schema.load(data)
            for key, image in file_data.items():
                filename = image.filename
                image_extension = filename.split('.')[-1]
                vendor_user_profile_schema.validate_image_extension(image_extension)
        except Exception as err:
            return bad_request_error(msg=f"Validation Error {err}")
        pan = self.db.query(VendorProfile).filter_by(pan_number=validated_vendor_data.get('pan_number')).first()
        if pan:
            return bad_request_error("PAN Number already in use.")
        # profile_image
        profile_image = validated_vendor_data.get('profile_image')
        if profile_image:
            profile_image_name = save_image(profile_image, user.id, 'profile_image')
            validated_vendor_data['profile_image'] = profile_image_name

        # pan_image
        pan_image = validated_vendor_data.get('pan_image')
        if pan_image:
            pan_image_name = save_image(pan_image, user.id, 'pan_image')
            validated_vendor_data['pan_image'] = pan_image_name

        # pan holder citizenship
        pan_holder_citizenship = validated_vendor_data.get('pan_holder_citizenship')
        if pan_holder_citizenship:
            pan_holder_citizenship_image_name = save_image(pan_holder_citizenship, user.id, 'pan_holder_citizenship')
            validated_vendor_data['pan_holder_citizenship'] = pan_holder_citizenship_image_name

        # pan holder photo
        pan_holder_photo = validated_vendor_data.get('pan_holder_photo')
        if pan_holder_photo:
            pan_holder_photo_name = save_image(pan_holder_photo, user.id, 'pan_holder_photo')
            validated_vendor_data['pan_holder_photo'] = pan_holder_photo_name

        validated_vendor_data['user_id'] = user.id
        validated_vendor_data['last_updated'] = datetime.now()

        try:
            # Create new profile
            new_profile = VendorProfile(**validated_vendor_data)
            self.db.add(new_profile)
            self.db.commit()
            return success_response(msg="Vendor Profile Created Successfully")
        except SQLAlchemyError as e:
            self.log_message(f"Database error while creating profile: {e}", _type='ERROR')
            self.db.rollback()
            return server_error(msg="Failed to create vendor profile")
        except Exception as e:
            self.log_message(f"Error while creating profile: {e}", _type='ERROR')
            self.db.rollback()
            return server_error(msg="Failed to create vendor profile")

        finally:
            self.db.close()


class VendorProfileDetailApi(DobatoApi):
    """
    Vendor profile detail api returns details for a specific vendor only
    """
    def get(self):
        """
        API endpoint to get vendor profile detail.

        **Endpoint:** `GET /vendor-api/profile-detail

        Methods:
            get(): Handle get requests for one specific vendor profile.
        Usage:
            Send a get request to '/vendor-api/profile-detail' with logged-in user.

        Returns: JSON response with vendor profile data.
        """

        if self.user is None:
            return unauthorized_response('Unauthorized User.')

        profile = (self.db.query(VendorProfile)
                   .join(User, User.id == VendorProfile.user_id)
                   .filter(VendorProfile.user_id == self.user.id).first())
        if profile:
            return self.detail_response(profile)
        else:
            return not_found_error('Profile not found.')

    def put(self):
        """
        API endpoint for vendor profile update.

        Methods:
            put(): Handle PUT requests for vendor profile update.

        Usage:
            Send a PUT request to '/vendor-api/profile-detail' with from-data containing
            'vendor_type', 'industry_id', 'profile_image', 'estd_date', 'location',
            'pan_number', 'pan_image', 'pan_holder_citizenship', 'pan_holder_photo' fields.

        Returns:
            JSON response with success status and message.
        """

        user = load_current_user()
        if user is None:
            return unauthorized_response(msg='Invalid user or no authorization.')

        user_profile = self.db.query(VendorProfile).filter(VendorProfile.user_id == user.id).first()
        if not user_profile:
            return bad_request_error(msg="Vendor profile doesn't exists")
        vendor_user_profile_schema = VendorProfileSchema()

        data = request.form.to_dict()
        file_data = request.files.to_dict()

        # merging form_data and image data into a single dictionary
        data.update(file_data)

        try:
            validated_vendor_data = vendor_user_profile_schema.load(data)
            for key, image in file_data.items():
                filename = image.filename
                image_extension = filename.split('.')[-1]
                vendor_user_profile_schema.validate_image_extension(image_extension)
        except Exception as err:
            return bad_request_error(msg=f"Validation Error {err}")

        # profile image
        profile_image = validated_vendor_data.get('profile_image')
        if profile_image:
            profile_image_name = save_image(profile_image, user.id, 'profile_image')
            validated_vendor_data['profile_image'] = profile_image_name

        # pan_image
        pan_image = validated_vendor_data.get('pan_image')
        if pan_image:
            pan_image_name = save_image(pan_image, user.id, 'pan_image')
            validated_vendor_data['pan_image'] = pan_image_name

        # pan holder citizenship
        pan_holder_citizenship = validated_vendor_data.get('pan_holder_citizenship')
        if pan_holder_citizenship:
            pan_holder_citizenship_image_name = save_image(pan_holder_citizenship, user.id, 'pan_holder_citizenship')
            validated_vendor_data['pan_holder_citizenship'] = pan_holder_citizenship_image_name

        # pan holder photo
        pan_holder_photo = validated_vendor_data.get('pan_holder_photo')
        if pan_holder_photo:
            pan_holder_photo_name = save_image(pan_holder_photo, user.id, 'pan_holder_photo')
            validated_vendor_data['pan_holder_photo'] = pan_holder_photo_name

        # Prepare data for the new profile
        validated_vendor_data['user_id'] = user.id
        validated_vendor_data['last_updated'] = datetime.now()

        try:
            # Update existing profile
            for key, value in validated_vendor_data.items():
                setattr(user_profile, key, value)
            self.db.commit()
            return success_response(msg="Vendor Profile Updated Successfully", data={})
        except SQLAlchemyError as e:
            self.log_message(f"Database error while updating profile: {e}", "ERROR")
            self.db.rollback()
            return server_error(msg="Failed to update vendor profile")
        except Exception as e:
            self.log_message(f"Error while updating profile: {e}", "ERROR")
            self.db.rollback()
            return server_error(msg="Failed to create vendor profile")

        finally:
            self.db.close()


class VendorBasicInfoApi(DobatoApi):
    def get(self):
        """
        API endpoint to get vendor basic info.

        **Endpoint:** `GET /vendor-api/basic-info

        Methods:
            get(): Handle get requests for one specific vendor basic info.
        Usage:
            Send a get request to '/vendor-api/basic-info' with logged-in user.

        Returns: JSON response with vendor basic info.
        """
        user = self.user
        if not user:
            return unauthorized_response("User doesn't exists")

        if not self.is_vendor(user.user_type_id):
            return unauthorized_response("User not registered as a vendor")

        user_data = self.db.query(User).filter(User.id == user.id).first()
        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()

        if not vendor_profile:
            new_user = True
            profile_verified = False
        else:
            new_user = False
            profile_verified = vendor_profile.is_sa_verified
        user_info = {
            'id': user_data.id,
            'business_name': user_data.fullname,
            'email': user_data.email,
            'email_verified': user_data.is_verified,
            'new_user': new_user,
            'profile_verified': profile_verified
        }
        self.db.close()
        return self.detail_response(user_info)
