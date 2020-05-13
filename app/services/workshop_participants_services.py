from app.common.errors import EntityNotFoundError, InvalidDataError
from app.models.user_model import Roles, UserModel
from app.models.workshop_model import (
    WorkshopModel,
    WorkshopParticipantModel,
    WorkshopParticipantStatus,
)
from app.schemas.user_schemas import ParticipantSchema


def add_participant(workshop_id, data) -> (dict, int):
    workshop = WorkshopModel.find_by_id(workshop_id=workshop_id)
    # Check if given workshop_id exists in DB
    if workshop is None:
        raise EntityNotFoundError

    # Deserialize data
    schema = ParticipantSchema()
    data, err_msg, err_code = schema.loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    # Check if there is already a participant with this email in DB
    user = UserModel.find_by_email(data.get("email"))
    if user is None:
        participant = UserModel(
            email=data.get("email"),
            firstName=data.get("firstName"),
            lastName=data.get("lastName"),
            role=[Roles.PARTICIPANT.value],
            workshopParticipations=[workshop_id],
        )

        status = WorkshopParticipantStatus.CREATED.value
    else:
        # If user already exists, check if it's a participant
        if Roles.PARTICIPANT.value in user.role:
            # Raise error if participant already registred in workshop
            if user.userId in [p.user.id for p in workshop.participants]:
                raise InvalidDataError(
                    msg="Participant already registered for this workshop"
                )
            status = WorkshopParticipantStatus.EXISTING.value
        else:
            # add participant role otherwise
            user.add_participant_role()
            status = WorkshopParticipantStatus.CREATED.value

        participant = user
        participant.workshopParticipations.append(workshop_id)

    # Append participant to workshop
    workshop.participants.append(
        WorkshopParticipantModel(user=participant.userId, status=status)
    )

    # Persist in DB
    participant.save()
    workshop.save()

    return schema.dump(participant), 200


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
    for registered in user.workshopParticipations:
        if registered != workshop_id:
            updated_workshop.append(registered)
    user.workshopParticipations = updated_workshop
    workshop.save()
    user.save()
    return None, 204
