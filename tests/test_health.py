import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    # Entering the context runs FastAPI lifespan startup,
    # including database table initialization.
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "openaiops-api"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_database_readiness(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_create_and_read_event(client):
    payload = {
        "event_type": "lab_checkpoint",
        "message": "PostgreSQL integration test",
    }

    created = client.post("/events", json=payload)
    assert created.status_code == 201

    created_event = created.json()
    assert created_event["event_type"] == payload["event_type"]
    assert created_event["message"] == payload["message"]

    listed = client.get("/events")
    assert listed.status_code == 200
    assert any(
        event["id"] == created_event["id"]
        for event in listed.json()
    )
