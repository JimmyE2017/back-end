from werkzeug.security import generate_password_hash

from app.common.errors import EntityNotFoundError, UserAlreadyExistsError
from app.models.action_card_model import ActionCardBatchModel
from app.models.user_model import Roles, UserModel
from app.schemas.user_schemas import CoachSchema


def get_coach(coach_id) -> (dict, int):
    coach = UserModel.find_coach_by_id(user_id=coach_id)

    # Check if given coach_id exists in DB
    if coach is None:
        raise EntityNotFoundError

    return CoachSchema().dump(coach), 200


def get_all_coachs() -> (dict, int):
    # Get all coachs
    coachs = UserModel.find_all_coaches()
    schema = CoachSchema(many=True)
    return schema.dump(coachs), 200


def create_coach(data: bytes) -> (dict, int):
    schema = CoachSchema()
    data, err_msg, err_code = schema.loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    role = data.pop("role")

    # Check if user already exist
    user = UserModel.find_by_email(data["email"])
    if user is not None:
        if Roles.COACH.value in user.role:
            # raise exception if user is already a coach
            raise UserAlreadyExistsError
        else:
            # Otherwise, update role
            user.role.append(Roles.COACH.value)
    else:
        user = UserModel(**data)
        user.role = [Roles.COACH.value]

    # Setting admin role if needed
    if role == "admin":
        user.role.append(Roles.ADMIN.value)

    # Encrypt password
    if user.password and user.password != "":
        user.password = generate_password_hash(user.password)

    # Create user in DB
    user.save()

    # Generate default action card batches
    default_action_card_batches = ActionCardBatchModel.find_default_batches()
    for default_action_card_batch in default_action_card_batches:
        ActionCardBatchModel(
            coachId=user.id,
            name=default_action_card_batch.name,
            actionCards=default_action_card_batch.actionCards,
            type=default_action_card_batch.type,
        ).save()

    return schema.dump(user), 200


def delete_coach(coach_id: str) -> (dict, int):
    coach = UserModel.find_coach_by_id(user_id=coach_id)

    # Check if given coach_id exists in DB
    if coach is None:
        raise EntityNotFoundError

    # Delete user in DB
    coach.delete()

    return {}, 204
