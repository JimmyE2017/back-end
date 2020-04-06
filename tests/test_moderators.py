import json

import pytest

from app.common.errors import EMPTY_BODY_ERROR, USER_ALREADY_EXISTS_ERROR
from app.models.user_model import UserModel

# Test Data
valid_moderator_data = [
    dict(
        firstName="firstName5",
        lastName="lastName5",
        email="moderator5@test.com",
        password="password5",
    ),
    dict(
        firstName="firstName6",
        lastName="lastName6",
        email="moderator6@test.com",
        password="password6",
    ),
    dict(
        firstName="firstName7",
        lastName="lastName7",
        email="moderator7@test.com",
        password="password7",
    ),
]

invalid_moderators_data = [
    dict(  # Missing email
        firstName="firstName1", lastName="lastName1", password="password1",
    ),
    dict(  # Missing first name
        lastName="lastName2", email="moderator8@test.com", password="password2",
    ),
    dict(  # Missing last name
        firstName="firstName3", email="moderator9@test.com", password="password3",
    ),
    dict(  # Missing password
        firstName="firstName4", lastName="lastName4", email="moderator4@test.com",
    ),
    dict(  # Password too short
        firstName="firstName5",
        lastName="lastName5",
        email="moderator10@test.com",
        password="passw",
    ),
    dict(  # Empty first name
        firstName="",
        lastName="lastName6",
        email="moderator11@test.com",
        password="password6",
    ),
    dict(  # Invalid email
        firstName="firstName7",
        lastName="lastName7",
        email="moderator7",
        password="password7",
    ),
]


@pytest.fixture(scope="class")
def create_some_moderators(db, request):
    moderator1 = UserModel(
        firstName="firstName1",
        lastName="lastName1",
        email="moderator1@test.com",
        password="password1",
        role="moderator",
    )

    moderator2 = UserModel(
        firstName="firstName2",
        lastName="lastName2",
        email="moderator2@test.com",
        password="password2",
        role="moderator",
    )

    moderator3 = UserModel(
        firstName="firstName3",
        lastName="lastName3",
        email="moderator3@test.com",
        password="password3",
        role="moderator",
    )

    moderator1.save()
    moderator2.save()
    moderator3.save()

    def teardown():
        moderator1.delete()
        moderator2.delete()
        moderator3.delete()

    request.addfinalizer(teardown)


@pytest.mark.usefixtures("create_some_moderators")
class TestModeratorRessourcesWithExistingData:
    def test_get_moderators(self, client, auth, init_admin):
        headers = auth.login(email="admin@test.com")

        response = client.get("/api/v1/moderators", headers=headers)
        response_data, status_code = json.loads(response.data), response.status_code

        assert status_code == 200
        assert len(response_data) == 3 + 1  # Adding 1 for the admin user

    def test_post_moderators_already_existing(self, client, auth, init_admin):
        data = dict(
            firstName="firstName4",
            lastName="lastName4",
            email="moderator1@test.com",  # Already exists
            password="password4",
        )

        headers = auth.login(email="admin@test.com")
        response = client.post(
            "/api/v1/moderators", headers=headers, data=json.dumps(data)
        )
        response_data, status_code = json.loads(response.data), response.status_code

        assert status_code == USER_ALREADY_EXISTS_ERROR.error_code
        assert response_data == USER_ALREADY_EXISTS_ERROR.content


def test_delete_moderators(client, auth, init_admin, request):
    moderator = UserModel(
        firstName="firstName1",
        lastName="lastName1",
        email="moderator1@test.com",
        password="password1",
        role="moderator",
    )
    moderator.save()

    headers = auth.login(email="admin@test.com")
    response = client.delete(f"/api/v1/moderators/{moderator.id}", headers=headers)

    assert response.status_code == 204
    assert UserModel.find_by_id(user_id=moderator.id) is None

    def teardown():
        moderator.delete()

    request.addfinalizer(teardown)


@pytest.mark.parametrize("data", valid_moderator_data)
def test_post_moderators_with_valid_data(client, auth, init_admin, data, request):
    headers = auth.login(email="admin@test.com")
    response = client.post("/api/v1/moderators", headers=headers, data=json.dumps(data))

    assert response.status_code == 200
    assert UserModel.find_by_email(data["email"]) is not None

    def teardown():
        moderator = UserModel.find_by_email(data["email"])
        moderator.delete()

    request.addfinalizer(teardown)


@pytest.mark.parametrize("data", invalid_moderators_data)
def test_post_moderators_with_invalid_data(client, auth, init_admin, data):
    headers = auth.login(email="admin@test.com")

    response = client.post("/api/v1/moderators", headers=headers, data=json.dumps(data))

    assert response.status_code == 400
    assert UserModel.find_by_email(data.get("email", "")) is None


def test_post_moderators_with_empty_body(client, auth, init_admin):
    headers = auth.login(email="admin@test.com")

    response = client.post("/api/v1/moderators", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    assert response_data == EMPTY_BODY_ERROR.content
    assert status_code == EMPTY_BODY_ERROR.error_code
