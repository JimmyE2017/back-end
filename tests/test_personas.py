import json

import pytest
from mongoengine import DoesNotExist

from app.common.errors import EmptyBodyError, EntityNotFoundError
from app.models.workshop_model import WorkshopModel


def test_get_workshop(
    client, auth, coach, workshop_with_persona, model_with_personas, personas
):
    headers = auth.login(email="coach@test.com")

    response = client.get(
        "/api/v1/workshops/{}".format(workshop_with_persona.id), headers=headers
    )
    response_data, status_code = json.loads(response.data), response.status_code
    expected_output = {
        "name": workshop_with_persona.name,
        "startAt": workshop_with_persona.startAt.isoformat(),
        "city": workshop_with_persona.city,
        "address": workshop_with_persona.address,
        "eventUrl": workshop_with_persona.eventUrl,
        "coachId": workshop_with_persona.coachId,
        "creatorId": workshop_with_persona.creatorId,
        "id": workshop_with_persona.id,
        "participants": [],
        "model": {
            "id": model_with_personas.id,
            "globalCarbonVariables": model_with_personas.globalCarbonVariables,
            "variableFormulas": model_with_personas.variableFormulas,
            "footprintStructure": model_with_personas.footprintStructure,
            "personas": [
                {
                    "id": personas[0].id,
                    "firstName": personas[0].firstName,
                    "lastName": personas[0].lastName,
                    "description": personas[0].description,
                    "answers": {"meat_per_day": 9000, "car_type": "futuristic"},
                },
                {
                    "id": personas[1].id,
                    "firstName": personas[1].firstName,
                    "lastName": personas[1].lastName,
                    "description": personas[1].description,
                    "answers": {"meat_per_day": 0, "car_type": None},
                },
            ],
            "actionCards": [],
            "actionCardBatches": [],
        },
    }
    assert status_code == 200
    assert response_data == expected_output
