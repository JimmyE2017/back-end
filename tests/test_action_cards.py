import json

from app.models.action_card_model import ActionCardBatchModel, ActionCardType
from app.models.city_model import Cities
from app.models.user_model import Roles, UserModel


def test_get_action_cards(client, auth, coach, action_cards):
    headers = auth.login(email=coach.email)

    response = client.get("/api/v1/action_cards", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    expected_first_result = {
        "id": action_cards[0].actionCardId,
        "cardNumber": action_cards[0].cardNumber,
        "name": action_cards[0].name,
        "category": action_cards[0].category,
        "type": action_cards[0].type,
        "key": action_cards[0].key,
        "sector": action_cards[0].sector,
        "cost": action_cards[0].cost,
        "impactType": action_cards[0].impactType,
        "operations": [
            {"variable": op.variable, "operation": op.operation}
            for op in action_cards[0].operations
        ],
    }

    assert status_code == 200
    assert len(response_data) == 3
    assert response_data[0] == expected_first_result


def test_get_action_card_batches(client, auth, coach, action_card_batches):
    headers = auth.login(email=coach.email)

    response = client.get(
        "/api/v1/coaches/{}/action_card_batches".format(coach.id), headers=headers,
    )
    response_data, status_code = json.loads(response.data), response.status_code
    action_card_batches = action_card_batches
    expected_first_result = {
        "id": action_card_batches[0].actionCardBatchId,
        "name": action_card_batches[0].name,
        "type": action_card_batches[0].type,
        "actionCardIds": action_card_batches[0].actionCardIds,
    }

    assert status_code == 200
    assert len(response_data) == 2
    assert response_data[0] == expected_first_result


def test_put_action_card_batches_success(
    client, auth, coach, action_cards, action_card_batches
):
    action_card1, action_card2, action_card3 = (
        action_cards[0],
        action_cards[1],
        action_cards[2],
    )
    headers = auth.login(email=coach.email)

    data = [
        {
            "name": "action_card_batch_name_1",
            "type": ActionCardType.INDIVIDUAL.value,
            "actionCardIds": [action_card1.id, action_card2.id],
        },
        {
            "id": action_card_batches[0].actionCardBatchId,
            "name": "action_card_batch_name_2_bis",
            "type": ActionCardType.COLLECTIVE.value,
            "actionCardIds": [action_card3.id],
        },
    ]

    response = client.put(
        "/api/v1/coaches/{}/action_card_batches".format(coach.id),
        headers=headers,
        data=json.dumps(data),
    )
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == 200
    assert "id" in response_data[0]
    assert (
        len(ActionCardBatchModel.find_action_card_batches_by_coach(coach_id=coach.id))
        == 2
    )


def test_put_action_card_batches_incorrect_action_card_ids(
    client, auth, coach, action_cards
):
    headers = auth.login(email=coach.email)
    action_card2, action_card3 = action_cards[1], action_cards[2]
    incorrect_id = "incorrect_id"
    data = [
        {
            "name": "action_card_batch_name_1",
            "type": ActionCardType.INDIVIDUAL.value,
            "actionCardIds": [incorrect_id, action_card2.id],
        },
        {
            "name": "action_card_batch_name_2",
            "type": ActionCardType.COLLECTIVE.value,
            "actionCardIds": [action_card3.id],
        },
    ]

    response = client.put(
        "/api/v1/coaches/{}/action_card_batches".format(coach.id),
        headers=headers,
        data=json.dumps(data),
    )
    response_text, status_code = str(response.data), response.status_code

    assert status_code == 400
    assert f"actionCardId {incorrect_id} does not exist" in response_text
    assert (
        len(ActionCardBatchModel.find_action_card_batches_by_coach(coach_id=coach.id))
        == 0
    )


def test_put_action_card_batches_missing_action_card_ids(
    client, auth, coach, action_cards
):
    headers = auth.login(email=coach.email)
    action_card1, action_card2, action_card3 = (
        action_cards[0],
        action_cards[1],
        action_cards[2],
    )
    data = [
        {
            "name": "action_card_batch_name_1",
            "type": ActionCardType.INDIVIDUAL.value,
            "actionCardIds": [action_card2.id],
        },
        {
            "name": "action_card_batch_name_2",
            "type": ActionCardType.COLLECTIVE.value,
            "actionCardIds": [action_card3.id],
        },
    ]

    response = client.put(
        "/api/v1/coaches/{}/action_card_batches".format(coach.id),
        headers=headers,
        data=json.dumps(data),
    )
    response_text, status_code = str(response.data), response.status_code

    assert status_code == 400
    assert (
        f"All actions cards need to be present. Missing {action_card1.id}"
        in response_text
    )
    assert (
        len(ActionCardBatchModel.find_action_card_batches_by_coach(coach_id=coach.id))
        == 0
    )


def test_put_action_card_batches_invalid_action_card_mix(
    client, auth, coach, action_cards
):
    headers = auth.login(email=coach.email)
    action_card1, action_card2, action_card3 = (
        action_cards[0],
        action_cards[1],
        action_cards[2],
    )
    data = [
        {
            "name": "action_card_batch_name_1",
            "type": ActionCardType.INDIVIDUAL.value,
            "actionCardIds": [action_card3.id, action_card2.id],
        },
        {
            "name": "action_card_batch_name_2",
            "type": ActionCardType.COLLECTIVE.value,
            "actionCardIds": [action_card1.id],
        },
    ]

    response = client.put(
        "/api/v1/coaches/{}/action_card_batches".format(coach.id),
        headers=headers,
        data=json.dumps(data),
    )
    response_text, status_code = str(response.data), response.status_code

    assert status_code == 400
    assert (
        f"Action cards within the same batch must be of the same type." in response_text
    )
    assert (
        len(ActionCardBatchModel.find_action_card_batches_by_coach(coach_id=coach.id))
        == 0
    )


def test_default_batches_at_coach_creation(
    client, auth, admin, default_action_card_batches, request
):
    headers = auth.login(email="admin@test.com")
    data = dict(
        firstName="firstName",
        lastName="lastName",
        email="coach20@test.com",
        password="password",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    )

    response = client.post("/api/v1/coaches", headers=headers, data=json.dumps(data))
    coach_id = json.loads(response.data)["id"]

    coach_action_card_batches = ActionCardBatchModel.find_action_card_batches_by_coach(
        coach_id
    )
    assert len(coach_action_card_batches) == 2
    assert coach_action_card_batches[0].name == default_action_card_batches[0].name

    def teardown():
        UserModel.find_coach_by_id(coach_id).delete()

    request.addfinalizer(teardown)
