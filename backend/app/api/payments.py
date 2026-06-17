import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.user import User
from app.models.enums import AppointmentStatus, PaymentStatus, UserRole
from app.services.comprovante import gerar_comprovante

router = APIRouter(prefix="/payments", tags=["payments"])

CONFIRMED_EVENTS = {"PAYMENT_CONFIRMED", "PAYMENT_RECEIVED", "RECEIVED"}
FAILED_EVENTS = {"PAYMENT_OVERDUE", "PAYMENT_DELETED"}


@router.post("/webhook/asaas")
async def asaas_webhook(
    request: Request,
    db: Session = Depends(get_db),
    asaas_access_token: str = Header(None, alias="asaas-access-token"),
):
    if settings.ASAAS_WEBHOOK_TOKEN and asaas_access_token != settings.ASAAS_WEBHOOK_TOKEN:
        raise HTTPException(status_code=403, detail="Token inválido")

    body = await request.json()
    event = body.get("event")
    payment_data = body.get("payment", {})
    asaas_payment_id = payment_data.get("id")
    if not asaas_payment_id:
        return {"ok": True}

    payment = db.query(Payment).filter(Payment.asaas_payment_id == asaas_payment_id).first()
    if not payment:
        return {"ok": True}

    appt = db.get(Appointment, payment.appointment_id)

    if event in CONFIRMED_EVENTS:
        payment.status = PaymentStatus.CONFIRMED
        payment.paid_at = datetime.now(timezone.utc)
        if appt:
            appt.valor_pago = float(appt.valor_pago or 0) + float(payment.valor)
            if appt.status == AppointmentStatus.AGENDADO:
                appt.status = AppointmentStatus.CONFIRMADO
        db.commit()
    elif event in FAILED_EVENTS:
        payment.status = PaymentStatus.FAILED
        db.commit()
    elif event == "PAYMENT_REFUNDED":
        payment.status = PaymentStatus.REFUNDED
        db.commit()

    return {"ok": True}


@router.get("/{appointment_id}/comprovante")
def comprovante(
    appointment_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    studio = appt.studio
    allowed = (
        user.role == UserRole.ADMIN
        or appt.cliente_id == user.id
        or (studio and studio.owner_id == user.id)
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="Acesso negado")

    payment = appt.payment
    if not payment or payment.status != PaymentStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Pagamento ainda não confirmado")

    pdf = gerar_comprovante(appt, studio, payment)
    return StreamingResponse(
        iter([pdf]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=comprovante-{appointment_id}.pdf"},
    )
