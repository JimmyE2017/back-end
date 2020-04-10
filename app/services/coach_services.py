from werkzeug.security import generate_password_hash

from app.common.errors import (
    AdminDeletionError,
    EntityNotFoundError,
    UserAlreadyExistsError,
)
from app.models.coach_model import CoachModel
from app.models.user_model import Roles
from app.schemas.coach_schemas import CoachSchema


def get_coach(coach_id) -> (dict, int):
    coach = CoachModel.find_by_id(user_id=coach_id)

    # Check if given coach_id exists in DB
    if coach is None:
        raise EntityNotFoundError

    return coach, 200


def get_all_coachs() -> (dict, int):
    # Get all coachs
    coachs = CoachModel.find_all_coaches()

    # TODO : Add pagination
    return coachs, 200


def create_coach(data: bytes) -> (dict, int):
    data, err_msg, err_code = CoachSchema().loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    user = CoachModel(**data)

    # Check if user already exist
    if CoachModel.find_by_email(user.email) is not None:
        raise UserAlreadyExistsError

    user.role = [Roles.COACH.value]  # Setting role
    # Encrypt password
    if user.password and user.password != "":
        user.password = generate_password_hash(user.password)

    # Create user in DB
    user.save(force_insert=True)

    return user, 200


def delete_coach(coach_id: str) -> (dict, int):
    coach = CoachModel.find_by_id(user_id=coach_id)

    # Check if given coach_id exists in DB
    if coach is None:
        raise EntityNotFoundError

    # Prevent deletion of admin
    if coach.role == Roles.ADMIN.value:
        raise AdminDeletionError

    # Delete user in DB
    coach.delete()

    return {}, 204


def create_admin_user(data: bytes) -> (dict, int):
    data, err_msg, err_code = CoachSchema().loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    user = CoachModel(**data)
    # Check if user already exist
    if CoachModel.find_by_email(user.email) is not None:
        raise UserAlreadyExistsError

    # Setting userId, role and encrypt password
    user.role = [Roles.ADMIN.value, Roles.COACH.value]
    user.password = generate_password_hash(user.password)

    # Create user in DB
    user.save(force_insert=True)

    return user, 200
