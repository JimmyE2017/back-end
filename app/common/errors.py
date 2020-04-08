from enum import Enum


class ErrorType(Enum):
    AUTHORIZATION_ERROR = "Authorization Error"
    INVALID_DATA_ERROR = "Invalid Data Error"
    BAD_REQUEST_ERROR = "Bad Request Error"


class BaseError(object):
    def __init__(self, type_error: ErrorType, msg: str, error_code: int):
        self.msg = msg
        self.type_error = type_error
        self.error_code = error_code
        self.content = {"msg": f"{self.type_error.value}: {self.msg}"}

    def get_error(self) -> (dict, int):
        return self.content, self.error_code


# Authorization errors
UNAUTHORIZED_TOKEN = BaseError(
    ErrorType.AUTHORIZATION_ERROR, "Missing access token. You must login first.", 401
)
EXPIRED_TOKEN = BaseError(
    ErrorType.AUTHORIZATION_ERROR, "Expired token. Please login again.", 401
)
INVALID_TOKEN = BaseError(ErrorType.AUTHORIZATION_ERROR, "Invalid token.", 401)
REVOKED_TOKEN = BaseError(
    ErrorType.AUTHORIZATION_ERROR, "Revoked token. Please login again.", 401
)
PERMISSION_DENIED = BaseError(ErrorType.AUTHORIZATION_ERROR, "Permission Denied.", 403)

# Invalid data errors
EMAIL_NOT_FOUND_ERROR = BaseError(ErrorType.INVALID_DATA_ERROR, "Email not found", 404)
INVALID_PASSWORD_ERROR = BaseError(
    ErrorType.INVALID_DATA_ERROR, "Incorrect password", 400
)
INVALID_DATA_ERROR = BaseError(
    ErrorType.INVALID_DATA_ERROR, "Error while loading data.", 400
)
USER_ALREADY_EXISTS_ERROR = BaseError(
    ErrorType.INVALID_DATA_ERROR, "User already exists.", 400
)
ENTITY_NOT_FOUND_ERROR = BaseError(
    ErrorType.BAD_REQUEST_ERROR, "Entity not found.", 404
)
EMPTY_BODY_ERROR = BaseError(
    ErrorType.INVALID_DATA_ERROR, "Body should not be empty", 400
)
ADMIN_DELETION_ERROR = BaseError(
    ErrorType.INVALID_DATA_ERROR, "Admin user can't be deleted.", 409
)
