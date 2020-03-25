from flask_jwt_extended import create_access_token, get_raw_jwt
from marshmallow import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from app.common.errors import (
    UNSUCCESSFUL_LOGIN_EMAIL_NOT_FOUND,
    UNSUCCESSFUL_LOGIN_WRONG_PASSWORD,
    USER_ALREADY_EXISTS_ERROR,
)
from app.models import db
from app.models.user_model import BlacklistTokenModel, Roles, UserModel
from app.schemas.user_schema import LoginSchema, UserSchema


def login(data: bytes) -> (dict, int):
    # Deserialized data
    schema = LoginSchema()
    try:
        data = schema.loads(data)
    except ValidationError as err:
        return err.messages, 400

    user = UserModel.find_by_email(email=data["email"])

    if user is None:
        return UNSUCCESSFUL_LOGIN_EMAIL_NOT_FOUND.get_error()

    if not check_password_hash(pwhash=user.password, password=data["password"]):
        return UNSUCCESSFUL_LOGIN_WRONG_PASSWORD.get_error()

    access_token = create_access_token(identity=user.user_id, fresh=True)

    return {"access_token": access_token}, 200


def logout() -> (dict, int):
    jti = get_raw_jwt()["jti"]
    blacklisted_token = BlacklistTokenModel(jti=jti)
    db.session.add(blacklisted_token)
    db.session.commit()

    return None, 204


def create_admin_user(data: bytes) -> (dict, int):
    # Deserialized data
    schema = UserSchema()
    try:
        user = schema.loads(data)
    except ValidationError as err:
        return err.messages, 400

    # Check if user already exist
    if UserModel.find_by_email(user.email) is not None:
        return USER_ALREADY_EXISTS_ERROR.get_error()

    user.role = Roles.ADMIN.value  # Setting role

    # Encrypt password
    user.password = generate_password_hash(user.password)

    # Create user in DB
    db.session.add(user)
    db.session.commit()

    return schema.dump(user), 200
