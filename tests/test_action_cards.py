import json

import pytest

from app.models.action_card_model import (
    ActionCardBatchModel,
    ActionCardCategory,
    ActionCardModel,
    ActionCardType,
)
from app.models.city_model import Cities
from app.models.user_model import Roles, UserModel


@pytest.fixture(scope="class")
def create_some_action_cards(db, request):
    action_card1 = ActionCardModel(
        cardNumber=1,
        name="action_card_name_1",
        category=ActionCardCategory.AWARENESS.value,
        type=ActionCardType.INDIVIDUAL.value,
        key="action_card_key_1",
        sector="action_card_sector_1",
        cost=1,
    )

    action_card2 = ActionCardModel(
        cardNumber=2,
        name="action_card_name_2",
        category=ActionCardCategory.ECOFRIENDLY_ACTION.value,
        type=ActionCardType.INDIVIDUAL.value,
        key="action_card_key_2",
        sector="action_card_sector_2",
        cost=2,
    )
    action_card3 = ActionCardModel(
        cardNumber=3,
        name="action_card_name_3",
        category=ActionCardCategory.SYSTEM.value,
        type=ActionCardType.COLLECTIVE.value,
        key="action_card_key_3",
        sector="action_card_sector_3",
        cost=3,
    )

    action_card1.save()
    action_card2.save()
    action_card3.save()

    def teardown():
        action_card1.delete()
        action_card2.delete()
        action_card3.delete()

    request.cls.action_cards = [action_card1, action_card2, action_card3]
    request.addfinalizer(teardown)

    return


@pytest.fixture(scope="function")
def create_some_action_card_batches(init_coach, request):
    # Coach's batch
    action_card_batch1 = ActionCardBatchModel(
        coachId=init_coach.id,
        name="action_card_batch_name_1",
        type=ActionCardType.INDIVIDUAL.value,
        actionCardIds=["1", "2"],
    )

    action_card_batch2 = ActionCardBatchModel(
        coachId=init_coach.id,
        name="action_card_batch_name_2",
        type=ActionCardType.COLLECTIVE.value,
        actionCardIds=["1", "3"],
    )
    # Default batches
    action_card_batch3 = ActionCardBatchModel(
        default=True,
        name="action_card_batch_name_3",
        type=ActionCardType.INDIVIDUAL.value,
        actionCardIds=["1", "2"],
    )

    action_card_batch4 = ActionCardBatchModel(
        default=True,
        name="action_card_batch_name_4",
        type=ActionCardType.COLLECTIVE.value,
        actionCardIds=["1", "3"],
    )
    action_card_batch1.save()
    action_card_batch2.save()
    action_card_batch3.save()
    action_card_batch4.save()

    def teardown():
        action_card_batch1.delete()
        action_card_batch2.delete()
        action_card_batch3.delete()
        action_card_batch4.delete()

    request.addfinalizer(teardown)

    return [
        action_card_batch1,
        action_card_batch2,
        action_card_batch3,
        action_card_batch4,
    ]


