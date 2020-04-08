from werkzeug.security import generate_password_hash

from app.common.errors import (
    AdminDeletionError,
    EntityNotFoundError,
    UserAlreadyExistsError,
)
from app.models.user_model import Roles, UserModel
from app.schemas.user_schemas import UserSchema


def get_moderator(moderator_id) -> (dict, int):
    moderator = UserModel.find_by_id(user_id=moderator_id)

    # Check if given moderator_id exists in DB
    if moderator is None:
        raise EntityNotFoundError

    return moderator, 200


def get_all_moderators() -> (dict, int):
    # Get all moderators
    moderators = UserModel.find_all_moderators()

    # TODO : Add pagination
    return moderators, 200


def create_moderator(data: bytes) -> (dict, int):
    data, err_msg, err_code = UserSchema().loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    user = UserModel(**data)

    # Check if user already exist
    if UserModel.find_by_email(user.email) is not None:
        raise UserAlreadyExistsError

    user.role = Roles.MODERATOR.value  # Setting role
    # Encrypt password
    if user.password and user.password != "":
        user.password = generate_password_hash(user.password)

    # Create user in DB
    user.save(force_insert=True)

    return user, 200


def delete_moderator(moderator_id: str) -> (dict, int):
    moderator = UserModel.find_by_id(user_id=moderator_id)

    # Check if given moderator_id exists in DB
    if moderator is None:
        raise EntityNotFoundError

    # Prevent deletion of admin
    if moderator.role == Roles.ADMIN.value:
        raise AdminDeletionError

    # Delete user in DB
    moderator.delete()

    return {}, 204
