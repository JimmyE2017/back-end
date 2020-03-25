from marshmallow import ValidationError
from werkzeug.security import generate_password_hash

from app.common.errors import (
    ADMIN_DELETION_ERROR,
    ENTITY_NOT_FOUND_ERROR,
    USER_ALREADY_EXISTS_ERROR,
)
from app.models import db
from app.models.user_model import Roles, UserModel
from app.schemas.user_schema import UserSchema


def get_all_moderators() -> (dict, int):
    # Get all moderators
    moderators = UserModel.find_all_moderators()

    # Serialize data
    schema = UserSchema(many=True)
    data = schema.dump(moderators)

    # TODO : Add pagination
    return data, 200


def create_moderator(data: bytes) -> (dict, int):
    # Deserialized data
    schema = UserSchema()
    try:
        user = schema.loads(data)
    except ValidationError as err:
        return err.messages, 400

    # Check if user already exist
    if UserModel.find_by_email(user.email) is not None:
        return USER_ALREADY_EXISTS_ERROR.get_error()

    user.role = Roles.MODERATOR.value  # Setting role

    # Encrypt password
    user.password = generate_password_hash(user.password)

    # Create user in DB
    db.session.add(user)
    db.session.commit()

    return schema.dump(user), 200


def delete_moderator(moderator_id: int) -> (dict, int):
    moderator = UserModel.find_by_id(user_id=moderator_id)

    # Check if given moderator_id exists in DB
    if moderator is None:
        return ENTITY_NOT_FOUND_ERROR.get_error()

    # Prevent deletion of admin
    if moderator.role == Roles.ADMIN.value:
        return ADMIN_DELETION_ERROR.get_error()

    # Delete user in DB
    db.session.delete(moderator)
    db.session.commit()

    return {}, 204
