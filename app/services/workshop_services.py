from datetime import datetime

from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app.common.errors import EntityNotFoundError, InvalidDataError
from app.models.carbon_forms_model import CarbonFormAnswersModel
from app.models.model_model import Model
from app.models.user_model import UserModel
from app.models.workshop_model import WorkshopModel
from app.schemas.workshop_schemas import WorkshopDetailSchema, WorkshopSchema


def get_workshop(workshop_id) -> (dict, int):
    workshop = WorkshopModel.find_by_id(workshop_id=workshop_id)

    # Check if given workshop_id exists in DB
    if workshop is None:
        raise EntityNotFoundError

    workshop.fetch_actions_cards()
    workshop.fetch_actions_card_batches()
    carbon_form_answers = CarbonFormAnswersModel.find_all_by_workshop_id(workshop_id)
    carbon_form_answers = {  # Convert into dict
        cfa.participant.pk: cfa.answers for cfa in carbon_form_answers
    }
    for wp in workshop.participants:
        if wp.user.id in carbon_form_answers:
            wp.surveyVariables = carbon_form_answers[wp.user.id]
    return WorkshopDetailSchema().dump(workshop), 200


def update_workshop(workshop_id: str, data: bytes) -> (dict, int):
    workshop = WorkshopModel.find_by_id(workshop_id=workshop_id)

    # Check if given workshop_id exists in DB
    if workshop is None:
        raise EntityNotFoundError

    # Deserialize data
    schema = WorkshopDetailSchema()
    workshop_data, err_msg, err_code = schema.loads_or_400(data)
    if err_msg:
        return err_msg, err_code
    try:
        schema.validate_partipant_id_in_rounds(
            workshop_data, participant_ids=workshop.get_participant_ids()
        )
    except ValidationError as e:
        raise InvalidDataError(details=e.messages)

    # Update rounds
    workshop.rounds = workshop_data.rounds

    workshop.updateAt = datetime.now()
    # Save to db
    workshop.save()
    workshop.reload()

    workshop.fetch_actions_cards()
    workshop.fetch_actions_card_batches()

    return WorkshopDetailSchema().dump(workshop), 200


def get_workshops() -> (dict, int):
    # Get all workshop from a given coach
    workshops = WorkshopModel.objects()
    return WorkshopSchema(many=True).dump(workshops), 200


def create_workshop(data: bytes) -> (dict, int):
    # Deserialize data
    schema = WorkshopSchema()
    data, err_msg, err_code = schema.loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    # Check existence of given coachId
    coach_id = data["coachId"]
    coach = UserModel.find_by_id(coach_id)
    if coach is None:
        raise InvalidDataError("Coach does not exist : {}".format(coach_id))

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
