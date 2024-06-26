from functools import wraps

import flask_jwt_extended.exceptions
from flask import redirect, url_for, request
from flask_jwt_extended import current_user, verify_jwt_in_request

from utilities.responses import unauthorized_response


class VendorLoginRequiredMixin(object):
    @classmethod
    def login_required(cls,f,refresh=False):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request(refresh=refresh)
                if current_user.is_authenticated and not current_user.user_type_id==3:
                    return unauthorized_response(msg='Invalid Vendor')
            except flask_jwt_extended.exceptions.NoAuthorizationError:
                return unauthorized_response(msg="Vendor Login Required!")
            except flask_jwt_extended.exceptions.WrongTokenError:
                return unauthorized_response(msg='Token Invalid!')
            except flask_jwt_extended.exceptions.FreshTokenRequired:
                return unauthorized_response(msg='Token Expired!')
            except Exception as e:
                return unauthorized_response(msg='Login Required!')
            if not current_user.is_authenticated:
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function

