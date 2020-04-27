import json

import pytest

from app.models.action_card_model import ActionCardModel


@pytest.fixture(scope="class")
def create_some_action_cards(db, request):
    action_card1 = ActionCardModel(
        number=1,
        title="action_card_title_1",
        category="action_card_category_1",
        type="action_card_type_1",
        key="action_card_key_1",
        sector="action_card_sector_1",
        cost=1,
    )

    action_card2 = ActionCardModel(
        number=2,
        title="action_card_title_2",
        category="action_card_category_2",
        type="action_card_type_2",
        key="action_card_key_2",
        sector="action_card_sector_2",
        cost=2,
    )
    action_card3 = ActionCardModel(
        number=3,
        title="action_card_title_3",
        category="action_card_category_3",
        type="action_card_type_3",
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


@pytest.mark.usefixtures("create_some_action_cards")
class TestActionCardsRessourcesWithExistingData:
    def test_get_action_cards(self, client, auth, init_coach):

        headers = auth.login(email="coach@test.com")

        response = client.get(
            "/api/v1/action_cards".format(init_coach.id), headers=headers
        )
        response_data, status_code = json.loads(response.data), response.status_code

        expected_first_result = {
            "actionCardId": self.action_cards[0].actionCardId,
            "number": self.action_cards[0].number,
            "title": self.action_cards[0].title,
            "category": self.action_cards[0].category,
            "type": self.action_cards[0].type,
            "key": self.action_cards[0].key,
            "sector": self.action_cards[0].sector,
            "cost": self.action_cards[0].cost,
        }

        assert status_code == 200
        assert len(response_data) == 3
        assert response_data[0] == expected_first_result
