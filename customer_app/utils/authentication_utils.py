from flask_jwt_extended import verify_jwt_in_request, get_current_user, jwt_required
from flask_jwt_extended.exceptions import NoAuthorizationError

from utilities.db_getter import get_session
from utilities.schemas.models import UserType


def load_current_user():
    try:
        verify_jwt_in_request()
    except NoAuthorizationError:
        return None
    return get_current_user()

