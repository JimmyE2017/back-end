from app.common.errors import EntityNotFoundError, InvalidDataError
from app.models.carbon_forms_model import CarbonFormAnswersModel
from app.models.user_model import UserModel
from app.models.workshop_model import WorkshopModel, WorkshopParticipantStatus
from app.schemas.carbon_forms_schemas import CarbonFormAnswersSchema


def create_carbon_form_answers(workshop_id: str, data: bytes) -> (dict, int):
    # Check existence of given workshop id
    workshop = WorkshopModel.find_by_id(workshop_id)
    if workshop is None:
        raise EntityNotFoundError

    # Deserialize data
    schema = CarbonFormAnswersSchema()
    data, err_msg, err_code = schema.loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    # Check existence of given email and make sure it belongs to one of
    # the workshop's participants
    user = UserModel.find_participant_by_email(data["email"])
    if user is None or user.id not in workshop.get_participant_ids():
        raise InvalidDataError(
            "This email does not belong to one of the workshop's participants"
        )

    # Check if participant has already answered the carbon form or not
    if (
        CarbonFormAnswersModel.find_by_workshop_id_and_participant_id(
            workshop_id, user.id
        )
        is not None
    ):
        raise InvalidDataError(
            "Participant has already answered to the carbon form for this workshop"
        )

    # Update participant status
    wp = workshop.get_workshop_participant(participant_id=user.id)
    wp.status = WorkshopParticipantStatus.TOCHECK.value

    # Save data
    carbon_form_answers = CarbonFormAnswersModel(
        workshop=workshop.id, participant=user.id, answers=data["answers"],
    )
    carbon_form_answers.save()
    workshop.save()

    carbon_form_answers.reload()
    return schema.dump(carbon_form_answers), 200
