from flask_jwt_extended import create_access_token, decode_token, get_raw_jwt
from werkzeug.security import check_password_hash, generate_password_hash

from app.common.errors import (
    EMAIL_NOT_FOUND_ERROR,
    ENTITY_NOT_FOUND_ERROR,
    INVALID_PASSWORD_ERROR,
    USER_ALREADY_EXISTS_ERROR,
    BaseError,
    ErrorType,
)
from app.models.user_model import BlacklistTokenModel, Roles, UserModel
from app.schemas.user_schemas import (
    ForgottenPasswordSchema,
    LoginSchema,
    NewPasswordSchema,
    UserSchema,
)


def login(data: bytes) -> (dict, int):
    # Deserialize data
    data, err_msg, err_code = LoginSchema().loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    user = UserModel.find_by_email(email=data["email"])

    if user is None:
        return EMAIL_NOT_FOUND_ERROR.get_error()

    if not check_password_hash(pwhash=user.password, password=data["password"]):
        return INVALID_PASSWORD_ERROR.get_error()

    access_token = create_access_token(identity=user.id, fresh=True)

    return {"access_token": access_token}, 200


def logout() -> (dict, int):
    jti = get_raw_jwt()["jti"]
    blacklisted_token = BlacklistTokenModel(token=jti)
    blacklisted_token.save(force_insert=True)  # Inserting in DB

    return None, 204


def forgotten_password(data: bytes) -> (dict, int):
    # Deserialize data
    data, err_msg, err_code = ForgottenPasswordSchema().loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    # Get user from email
    user = UserModel.find_by_email(email=data["email"])
    if user is None:
        return EMAIL_NOT_FOUND_ERROR.get_error()

    user.send_reset_password_mail()

    return None, 204


def update_password(params: dict, data: bytes) -> (None, int):
    # Validate and decode access token
    if "access_token" not in params:
        error = BaseError(
            ErrorType.AUTHORIZATION_ERROR,
            "Missing access token. You must add an access_token parameter",
            401,
        )
        return error.get_error()
    token = params.get("access_token")
    decoded_token = decode_token(token)

    user = UserModel.find_by_id(user_id=decoded_token.get("identity"))
    if user is None:
        return ENTITY_NOT_FOUND_ERROR.get_error()

    # Load new password
    data, err_msg, err_code = NewPasswordSchema().loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    user.password = generate_password_hash(data["password"])
    user.save()

    return None, 204


def create_admin_user(data: bytes) -> (dict, int):
    data, err_msg, err_code = UserSchema().loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    user = UserModel(**data)
    # Check if user already exist
    if UserModel.find_by_email(user.email) is not None:
        return USER_ALREADY_EXISTS_ERROR.get_error()

    # Setting userId, role and encrypt password
    user.role = Roles.ADMIN.value
    user.password = generate_password_hash(user.password)

    # Create user in DB
    user.save(force_insert=True)

    return user, 200
