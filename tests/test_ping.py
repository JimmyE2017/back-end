import json


def test_ping(client):
    response = client.get("/api/ping")
    assert json.loads(response.data) == {"data": "pong"}
    assert response.status_code == 200
