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
        "yearIncrement": workshop.yearIncrement,
        "participants": [
            {
                "status": WorkshopParticipantStatus.TOCHECK.value,
                "email": participant.email,
                "firstName": participant.firstName,
                "lastName": participant.lastName,
                "participantId": participant.userId,
                "surveyVariables": carbon_form_answers.answers,
            }
        ],
        "model": {
            "modelId": model.id,
            "globalCarbonVariables": model.globalCarbonVariables,
            "variableFormulas": model.variableFormulas,
            "footprintStructure": model.footprintStructure,
            "actionCards": [
                {
                    "actionCardId": action_card.actionCardId,
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
                    "actionCardBatchId": action_card_batch.actionCardBatchId,
                    "name": action_card_batch.name,
                    "type": action_card_batch.type,
                    "actionCardIds": [ac.pk for ac in action_card_batch.actionCards],
                }
                for action_card_batch in action_card_batches
            ],
            "personas": [
                {
                    "personaId": persona.id,
                    "firstName": persona.firstName,
                    "lastName": persona.lastName,
                    "description": persona.description,
                    "surveyVariables": persona.carbonFormAnswers,
                }
                for persona in personas
            ],
        },
        "rounds": [
            {
                "year": workshop_round.year,
                "carbonVariables": [
                    {"participantId": cv.participant.pk, "variables": cv.variables}
                    for cv in workshop_round.carbonVariables
                ],
                "carbonFootprints": [
                    {"participantId": cf.participant.pk, "footprint": cf.footprint}
                    for cf in workshop_round.carbonFootprints
                ],
                "roundConfig": {
                    "actionCardType": workshop_round.roundConfig.actionCardType,
                    "targetedYear": workshop_round.roundConfig.targetedYear,
                    "budget": workshop_round.roundConfig.budget,
                    "actionCardBatchIds": [
                        acb.pk for acb in workshop_round.roundConfig.actionCardBatches
                    ],
                },
                "globalCarbonVariables": workshop_round.globalCarbonVariables,
                # Using short hand statement
                # since collectiveChoices / indivudalChoices are alternating
                "collectiveChoices"
                if workshop_round.collectiveChoices is not None
                else "individualChoices": {
                    "actionCardIds": [
                        ac.pk for ac in workshop_round.collectiveChoices.actionCards
                    ]
                }
                if workshop_round.collectiveChoices is not None
                else [
                    {
                        "participantId": ic.participant.pk,
                        "actionCardIds": [ac.pk for ac in ic.actionCards],
                    }
                    for ic in workshop_round.individualChoices
                ],
            }
            for workshop_round in workshop.rounds
        ],
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
                "carbonVariables": [{"participantId": participant.id, "variables": {}}],
                "carbonFootprints": [
                    {"participantId": participant.id, "footprint": {}}
                ],
                "roundConfig": {
                    "actionCardType": "individual",
                    "targetedYear": 2023,
                    "budget": 4,
                    "actionCardBatchIds": [action_card_batches[0].pk],
                },
                "globalCarbonVariables": {},
                "individualChoices": [
                    {
                        "participantId": participant.id,
                        "actionCardIds": [action_card_batches[0].actionCards[0].pk],
                    }
                ],
            },
            {
                "year": 2023,
                "carbonVariables": [{"participantId": participant.id, "variables": {}}],
                "carbonFootprints": [
                    {"participantId": participant.id, "footprint": {}}
                ],
                "roundConfig": {
                    "actionCardType": "collective",
                    "targetedYear": 2026,
                    "budget": 4,
                    "actionCardBatchIds": [action_card_batches[1].pk],
                },
                "globalCarbonVariables": {},
                "collectiveChoices": {
                    "actionCardIds": [action_card_batches[1].actionCards[0].pk]
                },
            },
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
        # Assert individualChoices is updated
        if "individualChoices" in round_data:
            assert workshop_round.individualChoices is not None
            for individual_choices_data in round_data["individualChoices"]:
                individual_choices = [
                    x
                    for x in workshop_round.individualChoices
                    if x.participant.pk == individual_choices_data["participantId"]
                ]
                assert (
                    len(individual_choices) == 1
                )  # Assert existance of indivualChoicesModel for given participant
                individual_choices = individual_choices[0]
                for action_card_id in individual_choices_data["actionCardIds"]:
                    assert action_card_id in [
                        ac.pk for ac in individual_choices.actionCards
                    ]
        # Assert collectiveChoices is updated
        if "collectiveChoices" in round_data:
            assert workshop_round.collectiveChoices is not None

            for action_card_id in round_data["collectiveChoices"]["actionCardIds"]:
                assert action_card_id in [
                    ac.pk for ac in workshop_round.collectiveChoices.actionCards
                ]


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
