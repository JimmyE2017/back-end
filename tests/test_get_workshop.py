import json

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
        },
    }
    assert status_code == 200
    assert response_data == expected_output
