import json

import pytest
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

    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope="function")
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope="function")
def init_admin(session):
    admin = UserModel(
        first_name="admin_first_name",
        last_name="admin_last_name",
        email="admin@test.com",
        password=generate_password_hash("password"),
        role="admin",
    )

    session.add(admin)
    session.commit()
    return admin


@pytest.fixture(scope="function")
def init_moderator(session):
    moderator = UserModel(
        first_name="moderator_first_name",
        last_name="moderator_last_name",
        email="moderator@test.com",
        password=generate_password_hash("password"),
        role="moderator",
    )

    session.add(moderator)
    session.commit()
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
def auth(client, init_admin):
    return AuthActions(client)
