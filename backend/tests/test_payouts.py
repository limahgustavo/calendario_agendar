from datetime import datetime, timezone, date

from tests.conftest import TestingSessionLocal
from app.models.user import User
from app.models.studio import Studio
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.payout import Payout
from app.models.enums import (
    UserRole,
    PaymentStatus,
    PaymentType,
    AppointmentStatus,
    PaymentMode,
    ServiceCategory,
)
from app.services.payouts import generate_payouts_for_week


def test_payout_calculation():
    db = TestingSessionLocal()

    owner = User(
        name="Dona Repasse",
        email="payout.designer@test.com",
        role=UserRole.NAIL_DESIGNER,
        email_verified=True,
    )
    db.add(owner)
    db.flush()

    studio = Studio(owner_id=owner.id, name="Payout Studio", slug="payout-studio")
    db.add(studio)
    db.flush()
    studio_id = studio.id  # captura antes do commit (evita expire/detach)

    svc = Service(
        studio_id=studio.id, name="Serviço", price=200, categoria=ServiceCategory.APLICACAO
    )
    db.add(svc)
    db.flush()

    appt = Appointment(
        studio_id=studio.id,
        service_id=svc.id,
        servico_nome="Serviço",
        preco=200,
        payment_mode=PaymentMode.FULL_100,
        data=date.today(),
        hora="08:00",
        scheduled_at=datetime.now(),
        status=AppointmentStatus.CONFIRMADO,
        client_name="Cliente",
        client_email="cliente.payout@test.com",
        client_phone="11999990000",
        action_token="token-payout-test-1",
    )
    db.add(appt)
    db.flush()

    pay = Payment(
        appointment_id=appt.id,
        valor=200,
        tipo=PaymentType.FULL,
        status=PaymentStatus.CONFIRMED,
        paid_at=datetime.now(timezone.utc),
    )
    db.add(pay)
    db.commit()

    generate_payouts_for_week(db)
    db.close()

    db2 = TestingSessionLocal()
    payout = db2.query(Payout).filter(Payout.studio_id == studio_id).first()
    db2.close()

    assert payout is not None
    assert float(payout.valor_bruto) == 200.0
    assert float(payout.taxa_admin_pct) == 20.0
    assert float(payout.taxa_admin_valor) == 40.0
    assert float(payout.valor_liquido) == 160.0
