from flask_jwt_extended import get_jwt_identity

from app.common.errors import EntityNotFoundError
from app.models.action_card_model import ActionCardBatchModel, ActionCardModel
from app.models.model_model import Model
from app.models.user_model import UserModel
from app.models.workshop_model import WorkshopModel, WorkshopParticipants
from app.schemas.user_schemas import UserSchema
from app.schemas.workshop_schemas import WorkshopDetailSchema, WorkshopSchema


def get_workshop(workshop_id) -> (dict, int):
    workshop = WorkshopModel.find_by_id(workshop_id=workshop_id)

    # Check if given workshop_id exists in DB
    if workshop is None:
        raise EntityNotFoundError

    # Append action cards to field model
    action_cards = ActionCardModel.find_all()
    workshop.model.actionCards = action_cards

    # Append action card batches from creator to field model
    action_cards_batches = ActionCardBatchModel.find_action_card_batches_by_coach(
        coach_id=workshop.coachId
    )
    workshop.model.actionCardBatches = action_cards_batches

    return WorkshopDetailSchema().dump(workshop), 200


def get_workshops() -> (dict, int):
    # Get all workshop from a given coach
    workshops = WorkshopModel.objects()
    return WorkshopSchema(many=True).dump(workshops), 200


def create_workshop(data: bytes) -> (dict, int):
    schema = WorkshopSchema()
    data, err_msg, err_code = schema.loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    workshop = WorkshopModel(**data)
    # Append creator id
    workshop.creatorId = get_jwt_identity()
    # Append last created model id
    model = Model.find_last_created_model()
    workshop.model = model

    workshop.save()

    workshop.reload()
    return schema.dump(workshop), 200


def delete_workshop(workshop_id: str) -> (dict, int):
    workshop = WorkshopModel.find_by_id(workshop_id=workshop_id)

    # Check if given coach_id exists in DB
    if workshop is None:
        raise EntityNotFoundError
    # Delete user in DB
    workshop.delete()

    return {}, 204


def add_participant(workshop_id, user_data) -> (dict, int):
    workshop = WorkshopModel.find_by_id(workshop_id=workshop_id)
    user_data = UserSchema().loads(user_data)
    # Check if given workshop_id exists in DB
    if workshop is None:
        raise EntityNotFoundError
    user = UserModel.find_by_email(user_data.get("email"))
    participant = None
    if user is None:
        user = UserModel(
            email=user_data.get("email"),
            firstName=user_data.get("firstName"),
            lastName=user_data.get("lastName"),
            role=["participant"],
        )
        user.save()
        status = "created"
    else:
        status = "existing"
    user.reload()
    participant = WorkshopParticipants(user=user.userId, status=status)
    if workshop_id not in user.workshopParticipation:
        user.workshopParticipation.append(workshop_id)
        workshop.participants.append(participant)
    user.save()
    workshop.save()
    return get_workshop(workshop_id)


def remove_participant(workshop_id, participant_id) -> (dict, int):
    workshop = WorkshopModel.find_by_id(workshop_id=workshop_id)
    user = UserModel.find_by_id(participant_id)
    # Check if given workshop_id exists in DB
    if workshop is None or user is None:
        raise EntityNotFoundError
    updated_participants = []
    for participant in workshop.participants:
        if participant.user.userId != participant_id:
            updated_participants.append(participant)
    workshop.participants = updated_participants
    updated_workshop = []
    for registered in user.workshopParticipation:
        if registered != workshop_id:
            updated_workshop.append(registered)
    user.workshopParticipation = updated_workshop
    workshop.save()
    user.save()
    return get_workshop(workshop_id)
