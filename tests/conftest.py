import json

import pytest
from mongoengine import get_db
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db as _db
from app.models.user_model import UserModel


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
def db(app, request):
    """Session-wide test database."""
    _db.app = app

    def teardown():
        me = get_db()
        db_name = app.config["MONGODB_DB"]
        for collection in me.client.get_database(db_name).list_collection_names():
            me.client.get_database(db_name).drop_collection(collection)

    request.addfinalizer(teardown)
    return _db


# TODO : Check if the following two functions can be less repetitive
@pytest.fixture(scope="function")
def init_admin(db, request):
    """
    Create an admin for the scope of a function
    Remove it at the end
    """
    admin = UserModel(
        firstName="admin_first_name",
        lastName="admin_last_name",
        email="admin@test.com",
        password=generate_password_hash("password"),
        role="admin",
    )

    admin.save()

    # Delete admin at the end
    def teardown():
        admin.delete()

    request.addfinalizer(teardown)
    return admin


@pytest.fixture(scope="function")
def init_moderator(db, request):
    moderator = UserModel(
        firstName="moderator_first_name",
        lastName="moderator_last_name",
        email="moderator@test.com",
        password=generate_password_hash("password"),
        role="moderator",
    )

    moderator.save()

    # Delete moderator at the end
    def teardown():
        moderator.delete()

    request.addfinalizer(teardown)
    return moderator


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
