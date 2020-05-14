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


def test_get_coach(client, auth, coach):
    headers = auth.login(email="coach@test.com")

    response = client.get("/api/v1/coaches/{}".format(coach.id), headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == 200
    assert response_data["email"] == "coach@test.com"


def test_get_coaches(client, auth, admin, coaches):
    headers = auth.login(email="admin@test.com")

    response = client.get("/api/v1/coaches", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == 200
    assert len(response_data) == len(coaches) + 1  # Adding 1 for the admin user


def test_post_coaches_already_existing(client, auth, admin, coach):
    data = dict(
        firstName="firstName",
        lastName="lastName",
        email="coach@test.com",  # Already exists
        password="password",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    )

    headers = auth.login(email="admin@test.com")
    response = client.post("/api/v1/coaches", headers=headers, data=json.dumps(data))
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == UserAlreadyExistsError.code
    assert response_data == UserAlreadyExistsError().get_content()


def test_delete_coaches(client, auth, admin, coach, request):
    headers = auth.login(email="admin@test.com")
    response = client.delete(f"/api/v1/coaches/{coach.id}", headers=headers)

    assert response.status_code == 204
    assert UserModel.find_by_id(user_id=coach.id) is None


def test_delete_inexisting_coach(client, auth, admin):
    headers = auth.login(email="admin@test.com")
    response = client.delete(f"/api/v1/coaches/inexistingId", headers=headers)

    response_data, status_code = json.loads(response.data), response.status_code
    assert status_code == EntityNotFoundError.code
    assert response_data == EntityNotFoundError().get_content()


def test_get_inexisting_coach(client, auth, admin):
    headers = auth.login(email="admin@test.com")

    response = client.get("/api/v1/coaches/inexistingId", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code
    assert status_code == EntityNotFoundError.code
    assert response_data == EntityNotFoundError().get_content()


@pytest.mark.parametrize("data", valid_coach_data)
def test_post_coaches_with_valid_data(client, auth, admin, data, request):
    headers = auth.login(email="admin@test.com")
    response = client.post("/api/v1/coaches", headers=headers, data=json.dumps(data))

    assert response.status_code == 200
    assert UserModel.find_by_email(data["email"]) is not None

    def teardown():
        coach = UserModel.find_by_email(data["email"])
        coach.delete()

    request.addfinalizer(teardown)


def test_post_coaches_with_empty_body(client, auth, admin):
    headers = auth.login(email="admin@test.com")

    response = client.post("/api/v1/coaches", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    assert response_data == EmptyBodyError().get_content()
    assert status_code == EmptyBodyError.code


def test_create_coach_from_participant(client, auth, admin, participant):
    data = dict(
        firstName=participant.firstName,
        lastName=participant.lastName,
        email=participant.email,
        password="password",
        role=Roles.COACH.value,
        city=Cities.PARIS.value,
    )

    headers = auth.login(email="admin@test.com")
    response = client.post("/api/v1/coaches", headers=headers, data=json.dumps(data))

    participant.reload()
    assert response.status_code == 200
    assert Roles.COACH.value in participant.role
