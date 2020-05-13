import json

import pytest

from app.common.errors import (
    EmptyBodyError,
    EntityNotFoundError,
    UserAlreadyExistsError,
)
from app.models.city_model import Cities
from app.models.user_model import Roles, UserModel

valid_coach_data = [
    dict(
        firstName="firstName5",
        lastName="lastName5",
        email="coach5@test.com",
        password="password5",
        role=Roles.ADMIN.value,
        city=Cities.PARIS.value,
    ),
    dict(
        firstName="firstName6",
        lastName="lastName6",
        email="coach6@test.com",
        password="password6",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    ),
    dict(
        firstName="firstName7",
        lastName="lastName7",
        email="coach7@test.com",
        password="password7",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    ),
]

invalid_coaches_data = [
    dict(  # Missing email
        firstName="firstName1",
        lastName="lastName1",
        password="password1",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    ),
    dict(  # Missing first name
        lastName="lastName2",
        email="coach8@test.com",
        password="password2",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    ),
    dict(  # Missing last name
        firstName="firstName3",
        email="coach9@test.com",
        password="password3",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    ),
    dict(  # Missing password
        firstName="firstName4",
        lastName="lastName4",
        email="coach4@test.com",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    ),
    dict(  # Missing role
        firstName="firstName4",
        lastName="lastName4",
        email="coach4@test.com",
        password="password3",
        city=Cities.PARIS.value,
    ),
    dict(  # Missing city
        firstName="firstName4",
        lastName="lastName4",
        email="coach4@test.com",
        password="password3",
        role=Roles.COACH.value,
    ),
    dict(  # Password too short
        firstName="firstName5",
        lastName="lastName5",
        email="coach10@test.com",
        password="passw",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    ),
    dict(  # Empty first name
        firstName="",
        lastName="lastName6",
        email="coach11@test.com",
        password="password6",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    ),
    dict(  # Invalid email
        firstName="firstName7",
        lastName="lastName7",
        email="coach7",
        password="password7",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    ),
    dict(  # Invalid role
        firstName="firstName7",
        lastName="lastName7",
        email="coach8@test.com",
        password="password7",
        role=Roles.GUEST.value,
        city=Cities.PARIS.value,
    ),
]


@pytest.fixture(scope="class")
def create_some_coaches(db, request):
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


@pytest.mark.usefixtures("create_some_coaches")
class TestCoachRessourcesWithExistingData:
    def test_get_coach(self, client, auth, init_coach):
        headers = auth.login(email="coach@test.com")

        response = client.get(
            "/api/v1/coaches/{}".format(init_coach.id), headers=headers
        )
        response_data, status_code = json.loads(response.data), response.status_code

        assert status_code == 200
        assert response_data["email"] == "coach@test.com"

    def test_get_coaches(self, client, auth, init_admin):
        headers = auth.login(email="admin@test.com")

        response = client.get("/api/v1/coaches", headers=headers)
        response_data, status_code = json.loads(response.data), response.status_code

        assert status_code == 200
        assert len(response_data) == 3 + 1  # Adding 1 for the admin user

    def test_post_coaches_already_existing(self, client, auth, init_admin):
        data = dict(
            firstName="firstName4",
            lastName="lastName4",
            email="coach1@test.com",  # Already exists
            password="password4",
            role=Roles.COACH.value,
            city=Cities.PARIS.value,
        )

        headers = auth.login(email="admin@test.com")
        response = client.post(
            "/api/v1/coaches", headers=headers, data=json.dumps(data)
        )
        response_data, status_code = json.loads(response.data), response.status_code

        assert status_code == UserAlreadyExistsError.code
        assert response_data == UserAlreadyExistsError().get_content()


def test_delete_coaches(client, auth, init_admin, request):
    coach = UserModel(
        firstName="firstName1",
        lastName="lastName1",
        email="coach1@test.com",
        password="password1",
        role=[Roles.COACH.value],
        city=Cities.PARIS.value,
    )
    coach.save()

    headers = auth.login(email="admin@test.com")
    response = client.delete(f"/api/v1/coaches/{coach.id}", headers=headers)

    assert response.status_code == 204
    assert UserModel.find_by_id(user_id=coach.id) is None

    def teardown():
        coach.delete()

    request.addfinalizer(teardown)


def test_delete_inexisting_coach(client, auth, init_admin):

    headers = auth.login(email="admin@test.com")
    response = client.delete(f"/api/v1/coaches/inexistingId", headers=headers)

    response_data, status_code = json.loads(response.data), response.status_code
    assert status_code == EntityNotFoundError.code
    assert response_data == EntityNotFoundError().get_content()


def test_get_inexisting_coach(client, auth, init_admin):
    headers = auth.login(email="admin@test.com")

    response = client.get("/api/v1/coaches/inexistingId", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code
    assert status_code == EntityNotFoundError.code
    assert response_data == EntityNotFoundError().get_content()


@pytest.mark.parametrize("data", valid_coach_data)
def test_post_coaches_with_valid_data(client, auth, init_admin, data, request):
    headers = auth.login(email="admin@test.com")
    response = client.post("/api/v1/coaches", headers=headers, data=json.dumps(data))

    assert response.status_code == 200
    assert UserModel.find_by_email(data["email"]) is not None

    def teardown():
        coach = UserModel.find_by_email(data["email"])
        coach.delete()

    request.addfinalizer(teardown)


@pytest.mark.parametrize("data", invalid_coaches_data)
def test_post_coaches_with_invalid_data(client, auth, init_admin, data):
    headers = auth.login(email="admin@test.com")

    response = client.post("/api/v1/coaches", headers=headers, data=json.dumps(data))

    assert response.status_code == 400
    assert UserModel.find_by_email(data.get("email", "")) is None


def test_post_coaches_with_empty_body(client, auth, init_admin):
    headers = auth.login(email="admin@test.com")

    response = client.post("/api/v1/coaches", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    assert response_data == EmptyBodyError().get_content()
    assert status_code == EmptyBodyError.code
