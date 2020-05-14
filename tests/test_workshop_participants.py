import json

from app.common.errors import InvalidDataError
from app.models.user_model import Roles, UserModel
from app.models.workshop_model import WorkshopParticipantStatus


def test_add_participant_workshop(client, auth, coach, model, workshop, request):
    headers = auth.login(email="coach@test.com")

    data = {
        "email": "participant2@test.com",
        "firstName": "participant_first_name_2",
        "lastName": "participant_last_name_2",
    }

    previous_participants_count = len(workshop.participants)

    response = client.post(
        "/api/v1/workshops/{}/participants".format(workshop.workshopId),
        headers=headers,
        data=json.dumps(data),
    )

    workshop.reload()
    new_participant = UserModel.find_by_email(data.get("email"))

    status = {p.user.id: p.status for p in workshop.participants}[new_participant.id]

    assert response.status_code == 200
    assert len(workshop.participants) == previous_participants_count + 1
    assert workshop.id in new_participant.workshopParticipations
    assert new_participant.id in [p.user.id for p in workshop.participants]
    assert status == WorkshopParticipantStatus.CREATED.value

    def teardown():
        new_participant.delete()

    request.addfinalizer(teardown)


def test_add_coach_to_workshop(client, auth, coach, model, workshop):
    headers = auth.login(email=coach.email)
    data = {
        "email": coach.email,
        "firstName": coach.firstName,
        "lastName": coach.lastName,
    }

    response = client.post(
        "/api/v1/workshops/{}/participants".format(workshop.workshopId),
        headers=headers,
        data=json.dumps(data),
    )
    coach.reload()
    workshop.reload()

    status = {p.user.id: p.status for p in workshop.participants}[coach.id]

    assert response.status_code == 200
    assert Roles.PARTICIPANT.value in coach.role
    assert coach.id in [p.user.id for p in workshop.participants]
    assert workshop.id in coach.workshopParticipations
    assert status == WorkshopParticipantStatus.CREATED.value


def test_add_existing_participant(
    client, auth, coach, model, workshop, participant, workshops
):
    second_workshop = workshops[0]
    headers = auth.login(email=coach.email)
    data = {
        "email": participant.email,
        "firstName": participant.firstName,
        "lastName": participant.lastName,
    }

    response = client.post(
        "/api/v1/workshops/{}/participants".format(second_workshop.workshopId),
        headers=headers,
        data=json.dumps(data),
    )
    second_workshop.reload()
    participant.reload()

    status = {p.user.id: p.status for p in second_workshop.participants}[participant.id]

    assert response.status_code == 200
    assert participant.id in [p.user.id for p in second_workshop.participants]
    assert workshop.id in participant.workshopParticipations
    assert second_workshop.id in participant.workshopParticipations
    assert status == WorkshopParticipantStatus.EXISTING.value


def test_add_already_existing_participant_in_workshop(
    client, auth, coach, model, workshop, participant
):
    headers = auth.login(email="coach@test.com")

    data = {
        "email": participant.email,
        "firstName": participant.firstName,
        "lastName": participant.lastName,
    }

    response = client.post(
        "/api/v1/workshops/{}/participants".format(workshop.workshopId),
        headers=headers,
        data=json.dumps(data),
    )
    assert response.status_code == InvalidDataError.code
    assert "Participant already registered for this workshop" in str(response.data)
    assert UserModel.find_by_email("participant2@test.com") is None


def test_delete_participant_workshop(client, auth, coach, model, workshop, participant):
    headers = auth.login(email="coach@test.com")

    response = client.delete(
        "/api/v1/workshops/{}/participants/{}".format(
            workshop.workshopId, participant.userId
        ),
        headers=headers,
    )
    status_code = response.status_code

    workshop.reload()
    assert status_code == 204
    assert participant.userId not in [p.user.id for p in workshop.participants]
