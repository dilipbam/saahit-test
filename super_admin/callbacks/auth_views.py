import logging

from datetime import datetime, timedelta

import flask_jwt_extended
import jwt
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, verify_jwt_in_request

from werkzeug.security import check_password_hash

from customer_app.callbacks.user_validators import LoginSchema

from customer_app.utils.authentication_utils import load_current_user

from utilities.dobato import DobatoApi

from utilities.responses import success_response
from utilities.responses import unauthorized_response, bad_request_error
from utilities.schemas.models import User



class Login(DobatoApi):
    def post(self):
        """
        API endpoint for user login.

        Methods:
            post(): Handle POST requests for user login.

        Usage:
            Send a POST request to '/consumer-api/login' with JSON payload containing
            'username', 'password' fields.

        Returns:
            JSON response with access_token, refresh_token and success message.
        """
        data = request.json
        login_schema = LoginSchema()
        try:
            validated_data = login_schema.load(data)
        except:
            raise Exception

        username = validated_data.get('username')
        password = validated_data.get('password')

        dt = datetime.now()
        date_now = dt.strftime('%Y-%m-%d %H:%M:%S')

        user = self.db.query(User).filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return unauthorized_response(msg='Invalid username or password')

        if user.user_type_id != self.get_consumer_type_id():
            return bad_request_error(msg="Invalid User Type.")

        user.logged_in_at = date_now
        user.logged_out_at = None
        self.db.commit()
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(3600))
        refresh_token = create_refresh_token(identity=user.id, expires_delta=timedelta(3600))
        self.db.close()
        data = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return success_response(msg='User Logged-in successfully.', data=data)


class Logout(DobatoApi):
    def post(self):
        """
        API endpoint for user login.

        Methods:
            post(): Handle POST requests for user logout.

        Usage:
            Send a POST request to '/consumer-api/logout' with logged-in user

        Returns:
            JSON response with success message.
        """
        # session = get_session()
        curr_user = load_current_user()
        user = self.db.query(User).filter_by(id=curr_user.id).first()
        if not user:
            return unauthorized_response(msg={"User not registered"})
        dt = datetime.now()
        date_now = dt.strftime('%Y-%m-%d %H:%M:%S')
        user.logged_out_at = date_now
        self.db.commit()
        return success_response(msg=f"User {user.username} logged out successfully")

class RefreshTokenApi(DobatoApi):
    def post(self):
        """
        API endpoint for user login.

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




