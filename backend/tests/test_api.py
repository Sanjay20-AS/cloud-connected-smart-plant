import os
os.environ["DATABASE_URL"] = "sqlite:///./test_smartplant.db"
os.environ["DEVICE_API_KEY"] = "test-device-key"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "change-me"

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def login():
    response = client.post("/auth/login", json={"username": "admin", "password": "change-me"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health():
    response = client.get("/healthz")
    assert response.status_code == 200


def test_login():
    token = login()
    assert token


def test_sensor_ingestion_and_automatic_watering():
    response = client.post(
        "/api/v1/readings",
        headers={"X-Device-Key": "test-device-key"},
        json={
            "device_id": "test-plant",
            "soil_moisture": 15,
            "temperature": 28,
            "humidity": 55,
            "light": 500,
        },
    )
    assert response.status_code == 200

    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    events = client.get("/api/v1/watering-events", headers=headers)
    assert events.status_code == 200
    assert len(events.json()) >= 1
