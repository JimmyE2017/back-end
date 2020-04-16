import json

import click
from flask.cli import with_appcontext

from app.common.errors import CustomException
from app.services.coach_services import create_admin_user


@click.command("create_admin")
@click.option("--firstname", default="admin", prompt="User first name")
@click.option("--lastname", default="user", prompt="User last name")
@click.option("--email", default="admin@test.com", prompt="Email")
@click.password_option()
@with_appcontext
def create_admin(firstname, lastname, email, password):
    """
        Creates an admin user
    """
    data = {
        "email": email,
        "password": password,
        "firstName": firstname,
        "lastName": lastname,
    }
    try:
        create_admin_user(data=json.dumps(data))
    except CustomException as e:
        click.echo(click.style("Issue when creating admin.", fg="red"))
        click.echo(json.dumps(e.get_content(), indent=2))
        return
    click.echo(click.style("Admin User {0} created.".format(email), fg="green"))

    return


cli_commands = [create_admin]
