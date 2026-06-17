import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.core.database import SessionLocal
from app.models.appointment import Appointment
from app.models.notification_log import NotificationLog
from app.models.enums import (
    AppointmentStatus,
    NotificationType,
    NotificationChannel,
)
from app.services.zapi import zapi_service
from app.services.resend import resend_service
from app.services.notifications import action_urls
from app.tasks.celery_app import celery_app

TZ = ZoneInfo("America/Sao_Paulo")
ACTIVE = (AppointmentStatus.AGENDADO, AppointmentStatus.CONFIRMADO)


def _log(db, appt_id, ntype, channel, recipient, ok):
    db.add(
        NotificationLog(
            appointment_id=appt_id,
            type=ntype,
            channel=channel,
            recipient=recipient,
            success=ok,
        )
    )


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def send_reminder_24h(self, appointment_id: str):
    db = SessionLocal()
    try:
        appt = db.get(Appointment, uuid.UUID(appointment_id))
        if not appt or appt.status not in ACTIVE or appt.reminder_24h_sent:
            return
        studio = appt.studio
        confirm, cancel, _ = action_urls(appt)
        date_str = appt.data.strftime("%d/%m/%Y")

        wa = asyncio.run(
            zapi_service.send_reminder(
                appt.client_phone, appt.client_name, appt.servico_nome,
                date_str, appt.hora, 24, confirm, cancel, studio_name=studio.name,
            )
        )
        _log(db, appt.id, NotificationType.WHATSAPP_REMINDER_24H, NotificationChannel.WHATSAPP, appt.client_phone, wa)

        em = asyncio.run(
            resend_service.send_reminder(
                appt.client_email, appt.client_name, appt.servico_nome, date_str, appt.hora
            )
        )
        _log(db, appt.id, NotificationType.EMAIL_REMINDER, NotificationChannel.EMAIL, appt.client_email, em)

        appt.reminder_24h_sent = True
        db.commit()
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def send_reminder_2h(self, appointment_id: str):
    db = SessionLocal()
    try:
        appt = db.get(Appointment, uuid.UUID(appointment_id))
        if not appt or appt.status not in ACTIVE or appt.reminder_2h_sent:
            return
        if appt.confirmado_cliente_at is not None:
            return  # já confirmou presença
        studio = appt.studio
        confirm, cancel, _ = action_urls(appt)
        date_str = appt.data.strftime("%d/%m/%Y")

        wa = asyncio.run(
            zapi_service.send_reminder(
                appt.client_phone, appt.client_name, appt.servico_nome,
                date_str, appt.hora, 2, confirm, cancel, studio_name=studio.name,
            )
        )
        _log(db, appt.id, NotificationType.WHATSAPP_REMINDER_2H, NotificationChannel.WHATSAPP, appt.client_phone, wa)

        appt.reminder_2h_sent = True
        db.commit()
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()


def schedule_reminders(appt: Appointment) -> None:
    """Agenda lembretes 24h e 2h antes via Celery (eta)."""
    sched = appt.scheduled_at
    if sched.tzinfo is None:
        sched = sched.replace(tzinfo=TZ)
    now = datetime.now(timezone.utc)
    eta_24h = sched - timedelta(hours=24)
    eta_2h = sched - timedelta(hours=2)
    if eta_24h > now:
        send_reminder_24h.apply_async(args=[str(appt.id)], eta=eta_24h)
    if eta_2h > now:
        send_reminder_2h.apply_async(args=[str(appt.id)], eta=eta_2h)
