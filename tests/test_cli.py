from werkzeug.security import check_password_hash

from app.cli import create_admin
from app.models.user_model import UserModel


def test_create_admin(cli_runner, db):
    first_name = "admin first name"
    last_name = "admin last name"
    email = "admin@test.com"
    password = "password"

    input_stream = ""
    input_stream += first_name + "\n"  # First name
    input_stream += last_name + "\n"  # Last name
    input_stream += email + "\n"  # Email
    input_stream += password + "\n"  # Password
    input_stream += password + "\n"  # Password confirmation

    cli_runner.invoke(create_admin, input=input_stream)

    user = UserModel.find_by_email("admin@test.com")

    assert user is not None
    assert user.firstName == first_name
    assert user.lastName == last_name
    assert check_password_hash(pwhash=user.password, password=password)
