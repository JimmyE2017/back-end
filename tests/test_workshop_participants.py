import json

from app.models.user_model import UserModel


def test_add_participant_workshop(client, auth, coach, model, workshop, request):
    headers = auth.login(email="coach@test.com")

    data = {
        "email": "participant2@test.com",
        "firstName": "participant_first_name_2",
        "lastName": "participant_last_name_2",
    }

    response = client.post(
        "/api/v1/workshops/{}/participants".format(workshop.workshopId),
        headers=headers,
        data=json.dumps(data),
    )
    status_code = response.status_code

    workshop.reload()
    new_participant = UserModel.find_by_email(data.get("email"))
    assert status_code == 200
    assert len(workshop.participants) == 2
    assert new_participant is not None

    def teardown():
        new_participant.delete()

    request.addfinalizer(teardown)


def test_delete_participant_workshop(
    client, auth, coach, model, workshop, participant, request
):
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
