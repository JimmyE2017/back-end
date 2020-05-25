import json

from app.models.city_model import Cities
from app.models.workshop_model import WorkshopParticipantStatus


def test_get_workshop(
    client,
    auth,
    coach,
    workshop,
    model,
    action_cards,
    action_card_batches,
    participant,
    carbon_form_answers,
    personas,
):
    headers = auth.login(email="coach@test.com")

    response = client.get("/api/v1/workshops/{}".format(workshop.id), headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code
    expected_output = {
        "name": workshop.name,
        "startAt": workshop.startAt.isoformat(),
        "city": workshop.city,
        "address": workshop.address,
        "eventUrl": workshop.eventUrl,
        "coachId": workshop.coachId,
        "creatorId": workshop.creatorId,
        "id": workshop.id,
        "startYear": workshop.startYear,
        "endYear": workshop.endYear,
        "rounds": workshop.rounds,
        "yearIncrement": workshop.yearIncrement,
        "participants": [
            {
                "status": WorkshopParticipantStatus.TOCHECK.value,
                "email": participant.email,
                "firstName": participant.firstName,
                "lastName": participant.lastName,
                "id": participant.userId,
                "surveyVariables": carbon_form_answers.answers,
            }
        ],
        "model": {
            "id": model.id,
            "globalCarbonVariables": model.globalCarbonVariables,
            "variableFormulas": model.variableFormulas,
            "footprintStructure": model.footprintStructure,
            "actionCards": [
                {
                    "id": action_card.actionCardId,
                    "cardNumber": action_card.cardNumber,
                    "name": action_card.name,
                    "category": action_card.category,
                    "type": action_card.type,
                    "key": action_card.key,
                    "sector": action_card.sector,
                    "cost": action_card.cost,
                    "impactType": action_card.impactType,
                    "operations": [
                        {"variable": op.variable, "operation": op.operation}
                        for op in action_card.operations
                    ],
                }
                for action_card in action_cards
            ],
            "actionCardBatches": [
                {
                    "id": action_card_batch.actionCardBatchId,
                    "name": action_card_batch.name,
                    "type": action_card_batch.type,
                    "actionCardIds": action_card_batch.actionCardIds,
                }
                for action_card_batch in action_card_batches
            ],
            "personas": [
                {
                    "id": persona.id,
                    "firstName": persona.firstName,
                    "lastName": persona.lastName,
                    "description": persona.description,
                    "answers": persona.answers,
                }
                for persona in personas
            ],
        },
    }
    assert status_code == 200
    assert response_data == expected_output


def test_put_workshop(
    client,
    auth,
    coach,
    workshop,
    model,
    action_cards,
    action_card_batches,
    participant,
    carbon_form_answers,
):
    headers = auth.login(email="coach@test.com")
    data = {
        "name": "workshop_name_bis",
        "startAt": "2020-01-01T22:00:00Z",
        "coachId": workshop.coachId,
        "city": Cities.PARIS.value,
        "address": "address_bis",
        "eventUrl": "http://www.example_bis.com",
        "startYear": 2020,
        "endYear": 2050,
        "yearIncrement": 3,
        "participants": [
            # {
            #     "id": participant.id,
            #     "firstName": "Participant First name",
            #     "lastName": "Participant Last name",
            #     "email": "participant@test.com",
            #     "status": "tocheck",
            #     "surveyVariables": {
            #         "meat_per_day": 9000,
            #         "car_type": "futuristic"
            #     }
            # }
        ],
        "rounds": [
            {
                "year": 2020,
                "carbonVariables": [
                    {
                        "participantId": participant.id,
                        "variables": {
                            "hours_urban_train_per_week": 10,
                            "km_country_train": 5,
                            "km_plane": 200,
                        },
                    }
                ],
                "carbonFootprints": [
                    {
                        "participantId": participant.id,
                        "footprint": {
                            "transport": {
                                "plane": 1000,
                                "train": {"urbanTrain": 100, "mainlineTrain": 500},
                            }
                        },
                    }
                ],
                "roundConfig": {
                    "actionCardType": "individual",
                    "targetedYear": 2023,
                    "budget": 4,
                    "actionCardBatchIds": [
                        "actionCardId1",
                        "actionCardId2",
                        "actionCardId4",
                    ],
                },
            }
        ],
    }
    response = client.put(
        "/api/v1/workshops/{}".format(workshop.id),
        headers=headers,
        data=json.dumps(data),
    )

    workshop.reload()
    assert response.status_code == 200

    # Assert round are updated
    for round_data in data["rounds"]:
        workshop_round = [x for x in workshop.rounds if x.year == round_data["year"]]
        assert len(workshop_round) == 1  # Test existence of workshop round
        workshop_round = workshop_round[0]

        # Assert carbonVariables are updated
        if "carbonVariables" in round_data:
            for carbon_variables_data in round_data["carbonVariables"]:
                carbon_variables = [
                    x
                    for x in workshop_round.carbonVariables
                    if x.participant.pk == carbon_variables_data["participantId"]
                ]
                assert len(carbon_variables) == 1  # Assert existance of carbon info
                carbon_variables = carbon_variables[0]
                assert carbon_variables.variables == carbon_variables_data["variables"]

        # Assert carbonFootprints are updated
        if "carbonFootprints" in round_data:
            for carbon_footprint_data in round_data["carbonFootprints"]:
                carbon_footprints = [
                    x
                    for x in workshop_round.carbonFootprints
                    if x.participant.pk == carbon_footprint_data["participantId"]
                ]
                assert len(carbon_footprints) == 1  # Assert existance of carbon info
                carbon_footprints = carbon_footprints[0]
                assert carbon_footprints.footprint == carbon_footprints["footprint"]

        # Assert roundConfig is updated
        if "roundConfig" in round_data:
            round_config_data = round_data["roundConfig"]
            assert workshop_round.roundConfig is not None

            workshop_round_config = workshop_round.roundConfig
            assert (
                workshop_round_config.actionCardType
                == round_config_data["actionCardType"]
            )
            assert (
                workshop_round_config.targetedYear == round_config_data["targetedYear"]
            )
            if "actionCardBatchIds" in round_config_data:
                assert workshop_round_config.actionCardBatches is not None
                ids = [acb.pk for acb in workshop_round_config.actionCardBatches]
                for acb_id in round_config_data["actionCardBatchIds"]:
                    assert acb_id in ids


def test_put_workshop_invalid_participant_in_rounds_carbon_footprints(
    client,
    auth,
    coach,
    workshop,
    model,
    action_cards,
    action_card_batches,
    participant,
    carbon_form_answers,
):
    headers = auth.login(email="coach@test.com")
    data = {
        "name": "workshop_name_bis",
        "startAt": "2020-01-01T22:00:00Z",
        "coachId": workshop.coachId,
        "city": Cities.PARIS.value,
        "address": "address_bis",
        "eventUrl": "http://www.example_bis.com",
        "startYear": 2020,
        "endYear": 2050,
        "yearIncrement": 3,
        "participants": [
            # {
            #     "id": participant.id,
            #     "firstName": "Participant First name",
            #     "lastName": "Participant Last name",
            #     "email": "participant@test.com",
            #     "status": "tocheck",
            #     "surveyVariables": {
            #         "meat_per_day": 9000,
            #         "car_type": "futuristic"
            #     }
            # }
        ],
        "rounds": [
            {
                "year": 2020,
                "carbonVariables": [
                    {
                        "participantId": participant.id,
                        "variables": {
                            "hours_urban_train_per_week": 10,
                            "km_country_train": 5,
                            "km_plane": 200,
                        },
                    }
                ],
                "carbonFootprints": [
                    {
                        "participantId": "wrong id",
                        "footprint": {
                            "transport": {
                                "plane": 1000,
                                "train": {"urbanTrain": 100, "mainlineTrain": 500},
                            }
                        },
                    }
                ],
                "roundConfig": {
                    "actionCardType": "individual",
                    "targetedYear": 2023,
                    "budget": 4,
                    "actionCardBatchIds": [
                        "actionCardId1",
                        "actionCardId2",
                        "actionCardId4",
                    ],
                },
            }
        ],
    }
    response = client.put(
        "/api/v1/workshops/{}".format(workshop.id),
        headers=headers,
        data=json.dumps(data),
    )

    assert response.status_code == 400


def test_put_workshop_invalid_participant_in_rounds_(
    client,
    auth,
    coach,
    workshop,
    model,
    action_cards,
    action_card_batches,
    participant,
    carbon_form_answers,
):
    headers = auth.login(email="coach@test.com")
    data = {
        "name": "workshop_name_bis",
        "startAt": "2020-01-01T22:00:00Z",
        "coachId": workshop.coachId,
        "city": Cities.PARIS.value,
        "address": "address_bis",
        "eventUrl": "http://www.example_bis.com",
        "startYear": 2020,
        "endYear": 2050,
        "yearIncrement": 3,
        "participants": [
            # {
            #     "id": participant.id,
            #     "firstName": "Participant First name",
            #     "lastName": "Participant Last name",
            #     "email": "participant@test.com",
            #     "status": "tocheck",
            #     "surveyVariables": {
            #         "meat_per_day": 9000,
            #         "car_type": "futuristic"
            #     }
            # }
        ],
        "rounds": [
            {
                "year": 2020,
                "carbonVariables": [
                    {
                        "participantId": "Wrong Id",
                        "variables": {
                            "hours_urban_train_per_week": 10,
                            "km_country_train": 5,
                            "km_plane": 200,
                        },
                    }
                ],
                "carbonFootprints": [
                    {
                        "participantId": participant.id,
                        "footprint": {
                            "transport": {
                                "plane": 1000,
                                "train": {"urbanTrain": 100, "mainlineTrain": 500},
                            }
                        },
                    }
                ],
                "roundConfig": {
                    "actionCardType": "individual",
                    "targetedYear": 2023,
                    "budget": 4,
                    "actionCardBatchIds": [
                        "actionCardId1",
                        "actionCardId2",
                        "actionCardId4",
                    ],
                },
            }
        ],
    }
    response = client.put(
        "/api/v1/workshops/{}".format(workshop.id),
        headers=headers,
        data=json.dumps(data),
    )

    assert response.status_code == 400
