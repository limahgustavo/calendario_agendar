import asyncio
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.appointment import Appointment, AppointmentStatus
from app.models.notification_log import NotificationLog, NotificationType
from app.services.zapi import zapi_service
from app.services.resend import resend_service
from app.core.config import settings


def _build_action_urls(appointment: Appointment) -> tuple[str, str, str]:
    base = settings.FRONTEND_URL
    token = appointment.action_token
    return (
        f"{base}/acao/{token}/confirmar",
        f"{base}/acao/{token}/cancelar",
        f"{base}/acao/{token}/remarcar",
    )


def _log_notification(
    db,
    appointment: Appointment,
    ntype: NotificationType,
    recipient: str,
    success: bool,
    error: str | None = None,
) -> None:
    log = NotificationLog(
        appointment_id=appointment.id,
        type=ntype,
        recipient=recipient,
        success=success,
        error_message=error,
    )
    db.add(log)
    db.commit()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def send_reminder_24h(self, appointment_id: int):
    db = SessionLocal()
    try:
        appt = db.get(Appointment, appointment_id)
        if not appt or appt.status not in (
            AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING_PAYMENT
        ):
            return

        if appt.reminder_24h_sent:
            return

        confirm_url, cancel_url, reschedule_url = _build_action_urls(appt)
        scheduled_date = appt.scheduled_at.strftime("%d/%m/%Y")
        scheduled_time = appt.scheduled_at.strftime("%H:%M")

        wa_ok = asyncio.run(
            zapi_service.send_reminder(
                appt.client_phone,
                appt.client_name,
                appt.service.name,
                scheduled_date,
                scheduled_time,
                hours_before=24,
                confirm_url=confirm_url,
                cancel_url=cancel_url,
            )
        )
        _log_notification(db, appt, NotificationType.WHATSAPP_REMINDER_24H, appt.client_phone, wa_ok)

        email_ok = asyncio.run(
            resend_service.send_reminder(
                appt.client_email,
                appt.client_name,
                appt.service.name,
                scheduled_date,
                scheduled_time,
            )
        )
        _log_notification(db, appt, NotificationType.EMAIL_REMINDER, appt.client_email, email_ok)

        appt.reminder_24h_sent = True
        db.commit()
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def send_reminder_2h(self, appointment_id: int):
    db = SessionLocal()
    try:
        appt = db.get(Appointment, appointment_id)
        if not appt or appt.status not in (
            AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING_PAYMENT
        ):
            return

        if appt.reminder_2h_sent:
            return

        # Skip if client already confirmed
        if appt.client_confirmed_at:
            return

        confirm_url, cancel_url, _ = _build_action_urls(appt)
        scheduled_date = appt.scheduled_at.strftime("%d/%m/%Y")
        scheduled_time = appt.scheduled_at.strftime("%H:%M")

        wa_ok = asyncio.run(
            zapi_service.send_reminder(
                appt.client_phone,
                appt.client_name,
                appt.service.name,
                scheduled_date,
                scheduled_time,
                hours_before=2,
                confirm_url=confirm_url,
                cancel_url=cancel_url,
            )
        )
        _log_notification(db, appt, NotificationType.WHATSAPP_REMINDER_2H, appt.client_phone, wa_ok)

        appt.reminder_2h_sent = True
        db.commit()
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()
