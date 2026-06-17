from fastapi.testclient import TestClient


def test_health(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_login(client: TestClient):
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "testpass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client: TestClient):
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "wrong"})
    assert resp.status_code == 401


def test_list_services_empty(client: TestClient):
    resp = client.get("/api/services")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_service(client: TestClient, auth_headers):
    resp = client.post(
        "/api/services",
        json={"name": "Fibra", "price": 130.0, "duration_minutes": 90},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Fibra"
    assert data["price"] == 130.0


def test_create_service_unauthorized(client: TestClient):
    resp = client.post(
        "/api/services",
        json={"name": "Gel", "price": 90.0},
    )
    assert resp.status_code == 401


def test_calendar_empty(client: TestClient):
    resp = client.get("/api/availability/calendar?month_year=2026-12")
    assert resp.status_code == 200
    assert resp.json() == []