@pytest.mark.usefixtures("create_some_action_cards")
class TestActionCardsRessourcesWithExistingData:
    def test_get_action_cards(self, client, auth, init_coach):

        headers = auth.login(email=init_coach.email)

        response = client.get("/api/v1/action_cards", headers=headers)
        response_data, status_code = json.loads(response.data), response.status_code

        expected_first_result = {
            "id": self.action_cards[0].actionCardId,
            "cardNumber": self.action_cards[0].cardNumber,
            "name": self.action_cards[0].name,
            "category": self.action_cards[0].category,
            "type": self.action_cards[0].type,
            "key": self.action_cards[0].key,
            "sector": self.action_cards[0].sector,
            "cost": self.action_cards[0].cost,
        }

        assert status_code == 200
        assert len(response_data) == 3
        assert response_data[0] == expected_first_result

    def test_get_action_card_batches(
        self, client, auth, init_coach, create_some_action_card_batches
    ):
        headers = auth.login(email=init_coach.email)

        response = client.get(
            "/api/v1/coaches/{}/action_card_batches".format(init_coach.id),
            headers=headers,
        )
        response_data, status_code = json.loads(response.data), response.status_code
        action_card_batches = create_some_action_card_batches
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
        self, client, auth, init_coach, create_some_action_card_batches
    ):
        action_card1, action_card2, action_card3 = (
            self.action_cards[0],
            self.action_cards[1],
            self.action_cards[2],
        )
        headers = auth.login(email=init_coach.email)

        data = [
            {
                "name": "action_card_batch_name_1",
                "type": ActionCardType.INDIVIDUAL.value,
                "actionCardIds": [action_card1.id, action_card2.id],
            },
            {
                "id": create_some_action_card_batches[0].actionCardBatchId,
                "name": "action_card_batch_name_2_bis",
                "type": ActionCardType.COLLECTIVE.value,
                "actionCardIds": [action_card3.id],
            },
        ]

        response = client.put(
            "/api/v1/coaches/{}/action_card_batches".format(init_coach.id),
            headers=headers,
            data=json.dumps(data),
        )
        response_data, status_code = json.loads(response.data), response.status_code

        assert status_code == 200
        assert "id" in response_data[0]
        assert (
            len(
                ActionCardBatchModel.find_action_card_batches_by_coach(
                    coach_id=init_coach.id
                )
            )
            == 2
        )

    def test_put_action_card_batches_incorrect_action_card_ids(
        self, client, auth, init_coach
    ):
        headers = auth.login(email=init_coach.email)
        action_card2, action_card3 = self.action_cards[1], self.action_cards[2]
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
            "/api/v1/coaches/{}/action_card_batches".format(init_coach.id),
            headers=headers,
            data=json.dumps(data),
        )
        response_text, status_code = str(response.data), response.status_code

        assert status_code == 400
        assert f"actionCardId {incorrect_id} does not exist" in response_text
        assert (
            len(
                ActionCardBatchModel.find_action_card_batches_by_coach(
                    coach_id=init_coach.id
                )
            )
            == 0
        )

    def test_put_action_card_batches_missing_action_card_ids(
        self, client, auth, init_coach
    ):
        headers = auth.login(email=init_coach.email)
        action_card1, action_card2, action_card3 = (
            self.action_cards[0],
            self.action_cards[1],
            self.action_cards[2],
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
            "/api/v1/coaches/{}/action_card_batches".format(init_coach.id),
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
            len(
                ActionCardBatchModel.find_action_card_batches_by_coach(
                    coach_id=init_coach.id
                )
            )
            == 0
        )

    def test_put_action_card_batches_invalid_action_card_mix(
        self, client, auth, init_coach
    ):
        headers = auth.login(email=init_coach.email)
        action_card1, action_card2, action_card3 = (
            self.action_cards[0],
            self.action_cards[1],
            self.action_cards[2],
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
            "/api/v1/coaches/{}/action_card_batches".format(init_coach.id),
            headers=headers,
            data=json.dumps(data),
        )
        response_text, status_code = str(response.data), response.status_code

        assert status_code == 400
        assert (
            f"Action cards within the same batch must be of the same type."
            in response_text
        )
        assert (
            len(
                ActionCardBatchModel.find_action_card_batches_by_coach(
                    coach_id=init_coach.id
                )
            )
            == 0
        )

    def test_default_batches_at_coach_creation(
        self, client, auth, init_admin, create_some_action_card_batches, request
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

        response = client.post(
            "/api/v1/coaches", headers=headers, data=json.dumps(data)
        )
        coach_id = json.loads(response.data)["id"]

        action_card_batches = ActionCardBatchModel.find_action_card_batches_by_coach(
            coach_id
        )
        assert len(action_card_batches) == 2
        assert create_some_action_card_batches[2].name == action_card_batches[0].name

        def teardown():
            UserModel.find_coach_by_id(coach_id).delete()

        request.addfinalizer(teardown)
