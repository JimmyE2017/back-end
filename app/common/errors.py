from enum import Enum


class TypeError(Enum):
    LOGIN_ERROR = "Login Error"
    AUTHORIZATION_ERROR = "Authorization Error"
    INVALID_DATA_ERROR = "Invalid Data"


class BaseError(object):
    def __init__(self, type_error: TypeError, msg: str, error_code: int):
        self.msg = msg
        self.type_error = type_error
        self.error_code = error_code
        self.content = {self.type_error.value: msg}

    def get_error(self) -> (dict, int):
        return self.content, self.error_code


# Login errors
UNSUCCESSFUL_LOGIN_EMAIL_NOT_FOUND = BaseError(
    TypeError.LOGIN_ERROR, "Email not found", 401
)
UNSUCCESSFUL_LOGIN_WRONG_PASSWORD = BaseError(
    TypeError.LOGIN_ERROR, "Incorrect password", 401
)

# Authorization errors
UNAUTHORIZED_TOKEN = BaseError(
    TypeError.AUTHORIZATION_ERROR, "Missing access token. You must login first.", 401
)
EXPIRED_TOKEN = BaseError(
    TypeError.AUTHORIZATION_ERROR, "Expired token. Please login again.", 401
)
INVALID_TOKEN = BaseError(TypeError.AUTHORIZATION_ERROR, "Invalid token.", 401)
REVOKED_TOKEN = BaseError(
    TypeError.AUTHORIZATION_ERROR, "Revoked token. Please login again.", 401
)
PERMISSION_DENIED = BaseError(TypeError.AUTHORIZATION_ERROR, "Permission Denied.", 403)

# Invalid data errors
USER_ALREADY_EXISTS_ERROR = BaseError(
    TypeError.INVALID_DATA_ERROR, "User already exists.", 400
)
ENTITY_NOT_FOUND_ERROR = BaseError(
    TypeError.INVALID_DATA_ERROR, "Entity not found.", 404
)
ADMIN_DELETION_ERROR = BaseError(
    TypeError.INVALID_DATA_ERROR, "Admin user can't be deleted.", 409
)
