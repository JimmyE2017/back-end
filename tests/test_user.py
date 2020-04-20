import datetime
import json
import time

from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from app.common.errors import (
    EmailNotFoundError,
    ExpiredTokenError,
    InvalidDataError,
    InvalidPasswordError,
    InvalidTokenError,
    PermissionDeniedError,
    RevokedTokenError,
    UnauthorizedTokenError,
)
from app.common.mail.schemas import password_reset_schema
from app.models.user_model import UserModel


def _get_authorization_header(token):
    return {"Authorization": "Bearer {}".format(token)}


def test_successful_login(client, init_admin):
    data = {"email": "admin@test.com", "password": "password"}

    response = client.post("api/v1/login", data=json.dumps(data))
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == 200
    assert "access_token" in response_data


def test_unsuccessful_login_wrong_email(client, init_admin):
    data = {"email": "email_that_does_not_exist@test.com", "password": "password"}

    response = client.post("api/v1/login", data=json.dumps(data))
    response_data, status_code = json.loads(response.data), response.status_code
    assert status_code == EmailNotFoundError.code
    assert response_data == EmailNotFoundError().get_content()


def test_unsuccessful_login_wrong_password(client, init_admin):
    data = {"email": "admin@test.com", "password": "wrong_password"}

    response = client.post("api/v1/login", data=json.dumps(data))
    response_data, status_code = json.loads(response.data), response.status_code
    assert response_data == InvalidPasswordError().get_content()
    assert status_code == InvalidPasswordError.code


def test_succesful_logout(client, auth, init_admin):
    headers = auth.login(email="admin@test.com")

    response = client.delete("api/v1/logout", headers=headers)

    assert response.status_code == 204


# Request without Authorization header
def test_unauthorized_request(client, db):
    response = client.delete("api/v1/logout")

    response_data, status_code = json.loads(response.data), response.status_code
    assert response_data == UnauthorizedTokenError().get_content()
    assert status_code == UnauthorizedTokenError.code


# Request with expired token
def test_with_expired_token(client, db):
    access_token = create_access_token(
        "dummy expired token", expires_delta=datetime.timedelta(microseconds=1)
    )
    time.sleep(1)

    response = client.delete(
        "api/v1/logout", headers=_get_authorization_header(access_token)
    )

    response_data, status_code = json.loads(response.data), response.status_code
    assert response_data == ExpiredTokenError().get_content()
    assert status_code == ExpiredTokenError.code


# Request with invalid token
def test_with_invalid_token(client, db):
    response = client.delete(
        "api/v1/logout", headers=_get_authorization_header("Invalid token")
    )

    response_data, status_code = json.loads(response.data), response.status_code
    assert response_data == InvalidTokenError().get_content()
    assert status_code == InvalidTokenError.code


# Request with revoked token
def test_with_revoked_token(client, auth, init_admin):
    headers = auth.login(email="admin@test.com")
    auth.logout(headers)
    response = client.delete("api/v1/logout", headers=headers)

    response_data, status_code = json.loads(response.data), response.status_code
    assert response_data == RevokedTokenError().get_content()
    assert status_code == RevokedTokenError.code


def test_access_level_too_low(client, auth, init_coach):
    headers = auth.login(email="coach@test.com")

    # Try to access admin level endpoint
    response = client.post("/api/v1/coaches", headers=headers, data=json.dumps({}))
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == PermissionDeniedError.code
    assert response_data == PermissionDeniedError().get_content()


def test_good_access_level(client, auth, init_coach):
    headers = auth.login(email="coach@test.com")

    # Try to access admin level endpoint
    response = client.get("/api/v1/coaches", headers=headers)

    assert response.status_code == 200


def test_forgotten_password_mail_sent(client, mail, init_coach):
    with mail.record_messages() as outbox:
        data = {"email": init_coach.email}
        response = client.post("/api/v1/forgotten_password", data=json.dumps(data))
        assert response.status_code == 204
        assert len(outbox) == 1
        assert outbox[0].subject == password_reset_schema["subject"]


def test_forgotten_password_invalid_data(client, init_coach):
    data = {"email": "nonexistingemail@test.com"}

    response = client.post("/api/v1/forgotten_password", data=json.dumps(data))
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == EmailNotFoundError.code
    assert response_data == EmailNotFoundError().get_content()


def test_reset_password(client, init_coach):
    data = {"password": "new_password"}

    token = init_coach.send_reset_password_mail()

    response = client.post(
        "/api/v1/reset_password",
        data=json.dumps(data),
        query_string={"access_token": token},
    )
    init_coach = UserModel.find_by_id(user_id=init_coach.id)
    assert response.status_code == 204
    assert check_password_hash(pwhash=init_coach.password, password="new_password")


def test_reset_password_invalid_token(client, init_coach):
    data = {"password": "new_d"}  # Password too short

    init_coach.send_reset_password_mail()

    response = client.post(
        "/api/v1/reset_password",
        data=json.dumps(data),
        query_string={"access_token": "invalid token"},
    )
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == InvalidTokenError.code
    assert response_data == InvalidTokenError().get_content()


def test_reset_password_invalid_new_password(client, init_coach):
    data = {"password": "new_d"}  # Password too short

    token = init_coach.send_reset_password_mail()

    response = client.post(
        "/api/v1/reset_password",
        data=json.dumps(data),
        query_string={"access_token": token},
    )

    assert response.status_code == InvalidDataError.code


def test_user_me(client, auth, init_coach):
    headers = auth.login(email="coach@test.com")
    # Try to access admin level endpoint
    response = client.get("/api/v1/users/me", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == 200
    assert response_data["email"] == "coach@test.com"
