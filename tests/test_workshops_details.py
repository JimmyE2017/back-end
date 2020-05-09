import json
from datetime import datetime

import pytest

from app.models.action_card_model import (
    ActionCardBatchModel,
    ActionCardCategory,
    ActionCardModel,
    ActionCardType,
)
from app.models.model_model import Model
from app.models.participant_model import ParticipantModel
from app.models.user_model import UserModel
from app.models.workshop_model import WorkshopModel


@pytest.fixture(scope="function")
def setup_data(init_coach, request):
    model = Model(
        footprintStructure={
            "cf1": "variable_1",
            "cf2": {"cf2_1": "variable_2", "cf2_2": "variable_3"},
        },
        globalCarbonVariables={
            "global_variable_1": 100,
            "global_variable_2": {"key1": 101, "key2": 102},
        },
        variableFormulas={
            "variable_1": {
                "+": [{"var": "global_variable_1"}, {"var": "survey_variable_1"}]
            },
            "variable_2": {
                "*": [
                    {
                        "var": {
                            "cat": ["global_variable_2.", {"var": "survey_variable_2"}]
                        }
                    },
                    {"var": "survey_variable_3"},
                ]
            },
            "variable_3": {
                "*": [
                    {
                        "var": {
                            "cat": ["global_variable_2.", {"var": "survey_variable_2"}]
                        }
                    },
                    0.5,
                ]
            },
        },
    )

    model.save()

    action_card1 = ActionCardModel(
        number=1,
        title="action_card_title_1",
        category=ActionCardCategory.AWARENESS.value,
        type=ActionCardType.INDIVIDUAL.value,
        key="action_card_key_1",
        sector="action_card_sector_1",
        cost=1,
    )

    action_card2 = ActionCardModel(
        number=2,
        title="action_card_title_2",
        category=ActionCardCategory.ECOFRIENDLY_ACTION.value,
        type=ActionCardType.INDIVIDUAL.value,
        key="action_card_key_2",
        sector="action_card_sector_2",
        cost=2,
    )
    action_card3 = ActionCardModel(
        number=3,
        title="action_card_title_3",
        category=ActionCardCategory.SYSTEM.value,
        type=ActionCardType.COLLECTIVE.value,
        key="action_card_key_3",
        sector="action_card_sector_3",
        cost=3,
    )

    action_card1.save()
    action_card2.save()
    action_card3.save()
    action_cards = [action_card1, action_card2, action_card3]

    action_card_batch1 = ActionCardBatchModel(
        coachId=init_coach.id,
        number=1,
        title="action_card_batch_title_1",
        type=ActionCardType.INDIVIDUAL.value,
        actionCardIds=[action_card1.id, action_card2.id],
    )

    action_card_batch2 = ActionCardBatchModel(
        coachId=init_coach.id,
        number=2,
        title="action_card_batch_title_2",
        type=ActionCardType.COLLECTIVE.value,
        actionCardIds=[action_card3.id],
    )
    action_card_batch1.save()
    action_card_batch2.save()

    action_card_batches = [action_card_batch1, action_card_batch2]

    user = UserModel(
        email="schwarzy@gmail.com",
        firstName="Arnold",
        lastName="Schwarzy",
        role=["participant"],
    )
    user.save()
    user.reload()
    user_to_add = {
        "email": "trumpy@gmail.com",
        "firstName": "Donald",
        "lastName": "Trump",
    }
    participant = ParticipantModel(user=user.userId, status="created")

    workshop = WorkshopModel(
        title="workshop_title_1",
        startAt=datetime(2020, 1, 1, 1, 1, 1),
        city="city_1",
        address="address1",
        eventUrl="http://www.example1.com",
        coachId=init_coach.id,
        creatorId=init_coach.id,
        model=model,
        participants=[participant],
    )

    workshop.save()

    def teardown():
        model.delete()
        action_card1.delete()
        action_card2.delete()
        action_card3.delete()
        action_card_batch1.delete()
        action_card_batch2.delete()
        workshop.delete()
        user.delete()

    request.addfinalizer(teardown)

    return workshop, model, action_cards, action_card_batches, user, user_to_add


def test_get_workshop(client, auth, init_coach, setup_data):
    workshop, model, action_cards, action_card_batches, user, user_to_add = setup_data
    headers = auth.login(email="coach@test.com")

    response = client.get("/api/v1/workshops/{}".format(workshop.id), headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code
    print(response_data)
    expected_output = {
        "title": workshop.title,
        "startAt": workshop.startAt.isoformat(),
        "city": workshop.city,
        "address": workshop.address,
        "eventUrl": workshop.eventUrl,
        "coachId": workshop.coachId,
        "creatorId": workshop.creatorId,
        "workshopId": workshop.id,
        "participants": [
            {
                "status": "created",
                "email": user.email,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "userId": user.userId,
            }
        ],
        "model": {
            "id": model.id,
            "globalCarbonVariables": model.globalCarbonVariables,
            "variableFormulas": model.variableFormulas,
            "footprintStructure": model.footprintStructure,
            "actionCards": [
                {
                    "actionCardId": action_card.actionCardId,
                    "number": action_card.number,
                    "title": action_card.title,
                    "category": action_card.category,
                    "type": action_card.type,
                    "key": action_card.key,
                    "sector": action_card.sector,
                    "cost": action_card.cost,
                }
                for action_card in action_cards
            ],
            "actionCardBatches": [
                {
                    "actionCardBatchId": action_card_batch.actionCardBatchId,
                    "number": action_card_batch.number,
                    "title": action_card_batch.title,
                    "type": action_card_batch.type,
                    "actionCardIds": action_card_batch.actionCardIds,
                }
                for action_card_batch in action_card_batches
            ],
        },
    }
    assert status_code == 200
    assert response_data == expected_output


def test_add_participant_workshop(client, auth, init_coach, setup_data, request):
    workshop, model, action_cards, action_card_batches, user, user_to_add = setup_data
    headers = auth.login(email="coach@test.com")

    response = client.post(
        "/api/v1/workshops/{}/participants".format(workshop.workshopId),
        headers=headers,
        data=json.dumps(user_to_add),
    )
    status_code = response.status_code

    workshop.reload()
    new_user = UserModel.find_by_email(user_to_add.get("email"))
    assert status_code == 200
    assert len(workshop.participants) == 2
    assert new_user is not None

    def teardown():
        new_user.delete()

    request.addfinalizer(teardown)


def test_delete_participant_workshop(client, auth, init_coach, setup_data, request):
    workshop, model, action_cards, action_card_batches, user, user_to_add = setup_data
    headers = auth.login(email="coach@test.com")

    response = client.delete(
        "/api/v1/workshops/{}/participants/{}".format(workshop.workshopId, user.userId),
        headers=headers,
    )
    status_code = response.status_code

    workshop.reload()
    assert status_code == 200
    assert len(workshop.participants) == 0
