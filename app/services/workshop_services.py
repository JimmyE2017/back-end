from flask_jwt_extended import get_jwt_identity

from app.common.errors import EntityNotFoundError
from app.models.action_card_model import ActionCardBatchModel, ActionCardModel
from app.models.model_model import Model
from app.models.workshop_model import WorkshopModel
from app.schemas.workshop_schemas import WorkshopDetailSchema, WorkshopSchema


def get_workshop(workshop_id) -> (dict, int):
    workshop = WorkshopModel.find_by_id(workshop_id=workshop_id)

    # Check if given workshop_id exists in DB
    if workshop is None:
        raise EntityNotFoundError

    # Append data from model
    model = Model.find_by_id(model_id=workshop.modelId)
    workshop.model = model

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
    workshop.modelId = model.id

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
