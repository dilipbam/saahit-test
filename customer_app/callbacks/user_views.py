import asyncio
import io
import logging
import os
import random
import re
import string
import uuid
from datetime import datetime, timedelta

import flask_jwt_extended
import jwt
from PIL import Image
from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, verify_jwt_in_request
from itsdangerous import URLSafeTimedSerializer as Serializer
from marshmallow import ValidationError
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from customer_app.callbacks.user_validators import LoginSchema, RegisterSchema, UserProfileSchema
from customer_app.config import MEDIA_PATH, EMAIL, EMAIL_APP_PASSWORD
from customer_app.utils.authentication_utils import load_current_user
from utilities.dobato import DobatoApi
from customer_app.utils.email_util_b2c import send_verification_email, send_password_reset_email
from utilities.responses import success_response, server_error, validation_error
from utilities.responses import unauthorized_response, bad_request_error, forbidden_error, \
    not_found_error, conflict_error
from utilities.schemas.models import User, ConsumerProfile, UserLogs


class Register(DobatoApi):
    def post(self):
        """
        API endpoint for user registration.

        Methods:
            post(): Handle POST requests for user registration.

        Usage:
            Send a POST request to '/consumer-api/register' with JSON payload containing
            'fullname', 'password', 'confirm_password', 'email', and 'phone_number' fields.

        Returns:
            JSON response with registration status and message.
        """
        # TODO: Phone number sms verification

        data = request.json
        if 'phone_number' in data:
            data['phone_number'] = str(data['phone_number']).replace('-', '')

        register_schema = RegisterSchema()
        try:
            validated_data = register_schema.load(data)
        except ValidationError as e:
            error_message = "Validation failed: {}".format(e.messages)
            return server_error(error_message)
        except Exception as e:
            error_message = "An unexpected error occurred: {}".format(str(e))
            return server_error(error_message)

        password = validated_data.get('password')
        confirm_password = validated_data.get('confirm_password')
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')
        # validate unique username and email

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

        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        hashed_password = generate_password_hash(password)
        validated_data['password'] = hashed_password
        validated_data['user_type_id'] = self.get_consumer_type_id()
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
            return success_response(msg='User successfully registered.')
        except Exception as e:
            self.db.rollback()
            return jsonify({'message': str(e)})
        finally:
            self.db.close()

    def password_validation(self, password):
        if len(password) < 8:
            return validation_error('Password must be at least 8 characters long.')
        if not re.search(r'\d', password):
            return validation_error('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return validation_error('Password must contain at least one special character.')


class VerifyEmail(DobatoApi):
    def get(self):
        """
        API endpoint for user email verification.

        Methods:
            get(): Handle GET requests for user registration.

        Usage:
            Send a get request to '/consumer-api/verify-email' with JSON payload containing
            'email', 'verification_code'fields.

        Returns:
            JSON response with verification message.
        """
        # db = get_session()
        email = request.json['email']
        verification_code = request.json['verification_code']

        user = self.db.query(User).filter(User.email == email).first()
        if user:
            if user.is_verified:
                return conflict_error(msg='Email already verified')
            elif not self.is_consumer(user.user_type_id):
                return bad_request_error(msg='User not registered as a consumer.')
            elif user.verification_code == verification_code:
                user.is_verified = True
                user.verification_code = None
                self.db.commit()
                return success_response(msg='Email verified successfully')
            else:
                return jsonify({'message': 'Invalid verification code'}), 400
        return not_found_error(msg='Invalid User')


class ResendOTP(DobatoApi):
    def post(self):
        """
        API endpoint for resend otp for user email verification.

        Methods:
            post(): Handle POST requests for user registration.

        Usage:
            Send a post request to '/consumer-api/resend-otp' with logged-in user.

        Returns:
            JSON response with success message.
        """
        curr_user = load_current_user()
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        try:
            user = self.db.query(User).filter(User.id == curr_user.id).first()

            if not self.is_consumer(user.user_type_id):
                return bad_request_error(msg='User not registered as a consumer.')
            if user.is_verified:
                return bad_request_error(msg="Email already verified.")
            email = user.email
            # Send verification email
            asyncio.run(self.send_message({'event': 'SEND_VERIFICATION_EMAIL',
                                           'params': {'sender_email': EMAIL,
                                                      'receiver_email': email,
                                                      'verification_code': verification_code,
                                                      'password': EMAIL_APP_PASSWORD}}, port=8888))
            user.verification_code = verification_code
            self.db.commit()
        except Exception as e:
            return server_error(e)
        finally:
            self.db.close()
        return success_response(msg="OTP sent successfully")


class Login(DobatoApi):
    def post(self):
        """
        API endpoint for user login.

        Methods:
            post(): Handle POST requests for user login.

        Usage:
            Send a POST request to '/consumer-api/login' with JSON payload containing
            'email', 'password' fields.

        Returns:
            JSON response with access_token, refresh_token and success message.
        """
        data = request.json
        login_schema = LoginSchema()
        try:
            validated_data = login_schema.load(data)
        except ValidationError as e:
            self.log_message(str(e))
            return server_error(msg=f"Validation failed for the login credentials. {str(e)}")

        email = validated_data.get('email')
        password = validated_data.get('password')

        dt = datetime.now()
        date_now = dt.strftime('%Y-%m-%d %H:%M:%S')

        user = self.db.query(User).filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return unauthorized_response(msg='Invalid email or password')

        if not self.is_consumer(user.user_type_id):
            return bad_request_error(msg='User not registered as a consumer.')

        user_log = {
            'action_performed': 'Logged-In',
            'action_time': datetime.now(),
            'user_id': user.id
        }
        try:
            new_log = UserLogs(**user_log)
            self.db.add(new_log)
            self.db.commit()
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(1))
            refresh_token = create_refresh_token(identity=user.id, expires_delta=timedelta(1))
            data = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            self.log_message(f"User successfully logged in at: {datetime.now()}")
            return success_response(msg='User Logged-in successfully.', data=data)
        except Exception as e:
            self.log_message(str(e))
            return server_error("Server Error Occurred")
        finally:
            self.db.close()


