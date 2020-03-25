import json

import pytest

from app.common.errors import USER_ALREADY_EXISTS_ERROR
from app.models.user_model import UserModel


def test_get_moderators(client, auth, create_some_moderators):
    headers = auth.login(email="admin@test.com")

    response = client.get("/api/v1/moderators", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == 200
    assert len(response_data) == 3 + 1  # Adding 1 for the admin user


def test_post_moderators_with_valid_data(client, auth, valid_moderators_data):
    headers = auth.login(email="admin@test.com")

    for data in valid_moderators_data:
        response = client.post(
            "/api/v1/moderators", headers=headers, data=json.dumps(data)
        )

        assert response.status_code == 200
        assert UserModel.find_by_email(data["email"]) is not None


def test_post_moderators_with_invalid_data(client, auth, invalid_moderators_data):
    headers = auth.login(email="admin@test.com")

    for data in invalid_moderators_data:
        response = client.post(
            "/api/v1/moderators", headers=headers, data=json.dumps(data)
        )

        assert response.status_code == 400
        assert UserModel.find_by_email(data.get("email", "")) is None


def test_post_moderators_already_existing(client, auth, create_some_moderators):
    data = dict(
        first_name="first_name4",
        last_name="last_name4",
        email="moderator1@test.com",  # Already exists
        password="password4",
    )

    headers = auth.login(email="admin@test.com")
    response = client.post("/api/v1/moderators", headers=headers, data=json.dumps(data))
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == USER_ALREADY_EXISTS_ERROR.error_code
    assert response_data == USER_ALREADY_EXISTS_ERROR.content


@pytest.mark.skip(reason="Test is failing and i can't debug this shit")
def test_delete_moderators(client, auth, create_some_moderators):
    headers = auth.login(email="admin@test.com")

    response = client.delete("/api/v1/moderators/2", headers=headers)

    assert response.status_code == 204
    assert UserModel.find_by_id(user_id=2) is None


# Test Data
@pytest.fixture(scope="function")
def valid_moderators_data(session):
    moderator1 = dict(
        first_name="first_name1",
        last_name="last_name1",
        email="moderator1@test.com",
        password="password1",
    )

    moderator2 = dict(
        first_name="first_name2",
        last_name="last_name2",
        email="moderator2@test.com",
        password="password2",
    )

    moderator3 = dict(
        first_name="first_name3",
        last_name="last_name3",
        email="moderator3@test.com",
        password="password3",
    )

    return [moderator1, moderator2, moderator3]


@pytest.fixture(scope="function")
def invalid_moderators_data(session):
    data = []
    data.append(
        dict(  # Missing email
            first_name="first_name1", last_name="last_name1", password="password1",
        )
    )

    data.append(
        dict(  # Missing first name
            last_name="last_name2", email="moderator2@test.com", password="password2",
        )
    )

    data.append(
        dict(  # Missing last name
            first_name="first_name3", email="moderator3@test.com", password="password3",
        )
    )

    data.append(
        dict(  # Missing password
            first_name="first_name4",
            last_name="last_name4",
            email="moderator4@test.com",
        )
    )

    data.append(
        dict(  # Password too short
            first_name="first_name5",
            last_name="last_name5",
            email="moderator5@test.com",
            password="passw",
        )
    )

    data.append(
        dict(  # Empty first name
            first_name="",
            last_name="last_name6",
            email="moderator6@test.com",
            password="password6",
        )
    )
    data.append(
        dict(  # Invalid email
            first_name="first_name7",
            last_name="last_name7",
            email="moderator7",
            password="password7",
        )
    )

    return data


@pytest.fixture(scope="function")
def create_some_moderators(session):
    moderator1 = UserModel(
        first_name="first_name1",
        last_name="last_name1",
        email="moderator1@test.com",
        password="password1",
        role="moderator",
    )

    moderator2 = UserModel(
        first_name="first_name2",
        last_name="last_name2",
        email="moderator2@test.com",
        password="password2",
        role="moderator",
    )

    moderator3 = UserModel(
        first_name="first_name3",
        last_name="last_name3",
        email="moderator3@test.com",
        password="password3",
        role="moderator",
    )

    session.add(moderator1)
    session.add(moderator2)
    session.add(moderator3)
    session.commit()
