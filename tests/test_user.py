import datetime
import json
import time

from flask_jwt_extended import create_access_token

from app.common.errors import (
    EXPIRED_TOKEN,
    INVALID_TOKEN,
    PERMISSION_DENIED,
    REVOKED_TOKEN,
    UNAUTHORIZED_TOKEN,
    UNSUCCESSFUL_LOGIN_EMAIL_NOT_FOUND,
    UNSUCCESSFUL_LOGIN_WRONG_PASSWORD,
)


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
    assert status_code == UNSUCCESSFUL_LOGIN_EMAIL_NOT_FOUND.error_code
    assert response_data == UNSUCCESSFUL_LOGIN_EMAIL_NOT_FOUND.content


def test_unsuccessful_login_wrong_password(client, init_admin):
    data = {"email": "admin@test.com", "password": "wrong_password"}

    response = client.post("api/v1/login", data=json.dumps(data))
    response_data, status_code = json.loads(response.data), response.status_code
    assert response_data == UNSUCCESSFUL_LOGIN_WRONG_PASSWORD.content
    assert status_code == UNSUCCESSFUL_LOGIN_WRONG_PASSWORD.error_code


def test_succesful_logout(client, auth, init_admin):
    headers = auth.login(email="admin@test.com")

    response = client.delete("api/v1/logout", headers=headers)

    assert response.status_code == 204


# Request without Authorization header
def test_unauthorized_request(client, db):
    response = client.delete("api/v1/logout")

    response_data, status_code = json.loads(response.data), response.status_code
    assert response_data == UNAUTHORIZED_TOKEN.content
    assert status_code == UNAUTHORIZED_TOKEN.error_code


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
    assert response_data == EXPIRED_TOKEN.content
    assert status_code == EXPIRED_TOKEN.error_code


# Request with invalid token
def test_with_invalid_token(client, db):

    response = client.delete(
        "api/v1/logout", headers=_get_authorization_header("Invalid token")
    )

    response_data, status_code = json.loads(response.data), response.status_code
    assert response_data == INVALID_TOKEN.content
    assert status_code == INVALID_TOKEN.error_code


# Request with revoked token
def test_with_revoked_token(client, auth, init_admin):
    headers = auth.login(email="admin@test.com")
    auth.logout(headers)
    response = client.delete("api/v1/logout", headers=headers)

    response_data, status_code = json.loads(response.data), response.status_code
    assert response_data == REVOKED_TOKEN.content
    assert status_code == REVOKED_TOKEN.error_code


def test_access_level_too_low(client, auth, init_moderator):
    headers = auth.login(email="moderator@test.com")

    # Try to access admin level endpoint
    response = client.post("/api/v1/moderators", headers=headers, data=json.dumps({}))
    response_data, status_code = json.loads(response.data), response.status_code

    assert status_code == PERMISSION_DENIED.error_code
    assert response_data == PERMISSION_DENIED.content


def test_good_access_level(client, auth, init_moderator):
    headers = auth.login(email="moderator@test.com")

    # Try to access admin level endpoint
    response = client.get("/api/v1/moderators", headers=headers)

    assert response.status_code == 200
