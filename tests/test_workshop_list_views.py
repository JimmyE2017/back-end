import json

import pytest
from mongoengine import DoesNotExist

from app.common.errors import EmptyBodyError, EntityNotFoundError
from app.models.workshop_model import WorkshopModel


def test_get_workshops(client, auth, admin, workshops):
    workshop1, workshop2 = workshops[0], workshops[1]
    headers = auth.login(email="admin@test.com")

    response = client.get("/api/v1/workshops", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    expected_output = [
        dict(
            name=workshop1.name,
            startAt=workshop1.startAt.isoformat(),
            city=workshop1.city,
            address=workshop1.address,
            eventUrl=workshop1.eventUrl,
            coachId=workshop1.coachId,
            creatorId=workshop1.creatorId,
            id=workshop1.id,
        ),
        dict(
            name=workshop2.name,
            startAt=workshop2.startAt.isoformat(),
            city=workshop2.city,
            address=workshop2.address,
            eventUrl=workshop2.eventUrl,
            coachId=workshop2.coachId,
            creatorId=workshop2.creatorId,
            id=workshop2.id,
        ),
    ]
    assert status_code == 200
    assert expected_output == response_data


def test_delete_workshop(client, auth, admin, request, workshops):
    workshop = workshops[0]

    headers = auth.login(email="admin@test.com")
    response = client.delete(f"/api/v1/workshops/{workshop.id}", headers=headers)

    assert response.status_code == 204
    assert WorkshopModel.find_by_id(workshop.id) is None


def test_delete_inexisting_workshop(client, auth, admin):
    headers = auth.login(email="admin@test.com")
    response = client.delete(f"/api/v1/workshops/inexistingId", headers=headers)

    response_data, status_code = json.loads(response.data), response.status_code
    assert status_code == EntityNotFoundError.code
    assert response_data == EntityNotFoundError().get_content()


def test_get_inexisting_workshop(client, auth, admin):
    headers = auth.login(email="admin@test.com")

    response = client.get("/api/v1/workshops/inexistingId", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code
    assert status_code == EntityNotFoundError.code
    assert response_data == EntityNotFoundError().get_content()


def test_post_workshop_success(client, auth, admin, coach, model, request):

    data = dict(
        name="Atelier Data 4 Good",
        startAt="2020-01-01T01:01:01+01:00",
        city="Paris",
        address="Avenue Champ Elysee",
        eventUrl="http://www.example.com",
        coachId=coach.id,
    )

    headers = auth.login(email="admin@test.com")
    response = client.post("/api/v1/workshops", headers=headers, data=json.dumps(data))

    response_data, status_code = json.loads(response.data), response.status_code
    assert status_code == 200
    assert len(WorkshopModel.objects()) == 1

    def teardown():
        workshop = WorkshopModel.find_by_id(response_data["id"])
        workshop.delete()

    request.addfinalizer(teardown)


def test_post_workshops_with_inexisting_coach(client, auth, admin):
    headers = auth.login(email="admin@test.com")

    data = dict(  # inexisting coach id
        name="Atelier Data 4 Good",
        startAt="2020-01-01T01:01:01+01:00",
        city="Paris",
        address="Avenue Champ Elysee",
        eventUrl="http://www.example.com",
        coachId="inexisting_id",
    )

    response = client.post("/api/v1/workshops", headers=headers, data=json.dumps(data))

    assert response.status_code == 400
    assert len(WorkshopModel.objects()) == 0


def test_post_workshops_with_empty_body(client, auth, admin):
    headers = auth.login(email="admin@test.com")

    response = client.post("/api/v1/workshops", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    assert response_data == EmptyBodyError().get_content()
    assert status_code == EmptyBodyError.code


def test_post_workshops_but_no_model_in_db(client, auth, admin):
    data = dict(
        name="Atelier Data 4 Good",
        startAt="2020-01-01T01:01:01+01:00",
        city="Paris",
        address="Avenue Champ Elysee",
        eventUrl="http://www.example.com",
        coachId=admin.id,
    )

    headers = auth.login(email="admin@test.com")
    with pytest.raises(DoesNotExist):
        assert client.post("/api/v1/workshops", headers=headers, data=json.dumps(data))


def test_last_created_model_at_workshop_creation(client, auth, admin, models, request):

    data = dict(
        name="Atelier Data 4 Good",
        startAt="2020-01-01T01:01:01+01:00",
        city="Paris",
        address="Avenue Champ Elysee",
        eventUrl="http://www.example.com",
        coachId=admin.id,
    )

    headers = auth.login(email="admin@test.com")
    response = client.post("/api/v1/workshops", headers=headers, data=json.dumps(data))

    workshop = WorkshopModel.find_by_id(json.loads(response.data)["id"])

    assert workshop.model.id == models[1].id

    def teardown():
        workshop.delete()

    request.addfinalizer(teardown)
