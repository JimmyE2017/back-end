from enum import Enum


class ErrorType(Enum):
    AUTHORIZATION_ERROR = "Authorization Error"
    INVALID_DATA_ERROR = "Invalid Data Error"
    BAD_REQUEST_ERROR = "Bad Request Error"


class CustomException(Exception):
    error_type = None
    msg = ""
    code = 500
    details = None

    def __init__(self, msg: str = None, code: int = None, details: dict = None):
        if details:
            self.details = details
        if msg:
            self.msg = msg
        if code:
            self.code = code

    def get_content(self) -> dict:
        content = {"msg": f"{self.error_type.value}: {self.msg}"}
        if self.details:
            content.update({"details": self.details})
        return content


# Authorization Errors
class UnauthorizedTokenError(CustomException):
    error_type = ErrorType.AUTHORIZATION_ERROR
    msg = "Missing access token. You must login first."
    code = 401


class InvalidTokenError(CustomException):
    error_type = ErrorType.AUTHORIZATION_ERROR
    msg = "Invalid token."
    code = 401


class ExpiredTokenError(CustomException):
    error_type = ErrorType.AUTHORIZATION_ERROR
    msg = "Expired token. Please login again."
    code = 401


class RevokedTokenError(CustomException):
    error_type = ErrorType.AUTHORIZATION_ERROR
    msg = "Revoked token. Please login again."
    code = 401


class PermissionDeniedError(CustomException):
    error_type = ErrorType.AUTHORIZATION_ERROR
    msg = "Permission Denied."
    code = 403


# Invalid Data Errors
class EmailNotFoundError(CustomException):
    error_type = ErrorType.INVALID_DATA_ERROR
    msg = "Email not found."
    code = 404


class InvalidPasswordError(CustomException):
    error_type = ErrorType.INVALID_DATA_ERROR
    msg = "Incorrect password."
    code = 400


class InvalidDataError(CustomException):
    error_type = ErrorType.INVALID_DATA_ERROR
    msg = "Incorrect Data Error."
    code = 400


class UserAlreadyExistsError(CustomException):
    error_type = ErrorType.INVALID_DATA_ERROR
    msg = "User already exists."
    code = 400


class EntityNotFoundError(CustomException):
    error_type = ErrorType.INVALID_DATA_ERROR
    msg = "Entity not found."
    code = 404


class EmptyBodyError(CustomException):
    error_type = ErrorType.INVALID_DATA_ERROR
    msg = "Body should not be empty."
    code = 400
