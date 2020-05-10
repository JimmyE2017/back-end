import json
import os
from csv import DictReader

from werkzeug.security import check_password_hash

from app.cli import create_admin, importcsv, importjson
from app.models.action_card_model import ActionCardBatchModel, ActionCardModel
from app.models.model_model import Model
from app.models.user_model import UserModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_create_admin(cli_runner, db, request):
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

    def teardown():
        user.delete()

    request.addfinalizer(teardown)


def test_create_admin_already_existing(cli_runner, init_admin):
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

    result = cli_runner.invoke(create_admin, input=input_stream)
    assert "Issue when creating admin." in result.output


def test_importcsv_with_model_not_enabled(cli_runner):
    collection = "users"
    csv_file = "{}/ressources/csv/action_cards.csv.example".format(BASE_DIR)

    result = cli_runner.invoke(importcsv, [collection, csv_file])
    assert (
        "Collection {} does not support importcsv.".format(collection) in result.output
    )


def test_importcsv_no_drop(cli_runner, db, request):
    collection = "actionCards"
    csv_file = "{}/ressources/csv/action_cards.csv.example".format(BASE_DIR)

    # Inserting an action card beforehand
    action_card4 = ActionCardModel(
        number=4,
        title="action_card_title_4",
        category="action_card_category_4",
        type="action_card_type_4",
        key="action_card_key_4",
        sector="action_card_sector_4",
        cost=4,
    )
    action_card4.save()

    count = 0
    with open(csv_file, "r") as fr:
        reader = DictReader(fr)
        for _ in reader:
            count += 1

    result = cli_runner.invoke(importcsv, [collection, csv_file])
    assert (
        "Successfully inserted {} objects in collection {}".format(count, collection)
        in result.output
    )
    assert len(ActionCardModel.find_all()) == count + 1

    def teardown():
        ActionCardModel.drop_collection()

    request.addfinalizer(teardown)


def test_importcsv_with_drop(cli_runner, db, request):
    collection = "actionCards"
    csv_file = "{}/ressources/csv/action_cards.csv.example".format(BASE_DIR)

    # Inserting an action card beforehand
    action_card4 = ActionCardModel(
        number=4,
        title="action_card_title_4",
        category="action_card_category_4",
        type="action_card_type_4",
        key="action_card_key_4",
        sector="action_card_sector_4",
        cost=4,
    )
    action_card4.save()

    count = 0
    with open(csv_file, "r") as fr:
        reader = DictReader(fr)
        for _ in reader:
            count += 1

    result = cli_runner.invoke(importcsv, ["--drop", collection, csv_file])
    assert (
        "Successfully inserted {} objects in collection {}".format(count, collection)
        in result.output
    )
    assert len(ActionCardModel.find_all()) == count

    def teardown():
        ActionCardModel.drop_collection()

    request.addfinalizer(teardown)


def test_importcsv_with_list_fields(cli_runner, db, request):
    collection = "actionCardBatches"
    csv_file = "{}/ressources/csv/action_card_batches.csv.example".format(BASE_DIR)

    count = 0
    with open(csv_file, "r") as fr:
        reader = DictReader(fr)
        for _ in reader:
            count += 1

    result = cli_runner.invoke(importcsv, ["--drop", collection, csv_file])
    assert (
        "Successfully inserted {} objects in collection {}".format(count, collection)
        in result.output
    )
    assert len(ActionCardBatchModel.objects()) == count

    def teardown():
        ActionCardBatchModel.drop_collection()

    request.addfinalizer(teardown)


def test_importjson_with_drop(cli_runner, db, request):
    collection = "models"
    json_file = "{}/ressources/json/models.json.example".format(BASE_DIR)

    # Inserting an action card beforehand
    model1 = Model(
        footprintStructure={"footprint_category_1": "variable_1"},
        variableFormulas={"variable_1": {"+": [{"var": "global_variable_name"}, 1295]}},
        globalCarbonVariables={"global_variable_name": 42},
    )
    model1.save()

    with open(json_file, "r") as fr:
        json_data = json.load(fr)
    count = len(json_data) if isinstance(json_data, list) else 1

    result = cli_runner.invoke(importjson, ["--drop", collection, json_file])
    assert (
        "Successfully inserted {} objects in collection {}".format(count, collection)
        in result.output
    )
    assert len(Model.objects()) == count

    def teardown():
        Model.drop_collection()

    request.addfinalizer(teardown)


def test_importjson_without_drop(cli_runner, db, request):
    collection = "models"
    json_file = "{}/ressources/json/models.json.example".format(BASE_DIR)

    # Inserting an action card beforehand
    model1 = Model(
        footprintStructure={"footprint_category_1": "variable_1"},
        variableFormulas={"variable_1": {"+": [{"var": "global_variable_name"}, 1295]}},
        globalCarbonVariables={"global_variable_name": 42},
    )
    model1.save()

    with open(json_file, "r") as fr:
        json_data = json.load(fr)
    count = len(json_data) if isinstance(json_data, list) else 1

    result = cli_runner.invoke(importjson, ["--no-drop", collection, json_file])
    assert (
        "Successfully inserted {} objects in collection {}".format(count, collection)
        in result.output
    )
    assert len(Model.objects()) == count + 1

    def teardown():
        Model.drop_collection()

    request.addfinalizer(teardown)
