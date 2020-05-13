import json
from datetime import datetime, timedelta

import pytest
from mongoengine import get_db
from werkzeug.security import generate_password_hash

from app import create_app
from app.common.mail import mail as _mail
from app.models import db as _db
from app.models.action_card_model import (
    ActionCardBatchModel,
    ActionCardCategory,
    ActionCardModel,
    ActionCardType,
)
from app.models.city_model import Cities
from app.models.model_model import Model
from app.models.user_model import Roles, UserModel
from app.models.workshop_model import WorkshopModel, WorkshopParticipantModel


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test `Flask` application."""
    app = create_app("test")

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope="session")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="session")
def cli_runner(app):
    """A test cli runner for the app."""
    return app.test_cli_runner()


@pytest.fixture(scope="session")
def db(app, request):
    """Session-wide test database."""
    _db.app = app

    # Add init DB here

    def teardown():
        me = get_db()
        db_name = "test"
        for collection in me.client.get_database(db_name).list_collection_names():
            me.client.get_database(db_name).drop_collection(collection)

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope="session")
def mail(app):
    """A test client for the app."""
    _mail.app = app
    return _mail


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email="admin@test.com", password="password"):
        response = self._client.post(
            "/api/v1/login", data=json.dumps({"email": email, "password": password})
        )
        access_token = json.loads(response.data)["access_token"]
        return {"Authorization": f"Bearer {access_token}"}

    def logout(self, headers):
        return self._client.delete("/api/v1/logout", headers=headers)


@pytest.fixture(scope="function")
def auth(client):
    """
    To use in order to have a authenticated access while testing.
    If you use this fixture, don't forget to also init an user
    :param client:
    :return:
    """
    return AuthActions(client)


# ------- DATA ---------


@pytest.fixture(scope="function")
def admin(db, request):
    """
    Create an admin for the scope of a function
    Remove it at the end
    """
    admin = UserModel(
        firstName="admin_first_name",
        lastName="admin_last_name",
        email="admin@test.com",
        password=generate_password_hash("password"),
        role=[Roles.ADMIN.value, Roles.COACH.value],
        city=Cities.PARIS.value,
    )

    admin.save()

    # Delete admin at the end
    def teardown():
        admin.delete()

    request.addfinalizer(teardown)
    return admin


@pytest.fixture(scope="function")
def coach(db, request):
    coach = UserModel(
        firstName="coach_first_name",
        lastName="coach_last_name",
        email="coach@test.com",
        password=generate_password_hash("password"),
        role=[Roles.COACH.value],
        city=Cities.PARIS.value,
    )

    coach.save()

    # Delete coach at the end
    def teardown():
        coach.delete()

    request.addfinalizer(teardown)
    return coach


@pytest.fixture(scope="function")
def participant(db, request):
    participant = UserModel(
        email="participant1@test.com",
        firstName="participant_first_name_1",
        lastName="participant_last_name_1",
        role=[Roles.PARTICIPANT.value],
    )

    participant.save()

    # Delete participant at the end
    def teardown():
        participant.delete()

    request.addfinalizer(teardown)
    return participant


@pytest.fixture(scope="function")
def coaches(db, request):
    coach1 = UserModel(
        firstName="firstName1",
        lastName="lastName1",
        email="coach1@test.com",
        password="password1",
        role=[Roles.COACH.value],
        city=Cities.PARIS.value,
    )

    coach2 = UserModel(
        firstName="firstName2",
        lastName="lastName2",
        email="coach2@test.com",
        password="password2",
        role=[Roles.COACH.value],
        city=Cities.PARIS.value,
    )

    coach3 = UserModel(
        firstName="firstName3",
        lastName="lastName3",
        email="coach3@test.com",
        password="password3",
        role=[Roles.COACH.value],
        city=Cities.PARIS.value,
    )

    coach1.save()
    coach2.save()
    coach3.save()

    def teardown():
        coach1.delete()
        coach2.delete()
        coach3.delete()

    request.addfinalizer(teardown)
    return [coach1, coach2, coach3]


@pytest.fixture(scope="function")
def action_cards(db, request):
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

    request.addfinalizer(teardown)

    return [action_card1, action_card2, action_card3]


@pytest.fixture(scope="function")
def default_action_card_batches(action_cards, request):
    action_card_batch1 = ActionCardBatchModel(
        default=True,
        name="action_card_batch_name_1",
        type=ActionCardType.INDIVIDUAL.value,
        actionCardIds=["1", "2"],
    )

    action_card_batch2 = ActionCardBatchModel(
        default=True,
        name="action_card_batch_name_2",
        type=ActionCardType.COLLECTIVE.value,
        actionCardIds=["1", "3"],
    )
    action_card_batch1.save()
    action_card_batch2.save()

    def teardown():
        action_card_batch1.delete()
        action_card_batch2.delete()

    request.addfinalizer(teardown)

    return [
        action_card_batch1,
        action_card_batch2,
    ]


@pytest.fixture(scope="function")
def action_card_batches(action_cards, coach, request):
    # Coach's batch
    action_card_batch1 = ActionCardBatchModel(
        coachId=coach.id,
        name="action_card_batch_name_1",
        type=ActionCardType.INDIVIDUAL.value,
        actionCardIds=["1", "2"],
    )

    action_card_batch2 = ActionCardBatchModel(
        coachId=coach.id,
        name="action_card_batch_name_2",
        type=ActionCardType.COLLECTIVE.value,
        actionCardIds=["1", "3"],
    )
    action_card_batch1.save()
    action_card_batch2.save()

    def teardown():
        action_card_batch1.delete()
        action_card_batch2.delete()

    request.addfinalizer(teardown)

    return [
        action_card_batch1,
        action_card_batch2,
    ]


@pytest.fixture(scope="function")
def model(db, request):
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

    def teardown():
        model.delete()

    request.addfinalizer(teardown)
    return model


@pytest.fixture(scope="function")
def models(db, request):
    model1 = Model(
        footprintStructure={"var1": "var1"},
        globalCarbonVariables={"var1": "var1"},
        variableFormulas={"var1": "var1"},
        createdAt=datetime.utcnow(),
    )

    model2 = Model(
        footprintStructure={"var1": "var1"},
        globalCarbonVariables={"var1": "var1"},
        variableFormulas={"var1": "var1"},
        createdAt=datetime.utcnow() + timedelta(days=1),
    )

    model1.save()
    model2.save()

    def teardown():
        model1.delete()
        model2.delete()

    request.addfinalizer(teardown)
    return [model1, model2]


@pytest.fixture(scope="function")
def workshop(db, coach, model, participant, request):
    workshop_participant = WorkshopParticipantModel(user=participant, status="created")

    workshop = WorkshopModel(
        name="workshop_name_1",
        startAt=datetime(2020, 1, 1, 1, 1, 1),
        city="city_1",
        address="address1",
        eventUrl="http://www.example1.com",
        coachId=coach.id,
        creatorId=coach.id,
        model=model,
        participants=[workshop_participant],
    )
    workshop.save()

    def teardown():
        workshop.delete()

    request.addfinalizer(teardown)
    return workshop


@pytest.fixture(scope="function")
def workshops(db, request, coach):
    workshop1 = WorkshopModel(
        name="workshop_name_1",
        startAt=datetime(2020, 1, 1, 1, 1, 1),
        city="city_1",
        address="address1",
        eventUrl="http://www.example1.com",
        coachId=coach.id,
        creatorId=coach.id,
        model=None,
    )
    workshop2 = WorkshopModel(
        name="workshop_name_2",
        startAt=datetime(2020, 2, 2, 2, 2, 2),
        city="city_2",
        address="address2",
        eventUrl="http://www.example2.com",
        coachId=coach.id,
        creatorId=coach.id,
        model=None,
    )

    workshop1.save()
    workshop2.save()

    def teardown():
        workshop1.delete()
        workshop2.delete()

    request.addfinalizer(teardown)
    return [workshop1, workshop2]
