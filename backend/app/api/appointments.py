import secrets
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.appointment import Appointment, AppointmentStatus
from app.models.availability import AvailabilitySlot
from app.models.payment import Payment, PaymentStatus
from app.models.notification_log import NotificationLog, NotificationType
from app.models.user import User
from app.models.service import Service
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentBookingResponse,
)
from app.services.asaas import asaas_service
from app.services.zapi import zapi_service
from app.services.resend import resend_service
from app.tasks.reminders import send_reminder_24h, send_reminder_2h

router = APIRouter(prefix="/appointments", tags=["appointments"])


def _schedule_reminders(appt: Appointment) -> None:
    """Schedule 24h and 2h reminder tasks via Celery."""
    scheduled = appt.scheduled_at
    reminder_24h_at = scheduled - timedelta(hours=24)
    reminder_2h_at = scheduled - timedelta(hours=2)

    now = datetime.now(timezone.utc)
    if reminder_24h_at > now:
        send_reminder_24h.apply_async(
            args=[appt.id],
            eta=reminder_24h_at,
        )
    if reminder_2h_at > now:
        send_reminder_2h.apply_async(
            args=[appt.id],
            eta=reminder_2h_at,
        )


def _log(db, appt, ntype, recipient, ok):
    db.add(NotificationLog(
        appointment_id=appt.id, type=ntype,
        recipient=recipient, success=ok,
    ))


async def _send_confirmation_notifications(appt: Appointment, payment_link: str, db: Session):
    confirm_url = f"{settings.FRONTEND_URL}/acao/{appt.action_token}/confirmar"
    cancel_url = f"{settings.FRONTEND_URL}/acao/{appt.action_token}/cancelar"
    reschedule_url = f"{settings.FRONTEND_URL}/acao/{appt.action_token}/remarcar"
    scheduled_date = appt.scheduled_at.strftime("%d/%m/%Y")
    scheduled_time = appt.scheduled_at.strftime("%H:%M")
    total = float(appt.service.price)
    deposit = round(total * 0.5, 2)

    wa_ok = await zapi_service.send_confirmation(
        appt.client_phone, appt.client_name, appt.service.name,
        scheduled_date, scheduled_time, total, confirm_url, cancel_url, reschedule_url,
    )
    _log(db, appt, NotificationType.WHATSAPP_CONFIRMATION, appt.client_phone, wa_ok)

    email_ok = await resend_service.send_confirmation(
        appt.client_email, appt.client_name, appt.service.name,
        scheduled_date, scheduled_time, total, deposit, payment_link,
    )
    _log(db, appt, NotificationType.EMAIL_CONFIRMATION, appt.client_email, email_ok)
    db.commit()


@router.post("", response_model=AppointmentBookingResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    service = db.get(Service, data.service_id)
    if not service or not service.is_active:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    # Validate slot exists
    month_year = data.scheduled_at.strftime("%Y-%m")
    weekday = data.scheduled_at.weekday()
    time_str = data.scheduled_at.strftime("%H:%M")

    slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.month_year == month_year,
        AvailabilitySlot.weekday == weekday,
        AvailabilitySlot.time_str == time_str,
    ).first()
    if not slot:
        raise HTTPException(status_code=400, detail="Horário não disponível")

    # Check no conflicting appointment
    conflict = db.query(Appointment).filter(
        Appointment.scheduled_at == data.scheduled_at,
        Appointment.status.in_([
            AppointmentStatus.PENDING_PAYMENT,
            AppointmentStatus.CONFIRMED,
        ]),
    ).first()
    if conflict:
        raise HTTPException(status_code=409, detail="Horário já ocupado")

    # Get professional (first active user)
    professional = db.query(User).filter(User.is_active == True).first()

    action_token = secrets.token_urlsafe(32)
    appt = Appointment(
        professional_id=professional.id,
        service_id=service.id,
        client_name=data.client_name,
        client_email=data.client_email,
        client_phone=data.client_phone,
        scheduled_at=data.scheduled_at,
        notes=data.notes,
        action_token=action_token,
    )
    db.add(appt)
    db.flush()

    # Create Asaas charge
    deposit = round(float(service.price) * 0.5, 2)
    due_date = data.scheduled_at.strftime("%Y-%m-%d")
    description = f"Sinal - {service.name} em {data.scheduled_at.strftime('%d/%m/%Y')}"

    try:
        customer_id = await asaas_service.find_or_create_customer(
            data.client_name, data.client_email, data.client_phone
        )
        charge = await asaas_service.create_charge(customer_id, deposit, description, due_date)
        payment_link = charge["asaas_payment_link"] or charge["asaas_invoice_url"]
    except Exception:
        payment_link = f"{settings.FRONTEND_URL}/pagamento-pendente"
        charge = {"asaas_payment_id": None, "asaas_payment_link": payment_link, "asaas_invoice_url": None}

    payment = Payment(
        appointment_id=appt.id,
        amount=deposit,
        asaas_payment_id=charge.get("asaas_payment_id"),
        asaas_payment_link=charge.get("asaas_payment_link"),
        asaas_invoice_url=charge.get("asaas_invoice_url"),
    )
    db.add(payment)
    db.commit()
    db.refresh(appt)

    await _send_confirmation_notifications(appt, payment_link, db)
    _schedule_reminders(appt)

    return AppointmentBookingResponse(
        appointment_id=appt.id,
        payment_link=payment_link,
        message="Agendamento criado! Finalize o pagamento do sinal para confirmar.",
    )


@router.post("/{token}/confirmar")
def confirm_by_token(token: str, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.action_token == token).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    appt.client_confirmed_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Agendamento confirmado!"}


@router.post("/{token}/cancelar")
def cancel_by_token(token: str, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.action_token == token).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    if appt.status == AppointmentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Não é possível cancelar agendamento concluído")
    appt.status = AppointmentStatus.CANCELLED
    db.commit()
    return {"message": "Agendamento cancelado."}


@router.post("/{token}/remarcar")
def reschedule_by_token(token: str, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.action_token == token).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    appt.status = AppointmentStatus.RESCHEDULED
    db.commit()
    return {"message": "Solicitação de remarcação enviada. Entraremos em contato."}


# Admin routes
@router.get("", response_model=list[AppointmentResponse])
def list_appointments(
    status_filter: AppointmentStatus | None = Query(None, alias="status"),
    month_year: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Appointment)
    if status_filter:
        q = q.filter(Appointment.status == status_filter)
    if month_year:
        year, month = int(month_year[:4]), int(month_year[5:])
        from datetime import date
        from calendar import monthrange
        _, days = monthrange(year, month)
        q = q.filter(
            Appointment.scheduled_at >= datetime(year, month, 1),
            Appointment.scheduled_at <= datetime(year, month, days, 23, 59, 59),
        )
    return q.order_by(Appointment.scheduled_at).all()


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(appt, field, value)
    db.commit()
    db.refresh(appt)
    return appt
