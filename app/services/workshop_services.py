from werkzeug.security import generate_password_hash

from app.common.errors import (
    AdminDeletionError,
    EntityNotFoundError,
    UserAlreadyExistsError,
)
from app.models.workshop import Workshop
from app.models.user_model import Roles
from app.schemas.workshop_schemas import WorkshopSchema


def get_workshop(workshop_id) -> (dict, int):
    workshop = Workshop.find_by_id(workshop_id=workshop_id)

    # Check if given workshop_id exists in DB
    if workshop is None:
        raise EntityNotFoundError

    return workshop, 200


def get_workshops_from_coach(coach_id) -> (dict, int):
    # Get all workshop from a given coach
    workshops = Workshop.find_by_coach_id(coach_id=coach_id)
    return workshops, 200


def create_workshop(data: bytes) -> (dict, int):
    data, err_msg, err_code = WorkshopSchema().loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    workshop = Workshop(**data).save()
    return workshop, 200


def delete_workshop(workshop_id: str) -> (dict, int):
    workshop = Workshop.find_by_id(workshop_id=workshop_id)

    # Check if given coach_id exists in DB
    if workshop is None:
        raise EntityNotFoundError
    # Delete user in DB
    workshop.delete()

    return {}, 204