class Logout(DobatoApi):
    def post(self):
        """
        API endpoint for user logout.

        Methods:
            post(): Handle POST requests for user logout.

        Usage:
            Send a POST request to '/consumer-api/logout' with logged-in user

        Returns:
            JSON response with success message.
        """
        user = self.db.query(User).filter_by(id=self.user.id).first()
        if not user:
            return unauthorized_response(msg={"User not registered"})

        if not self.is_consumer(user.user_type_id):
            return bad_request_error(msg='User not registered as a consumer.')
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


class RefreshTokenApi(DobatoApi):
    def post(self):
        """
        API endpoint for user token refresh.

        Methods:
            post(): Handle POST requests for user token refresh.

        Usage:
            Send a POST request to '/consumer-api/refresh-token' with logged-in user

        Returns:
            JSON response with success message and new access and refresh token.
        """
        # db = get_session()
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


class ForgotPassword(DobatoApi):
    def post(self):
        """
        API endpoint for forgot-password.

        Methods:
            post(): Handle POST requests for password-forgot.

        Usage:
            Send a POST request to '/consumer-api/forgot-password' with JSON payload containing
            'email', 'reset_url' field.

        Returns:
            JSON response with success message.
        """
        email = request.json.get('email')
        reset_url = request.json.get('reset_url')
        user = self.db.query(User).filter_by(email=email).first()
        if user:
            if not self.is_consumer(user.user_type_id):
                return bad_request_error(msg='User not registered as a consumer.')
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


class ResetPassword(DobatoApi):
    def post(self, token):
        """
        API endpoint for password-reset.

        Methods:
            post(): Handle POST requests for password-reset.

        Usage:
            Send a POST request to '/consumer-api/reset-password/<token>' with JSON payload containing
            'password' and 'confirm_password' fields.

        Returns:
            JSON response with success message.
        """
        # db = get_session()
        s = Serializer(current_app.secret_key)
        try:
            user_token = s.loads(token, max_age=360)
            user = self.db.query(User).filter_by(id=user_token['user_id']).first()
            if not self.is_consumer(user.user_type_id):
                return bad_request_error(msg='User not registered as a consumer.')
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
            return forbidden_error(msg=f'Signature token expired')


