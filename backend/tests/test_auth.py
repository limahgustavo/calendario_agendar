from fastapi.testclient import TestClient


def test_health(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_admin_login(client: TestClient):
    resp = client.post(
        "/api/auth/login", json={"email": "admin@test.com", "password": "testpass123"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["role"] == "admin"


def test_login_wrong_password(client: TestClient):
    resp = client.post(
        "/api/auth/login", json={"email": "admin@test.com", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_register_client(client: TestClient):
    resp = client.post(
        "/api/auth/register",
        json={"name": "Cliente Teste", "email": "novo.cliente@test.com"},
    )
    assert resp.status_code == 200
    assert "link" in resp.json()["message"].lower()


def test_me_requires_auth(client: TestClient):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_admin(client: TestClient, admin_headers):
    resp = client.get("/api/auth/me", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


def test_plans_listed(client: TestClient):
    # planos só existem após seed; aqui garantimos que o endpoint responde
    resp = client.get("/api/plans")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
