from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.appointment import Appointment, AppointmentStatus
from app.models.payment import Payment, PaymentStatus

router = APIRouter(prefix="/payments", tags=["payments"])

CONFIRMED_EVENTS = {"PAYMENT_CONFIRMED", "RECEIVED"}


@router.post("/webhook/asaas")
async def asaas_webhook(
    request: Request,
    db: Session = Depends(get_db),
    asaas_access_token: str = Header(None, alias="asaas-access-token"),
):
    # Validate webhook token
    if asaas_access_token != settings.ASAAS_WEBHOOK_TOKEN:
        raise HTTPException(status_code=403, detail="Token inválido")

    body = await request.json()
    event = body.get("event")
    payment_data = body.get("payment", {})
    asaas_payment_id = payment_data.get("id")

    if not asaas_payment_id:
        return {"ok": True}

    payment = db.query(Payment).filter(
        Payment.asaas_payment_id == asaas_payment_id
    ).first()

    if not payment:
        return {"ok": True}

    if event in CONFIRMED_EVENTS:
        payment.status = PaymentStatus.CONFIRMED
        payment.confirmed_at = datetime.now(timezone.utc)
        appt = db.get(Appointment, payment.appointment_id)
        if appt and appt.status == AppointmentStatus.PENDING_PAYMENT:
            appt.status = AppointmentStatus.CONFIRMED
        db.commit()
    elif event in {"PAYMENT_OVERDUE", "PAYMENT_DELETED"}:
        payment.status = PaymentStatus.FAILED
        db.commit()
    elif event == "PAYMENT_REFUNDED":
        payment.status = PaymentStatus.REFUNDED
        db.commit()

    return {"ok": True}
