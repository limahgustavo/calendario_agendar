from fastapi.testclient import TestClient

from tests.conftest import TestingSessionLocal
from app.models.auth_token import AuthToken
from app.models.user import User


def _designer_token(client: TestClient) -> tuple[str, str]:
    """Registra um studio, define a senha e retorna (token_jwt, slug)."""
    r = client.post(
        "/api/studios/register",
        json={
            "designer_name": "Ana",
            "email": "ana.designer@test.com",
            "whatsapp": "11988887777",
            "studio_name": "Ana Studio Teste",
        },
    )
    assert r.status_code == 200, r.text
    slug = r.json()["slug"]

    db = TestingSessionLocal()
    at = (
        db.query(AuthToken)
        .join(User, User.id == AuthToken.user_id)
        .filter(User.email == "ana.designer@test.com")
        .order_by(AuthToken.created_at.desc())
        .first()
    )
    raw = at.token
    db.close()

    r = client.post("/api/auth/set-password", json={"token": raw, "password": "senha123"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"], slug


def test_studio_booking_flow(client: TestClient, monkeypatch):
    token, slug = _designer_token(client)
    h = {"Authorization": f"Bearer {token}"}

    # serviço
    r = client.post(
        "/api/services",
        json={"name": "Fibra", "categoria": "aplicacao", "price": 130.0, "duration_minutes": 90},
        headers=h,
    )
    assert r.status_code == 201, r.text
    service_id = r.json()["id"]

    # disponibilidade (julho/2026, seg-sex, 08h e 13h)
    r = client.post(
        "/api/availability",
        json={"ano": 2026, "mes": 7, "dias_semana": [0, 1, 2, 3, 4], "horarios": ["08:00", "13:00"]},
        headers=h,
    )
    assert r.status_code == 200, r.text

    # calendário público
    r = client.get(f"/api/availability/{slug}/calendar?month=2026-07")
    assert r.status_code == 200
    assert len(r.json()) > 0

    # mock do Asaas (sem rede)
    async def fake_customer(*a, **k):
        return "cus_test"

    async def fake_charge(*a, **k):
        return {"asaas_payment_id": "pay_test", "asaas_invoice_url": "http://pay.test"}

    monkeypatch.setattr("app.api.appointments.asaas_service.find_or_create_customer", fake_customer)
    monkeypatch.setattr("app.api.appointments.asaas_service.create_charge", fake_charge)

    booking = {
        "service_id": service_id,
        "data": "2026-07-01",
        "hora": "08:00",
        "client_name": "Joana",
        "client_email": "joana@test.com",
        "client_phone": "11999998888",
        "client_cpf_cnpj": "24971563792",
    }
    r = client.post(f"/api/appointments/{slug}", json=booking)
    assert r.status_code == 201, r.text
    assert r.json()["amount"] == 65.0  # payment_mode default = deposit_50 → 50% de 130

    # mesmo horário agora está ocupado
    r2 = client.post(f"/api/appointments/{slug}", json=booking)
    assert r2.status_code == 409

    # horário fora da disponibilidade
    bad = {**booking, "hora": "20:00"}
    r3 = client.post(f"/api/appointments/{slug}", json=bad)
    assert r3.status_code == 400


def test_booking_unknown_studio(client: TestClient):
    r = client.post(
        "/api/appointments/studio-inexistente",
        json={
            "service_id": "00000000-0000-0000-0000-000000000000",
            "data": "2026-07-01",
            "hora": "08:00",
            "client_name": "Cliente X",
            "client_email": "x@test.com",
            "client_phone": "11999998888",
        },
    )
    assert r.status_code == 404