class CustomerProfile(DobatoApi):
    def get(self):
        """
        API endpoint for customer-profile.

        Methods:
            get(): Handle GET requests for customer-profile.

        Usage:
            Send a GET request to '/consumer-api/profile' with logged-in user

        Returns:
            JSON response with user data.
        """
        # session = get_session()
        user = load_current_user()
        if user:
            profile = (self.db.query(User, ConsumerProfile)
                       .outerjoin(ConsumerProfile, User.id == ConsumerProfile.user_id)
                       .filter(User.id == user.id)
                       .with_entities(User.fullname, User.phone_number,
                                      User.email, ConsumerProfile.image,
                                      ConsumerProfile.last_updated, ConsumerProfile.gender).first())._asdict()
            if profile:
                return jsonify(profile)
            else:
                return not_found_error('Profile not found.')
        else:
            return unauthorized_response(msg="Unauthorized User")  # Invalid user error 401 in custom errors

    def post(self):
        """
        API endpoint for customer-profile.

        Methods:
            post(): Handle POST requests for customer-profile.

        Usage:
            Send a GET request to '/consumer-api/profile' with JSON payload containing
            'image' and 'gender' fields with logged-in user.

        Returns:
            JSON response with success message.
        """
        # session = get_session()
        user = load_current_user()

        user_profile = self.db.query(ConsumerProfile).filter(ConsumerProfile.user_id == user.id).first()
        user_profile_schema = UserProfileSchema()

        if user_profile:
            return bad_request_error(msg='User profile already exists')

        request_data = request.form
        image = request.files.get('image')

        # Extract image extension from filename
        image_extension = image.filename.split('.')[-1]

        # Validate image extension
        user_profile_schema.validate_image_extension(image_extension)

        # Generate unique name for the image
        unique_name = str(uuid.uuid4())
        img_name = unique_name + '.' + image_extension.lower()  # image.filename + image_extension.lower()

        # Read image in memory
        with Image.open(image) as img:
            # Convert image to RGB mode
            img = img.convert('RGB')
            # Resize image to 300x300
            img.thumbnail((400, 400))
            # Save resized image to memory
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG')
            img_io.seek(0)

        # Save image to disk
        image_path = os.path.join(MEDIA_PATH, img_name)
        with open(image_path, 'wb') as f:
            f.write(img_io.read())

        # Prepare data for the new profile
        data = request.form.to_dict()
        data['image'] = img_name
        data['user_id'] = user.id
        dt = datetime.now()
        updated_date = dt.strftime('%Y-%m-%d')
        data['last_updated'] = updated_date
        try:
            # Create new profile
            new_profile = ConsumerProfile(**data)
            self.db.add(new_profile)
            self.db.commit()
            return success_response(msg="User Profile Created Successfully")
        except Exception as e:
            print(e)
            return server_error(msg="Failed to create user profile")
        finally:
            self.db.close()


class UpdateProfile(DobatoApi):
    def post(self, user_id):
        """
        API endpoint for customer-profile-update.

        Methods:
            post(): Handle POST requests for customer-profile-update.

        Usage:
            Send a GET request to '/consumer-api/update-profile/<int:user_id>' with JSON payload containing
            'image' and 'gender' fields with logged-in user.

        Returns:
            JSON response with success message.
        """
        # session = get_session()

        user_profile = self.db.query(ConsumerProfile).filter(ConsumerProfile.user_id == user_id).first()
        user_profile_schema = UserProfileSchema()

        if not user_profile:
            return bad_request_error(msg='User profile does not exist')

        request_data = request.form
        image = request.files.get('image')

        gender = request_data.get('gender')
        if gender:
            user_profile.gender = gender

        if image:
            # Extract image extension from filename
            image_extension = image.filename.split('.')[-1]

            # Validate image extension
            user_profile_schema.validate_image_extension(image_extension)

            # Generate unique name for the image
            unique_name = str(uuid.uuid4())
            img_name = unique_name + '.' + image_extension.lower()  # image.filename + image_extension.lower()

            # Read image in memory
            with Image.open(image) as img:
                # Convert image to RGB mode
                img = img.convert('RGB')
                # Resize image to 300x300
                img.thumbnail((300, 300))
                # Save resized image to memory
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG')
                img_io.seek(0)

            # Save image to disk
            image_path = os.path.join(MEDIA_PATH, img_name)
            with open(image_path, 'wb') as f:
                f.write(img_io.read())

            user_profile.image = img_name  # Update image path in the profile data

        dt = datetime.now()
        updated_date = dt.strftime('%Y-%m-%d')
        user_profile.last_updated = updated_date

        try:
            self.db.commit()
            return success_response(msg="User Profile Updated Successfully")
        except Exception as e:
            print(e)
            return server_error(msg="Failed to update user profile")
        finally:
            self.db.close()
