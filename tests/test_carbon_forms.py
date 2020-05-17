import json

from app.common.errors import EntityNotFoundError, InvalidDataError
from app.models.carbon_forms_model import CarbonFormAnswersModel
from app.models.workshop_model import WorkshopParticipantStatus


def test_post_carbon_form_answers(client, workshop, participant):
    count = len(CarbonFormAnswersModel.objects)

    data = {
        "email": participant.email,
        "answers": {"meat_per_day": 9000, "car_type": "futuristic"},
    }
    response = client.post(
        "/api/v1/carbon_forms/{}".format(workshop.workshopId), data=json.dumps(data),
    )

    response_data, status_code = json.loads(response.data), response.status_code

    expected_result = {
        "id": response_data["id"],  # yeah too lazy to fetch the id
        "workshopId": workshop.id,
        "participantId": participant.id,
        "answers": {"meat_per_day": 9000, "car_type": "futuristic"},
    }

    workshop.reload()

    assert status_code == 200
    assert len(CarbonFormAnswersModel.objects) == count + 1
    assert response_data == expected_result
    assert workshop.participants[0].status == WorkshopParticipantStatus.TOCHECK.value


def test_post_carbon_form_answers_inexisting_workshop(client):
    data = {
        "email": "email@test.com",
        "answers": {"meat_per_day": 9000, "car_type": "futuristic"},
    }
    response = client.post(
        "/api/v1/carbon_forms/{}".format("inexistingId"), data=json.dumps(data),
    )

    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == EntityNotFoundError.code
    assert response_data == EntityNotFoundError().get_content()


def test_post_carbon_form_answers_non_existing_participant(client, workshop):
    data = {
        "email": "email@test.com",
        "answers": {"meat_per_day": 9000, "car_type": "futuristic"},
    }
    response = client.post(
        "/api/v1/carbon_forms/{}".format(workshop.id), data=json.dumps(data),
    )

    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == InvalidDataError.code
    assert "This email does not belong to one of the workshop's participants" in str(
        response_data
    )


def test_post_carbon_form_answers_participant_not_in_workshop(
    client, workshop, participant, workshops
):
    data = {
        "email": participant.email,
        "answers": {"meat_per_day": 9000, "car_type": "futuristic"},
    }
    response = client.post(
        "/api/v1/carbon_forms/{}".format(workshops[0].id), data=json.dumps(data),
    )

    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == InvalidDataError.code
    assert "This email does not belong to one of the workshop's participants" in str(
        response_data
    )


def test_post_carbon_form_answers_already_existing(
    client, workshop, participant, carbon_form_answers
):
    data = {
        "email": participant.email,
        "answers": {"meat_per_day": 9000, "car_type": "futuristic"},
    }
    response = client.post(
        "/api/v1/carbon_forms/{}".format(workshop.id), data=json.dumps(data),
    )

    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == InvalidDataError.code
    assert (
        "Participant has already answered to the carbon form for this workshop"
        in str(response_data)
    )
