from flask_jwt_extended import (
    create_access_token,
    decode_token,
    get_jwt_identity,
    get_raw_jwt,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.common.errors import (
    EmailNotFoundError,
    EntityNotFoundError,
    InvalidPasswordError,
    InvalidTokenError,
)
from app.models.user_model import BlacklistTokenModel, Roles, UserModel
from app.schemas.user_schemas import (
    CoachSchema,
    ForgottenPasswordSchema,
    LoginSchema,
    NewPasswordSchema,
)


def login(data: bytes) -> (dict, int):
    # Deserialize data
    data, err_msg, err_code = LoginSchema().loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    user = UserModel.find_by_email(email=data["email"])

    if user is None:
        raise EmailNotFoundError

    if not check_password_hash(pwhash=user.password, password=data["password"]):
        raise InvalidPasswordError

    # Generate access token
    access_token = create_access_token(identity=user.id, fresh=True)
    output_data = {"access_token": access_token}

    return output_data, 200


def logout() -> (dict, int):
    jti = get_raw_jwt()["jti"]
    blacklisted_token = BlacklistTokenModel(token=jti)
    blacklisted_token.save(force_insert=True)  # Inserting in DB

    return None, 204


def get_me() -> (dict, int):
    current_user_id = get_jwt_identity()

    current_user = UserModel().find_by_id(user_id=current_user_id)

    if current_user is None:
        raise EntityNotFoundError

    output_data = {}
    if Roles.COACH.value in current_user.role:
        output_data = CoachSchema().dump(current_user)

    return output_data, 200


def forgotten_password(data: bytes) -> (dict, int):
    # Deserialize data
    data, err_msg, err_code = ForgottenPasswordSchema().loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    # Get user from email
    user = UserModel.find_by_email(email=data["email"])
    if user is None:
        raise EmailNotFoundError

    user.send_reset_password_mail()

    return None, 204


def update_password(params: dict, data: bytes) -> (None, int):
    # Validate and decode access token
    if "access_token" not in params:
        error = InvalidTokenError()
        error.msg = ("Missing access token. You must add an access_token parameter",)
        raise error
    token = params.get("access_token")
    decoded_token = decode_token(token)

    user = UserModel.find_by_id(user_id=decoded_token.get("identity"))
    if user is None:
        raise EntityNotFoundError

    # Load new password
    data, err_msg, err_code = NewPasswordSchema().loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    user.password = generate_password_hash(data["password"])
    user.save()

    return None, 204
