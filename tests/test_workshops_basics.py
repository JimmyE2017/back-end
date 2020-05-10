import json
from datetime import datetime, timedelta

import pytest
from mongoengine import DoesNotExist

from app.common.errors import EmptyBodyError, EntityNotFoundError
from app.models.model_model import Model
from app.models.workshop_model import WorkshopModel


@pytest.fixture(scope="function")
def invalid_workshops_data(init_coach):
    invalid_data = [
        dict(  # Missing fields
            startAt="2020-01-01T01:01:01+01:00",
            city="Paris",
            eventUrl="http://www.example.com",
            coachId=init_coach.id,
        ),
        dict(  # Invalid date format
            name="Atelier Data 4 Good",
            startAt="Invalid date format",
            city="Paris",
            address="Avenue Champ Elysee",
            eventUrl="http://www.example.com",
            coachId=init_coach.id,
        ),
        dict(  # inexisting coach id
            name="Atelier Data 4 Good",
            startAt="2020-01-01T01:01:01+01:00",
            city="Paris",
            address="Avenue Champ Elysee",
            eventUrl="http://www.example.com",
            coachId="inexisting_id",
        ),
    ]
    return invalid_data


@pytest.fixture(scope="function")
def create_some_workshops(db, request, init_coach):
    workshop1 = WorkshopModel(
        name="workshop_name_1",
        startAt=datetime(2020, 1, 1, 1, 1, 1),
        city="city_1",
        address="address1",
        eventUrl="http://www.example1.com",
        coachId=init_coach.id,
        creatorId=init_coach.id,
        model=None,
    )
    workshop2 = WorkshopModel(
        name="workshop_name_2",
        startAt=datetime(2020, 2, 2, 2, 2, 2),
        city="city_2",
        address="address2",
        eventUrl="http://www.example2.com",
        coachId=init_coach.id,
        creatorId=init_coach.id,
        model=None,
    )

    workshop1.save()
    workshop2.save()

    def teardown():
        workshop1.delete()
        workshop2.delete()

    request.addfinalizer(teardown)

    return workshop1, workshop2


def test_get_workshops(client, auth, init_admin, create_some_workshops):
    workshop1, workshop2 = create_some_workshops
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


def test_delete_workshop(client, auth, init_admin, request):
    workshop = WorkshopModel(
        name="Atelier Data 4 Good",
        startAt=datetime(2020, 4, 4, 1, 1, 1),
        city="Paris",
        address="Avenue Champ Elysee",
        eventUrl="http://www.example.com",
        coachId=init_admin.id,
        creatorId=init_admin.id,
        model=None,
    )
    workshop.save()

    headers = auth.login(email="admin@test.com")
    response = client.delete(f"/api/v1/workshops/{workshop.id}", headers=headers)

    assert response.status_code == 204
    assert WorkshopModel.find_by_id(workshop.id) is None

    def teardown():
        workshop.delete()

    request.addfinalizer(teardown)


def test_delete_inexisting_workshop(client, auth, init_admin):
    headers = auth.login(email="admin@test.com")
    response = client.delete(f"/api/v1/workshops/inexistingId", headers=headers)

    response_data, status_code = json.loads(response.data), response.status_code
    assert status_code == EntityNotFoundError.code
    assert response_data == EntityNotFoundError().get_content()


def test_get_inexisting_workshop(client, auth, init_admin):
    headers = auth.login(email="admin@test.com")

    response = client.get("/api/v1/workshops/inexistingId", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code
    assert status_code == EntityNotFoundError.code
    assert response_data == EntityNotFoundError().get_content()


def test_post_workshop_success(client, auth, init_admin, init_coach, request):
    model = Model(
        footprintStructure={"var1": "var1"},
        globalCarbonVariables={"var1": "var1"},
        variableFormulas={"var1": "var1"},
        createdAt=datetime.utcnow(),
    )
    model.save()

    data = dict(
        name="Atelier Data 4 Good",
        startAt="2020-01-01T01:01:01+01:00",
        city="Paris",
        address="Avenue Champ Elysee",
        eventUrl="http://www.example.com",
        coachId=init_coach.id,
    )

    headers = auth.login(email="admin@test.com")
    response = client.post("/api/v1/workshops", headers=headers, data=json.dumps(data))

    response_data, status_code = json.loads(response.data), response.status_code
    assert status_code == 200
    assert len(WorkshopModel.objects()) == 1

    def teardown():
        workshop = WorkshopModel.find_by_id(response_data["id"])
        workshop.delete()
        model.delete()

    request.addfinalizer(teardown)


def test_post_workshops_with_invalid_data(
    client, auth, init_admin, invalid_workshops_data
):
    headers = auth.login(email="admin@test.com")

    for data in invalid_workshops_data:

        response = client.post(
            "/api/v1/workshops", headers=headers, data=json.dumps(data)
        )

        assert response.status_code == 400
        assert len(WorkshopModel.objects()) == 0


def test_post_workshops_with_empty_body(client, auth, init_admin):
    headers = auth.login(email="admin@test.com")

    response = client.post("/api/v1/workshops", headers=headers)
    response_data, status_code = json.loads(response.data), response.status_code

    assert response_data == EmptyBodyError().get_content()
    assert status_code == EmptyBodyError.code


def test_post_workshops_but_no_model_in_db(client, auth, init_admin):
    data = dict(
        name="Atelier Data 4 Good",
        startAt="2020-01-01T01:01:01+01:00",
        city="Paris",
        address="Avenue Champ Elysee",
        eventUrl="http://www.example.com",
        coachId=init_admin.id,
    )

    headers = auth.login(email="admin@test.com")
    with pytest.raises(DoesNotExist):
        assert client.post("/api/v1/workshops", headers=headers, data=json.dumps(data))


def test_last_created_model_at_workshop_creation(client, auth, init_admin, request):
    model1 = Model(
        footprintStructure={"var1": "var1"},
        globalCarbonVariables={"var1": "var1"},
        variableFormulas={"var1": "var1"},
        createdAt=datetime.utcnow(),
    )

    model2 = Model(
        footprintStructure={"var1": "var1"},
        globalCarbonVariables={"var1": "var1"},
        variableFormulas={"var1": "var1"},
        createdAt=datetime.utcnow() + timedelta(days=1),
    )

    model1.save()
    model2.save()

    data = dict(
        name="Atelier Data 4 Good",
        startAt="2020-01-01T01:01:01+01:00",
        city="Paris",
        address="Avenue Champ Elysee",
        eventUrl="http://www.example.com",
        coachId=init_admin.id,
    )

    headers = auth.login(email="admin@test.com")
    response = client.post("/api/v1/workshops", headers=headers, data=json.dumps(data))

    workshop = WorkshopModel.find_by_id(json.loads(response.data)["id"])

    assert workshop.model.id == model2.id

    def teardown():
        workshop.delete()
        model1.delete()
        model2.delete()

    request.addfinalizer(teardown)
