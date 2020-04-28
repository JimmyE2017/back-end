import csv
import json

import click
from flask.cli import with_appcontext

from app.common.errors import CustomException
from app.models import db
from app.models.action_card_model import ActionCardBatchModel, ActionCardModel
from app.models.city_model import Cities
from app.models.user_model import Roles
from app.services.coach_services import create_coach

MODELS_WITH_ENABLED_IMPORTCSV = {
    "actionCards": ActionCardModel,
    "actionCardBatches": ActionCardBatchModel,
}


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
        "role": Roles.ADMIN.value,
        "city": Cities.PARIS.value,
    }
    try:
        user, _ = create_coach(data=json.dumps(data))
    except CustomException as e:
        click.echo(click.style("Issue when creating admin.", fg="red"))
        click.echo(json.dumps(e.get_content(), indent=2))
        raise e
    click.echo(click.style("{0} created.".format(str(user)), fg="green"))

    return


def _parse_row(row, model):
    for k, v in row.items():
        if isinstance(getattr(model, k), db.ListField):
            row[k] = json.loads(v)
    return row


@click.command("importcsv")
@click.option(
    "--drop/--no-drop",
    default=False,
    help="Whether to drop the collection beforehand or not",
)
@click.argument("collection")
@click.argument("csv_file", type=click.Path(exists=True))
def importcsv(collection, csv_file, drop):
    """ Import a CSV file into a given collection

    COLLECTION is the name of the target mongo collection

    CSV_FILE is the path to the file

    CSV delimiter should be a comma and lines separeted by newline
    """
    if collection not in MODELS_WITH_ENABLED_IMPORTCSV:
        click.echo(
            click.style(
                "Collection {} does not support importcsv.".format(collection), fg="red"
            )
        )
        click.echo(
            "Only the following collections support import csv : {}".format(
                ", ".join([c for c in MODELS_WITH_ENABLED_IMPORTCSV.keys()])
            )
        )
        raise Exception("Collection {} does not support importcsv.".format(collection))

    model = MODELS_WITH_ENABLED_IMPORTCSV[collection]

    if drop:
        click.echo("Dropping collection {}".format(collection))
        model.drop_collection()
    count = 0
    with open(csv_file, "r") as fr:
        reader = csv.DictReader(fr)
        for row in reader:
            data = model(**_parse_row(row, model))
            data.save()
            count += 1
    click.echo(
        click.style(
            "Successfully inserted {} objects in collection {}".format(
                count, collection
            ),
            fg="green",
        )
    )
    return


cli_commands = [create_admin, importcsv]
