"""Orquestra o envio de notificações (WhatsApp + email) e registra logs."""
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.appointment import Appointment
from app.models.studio import Studio
from app.models.notification_log import NotificationLog
from app.models.enums import (
    NotificationType,
    NotificationChannel,
    PaymentMode,
)
from app.services.zapi import zapi_service
from app.services.resend import resend_service


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


def action_urls(appt: Appointment) -> tuple[str, str, str]:
    base = f"{settings.FRONTEND_URL}/acao/{appt.action_token}"
    return f"{base}/confirmar", f"{base}/cancelar", f"{base}/remarcar"


def deposit_amount(appt: Appointment) -> float:
    total = float(appt.preco)
    if appt.payment_mode == PaymentMode.FULL_100:
        return total
    return round(total * 0.5, 2)


async def send_booking_confirmation(
    db: Session, appt: Appointment, studio: Studio, payment_link: str
):
    confirm, cancel, resched = action_urls(appt)
    date_str = appt.data.strftime("%d/%m/%Y")
    total = float(appt.preco)

    wa = await zapi_service.send_confirmation(
        appt.client_phone,
        appt.client_name,
        appt.servico_nome,
        date_str,
        appt.hora,
        total,
        confirm,
        cancel,
        resched,
        studio_name=studio.name,
        payment_link=payment_link,
    )
    _log(db, appt.id, NotificationType.WHATSAPP_CONFIRMATION, NotificationChannel.WHATSAPP, appt.client_phone, wa)

    em = await resend_service.send_confirmation(
        appt.client_email,
        appt.client_name,
        appt.servico_nome,
        date_str,
        appt.hora,
        total,
        deposit_amount(appt),
        payment_link,
    )
    _log(db, appt.id, NotificationType.EMAIL_CONFIRMATION, NotificationChannel.EMAIL, appt.client_email, em)
    db.commit()
