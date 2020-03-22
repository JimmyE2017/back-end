import pytest

from app import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app("test")
    # create the database and load test data
    # with app.app_context():
    #     init_db()
    #     get_db().executescript(_data_sql)

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
