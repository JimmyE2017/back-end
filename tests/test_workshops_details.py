import json
from datetime import datetime

import pytest

from app.models.model_model import Model
from app.models.workshop_model import WorkshopModel


@pytest.fixture(scope="function")
def setup_data(init_coach, request):
    model = Model(
        footprintStructure={
            "cf1": "variable_1",
            "cf2": {"cf2_1": "variable_2", "cf2_2": "variable_3"},
        },
        globalCarbonVariables={
            "global_variable_1": 100,
            "global_variable_2": {"key1": 101, "key2": 102},
        },
        variableFormulas={
            "variable_1": {
                "+": [{"var": "global_variable_1"}, {"var": "survey_variable_1"}]
            },
            "variable_2": {
                "*": [
                    {
                        "var": {
                            "cat": ["global_variable_2.", {"var": "survey_variable_2"}]
                        }
                    },
                    {"var": "survey_variable_3"},
                ]
            },
            "variable_3": {
                "*": [
                    {
                        "var": {
                            "cat": ["global_variable_2.", {"var": "survey_variable_2"}]
                        }
                    },
                    0.5,
                ]
            },
        },
    )

    model.save()

    workshop = WorkshopModel(
        title="workshop_title_1",
        startAt=datetime(2020, 1, 1, 1, 1, 1),
        city="city_1",
        address="address1",
        eventUrl="http://www.example1.com",
        coachId=init_coach.id,
        creatorId=init_coach.id,
        modelId=model.id,
    )

    workshop.save()

    def teardown():
        model.delete()
        workshop.delete()

    request.addfinalizer(teardown)

    return workshop, model


def test_get_workshop(client, auth, init_coach, setup_data):
    workshop, model = setup_data
    headers = auth.login(email="coach@test.com")

    response = client.get("/api/v1/workshops/{}".format(workshop.id), headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    expected_output = {
        "title": workshop.title,
        "startAt": workshop.startAt.isoformat(),
        "city": workshop.city,
        "address": workshop.address,
        "eventUrl": workshop.eventUrl,
        "coachId": workshop.coachId,
        "creatorId": workshop.creatorId,
        "workshopId": workshop.id,
        "model": {
            "id": model.id,
            "globalCarbonVariables": model.globalCarbonVariables,
            "variableFormulas": model.variableFormulas,
            "footprintStructure": model.footprintStructure,
        },
    }
    assert status_code == 200
    assert response_data == expected_output
