from functools import wraps

from flask_jwt_extended import get_current_user

from app.common.errors import PermissionDeniedError
from app.models.user_model import Roles


def requires_access_level(access_level: Roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if user is None or not user.allowed(access_level):
                raise PermissionDeniedError
            return f(*args, **kwargs)

        return decorated_function

    return decorator
