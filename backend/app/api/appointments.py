import logging
import secrets
import uuid
from datetime import datetime, time, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.api.deps import get_current_studio
from app.models.user import User
from app.models.studio import Studio
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.notification_log import NotificationLog
from app.models.enums import (
    AppointmentStatus,
    PaymentMode,
    PaymentType,
    PaymentStatus,
    UserRole,
    AuthTokenType,
    NotificationType,
    NotificationChannel,
)
from app.schemas.appointment import (
    BookingCreate,
    ManualBookingCreate,
    BookingResponse,
    AppointmentUpdate,
    AppointmentResponse,
    PaymentInfo,
    RatingRequest,
)
from app.services.asaas import asaas_service
from app.services.zapi import zapi_service
from app.services.calendar import is_slot_configured, is_slot_free
from app.services.notifications import send_booking_confirmation
from app.services.plans import check_plan_limit
from app.services.tokens import create_auth_token
from app.services.resend import resend_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/appointments", tags=["appointments"])


# ---------- helpers ----------
def _to_response(appt: Appointment, studio_name: str | None = None) -> AppointmentResponse:
    pay = appt.payment
    return AppointmentResponse(
        id=appt.id,
        studio_id=appt.studio_id,
        studio_name=studio_name or (appt.studio.name if appt.studio else None),
        servico_nome=appt.servico_nome,
        preco=float(appt.preco),
        payment_mode=appt.payment_mode,
        data=appt.data,
        hora=appt.hora,
        scheduled_at=appt.scheduled_at,
        status=appt.status,
        valor_pago=float(appt.valor_pago),
        client_name=appt.client_name,
        client_email=appt.client_email,
        client_phone=appt.client_phone,
        notas=appt.notas,
        confirmado_cliente_at=appt.confirmado_cliente_at,
        rating=appt.rating,
        payment=(
            PaymentInfo(
                valor=float(pay.valor),
                tipo=pay.tipo,
                status=pay.status,
                asaas_invoice_url=pay.asaas_invoice_url,
            )
            if pay
            else None
        ),
    )


def _link_or_create_client(db: Session, data) -> tuple[User, bool]:
    user = db.query(User).filter(User.email == data.client_email).first()
    is_new = False
    if not user:
        user = User(
            email=data.client_email,
            name=data.client_name,
            whatsapp=data.client_phone,
            cpf_cnpj=getattr(data, "client_cpf_cnpj", None),
            role=UserRole.CLIENTE,
        )
        db.add(user)
        db.flush()
        is_new = True
    elif not user.cpf_cnpj and getattr(data, "client_cpf_cnpj", None):
        user.cpf_cnpj = data.client_cpf_cnpj
    return user, is_new


async def _create_charge_safe(appt: Appointment, studio: Studio, amount: float, cpf: str | None):
    try:
        customer_id = await asaas_service.find_or_create_customer(
            appt.client_name, appt.client_email, appt.client_phone, cpf
        )
        label = "Sinal" if appt.payment_mode == PaymentMode.DEPOSIT_50 else "Pagamento"
        desc = f"{label} - {appt.servico_nome} ({studio.name})"
        charge = await asaas_service.create_charge(customer_id, amount, desc, appt.data.isoformat())
        return charge["asaas_invoice_url"], charge
    except Exception as e:
        logger.error("Asaas charge failed: %s", e, exc_info=True)
        return (
            f"{settings.FRONTEND_URL}/pagamento-pendente",
            {"asaas_payment_id": None, "asaas_invoice_url": None},
        )


async def _do_booking(db, studio, service, data, amount, tipo, cobrar=True):
    scheduled_at = datetime.combine(data.data, time.fromisoformat(f"{data.hora}:00"))

    if not is_slot_configured(db, studio.id, data.data, data.hora):
        raise HTTPException(status_code=400, detail="Horário não disponível")
    if not is_slot_free(db, studio.id, scheduled_at):
        raise HTTPException(status_code=409, detail="Horário já ocupado")

    cliente, is_new = _link_or_create_client(db, data)

    appt = Appointment(
        studio_id=studio.id,
        cliente_id=cliente.id,
        service_id=service.id,
        servico_nome=service.name,
        preco=service.price,
        payment_mode=studio.payment_mode,
        data=data.data,
        hora=data.hora,
        scheduled_at=scheduled_at,
        client_name=data.client_name,
        client_email=data.client_email,
        client_phone=data.client_phone,
        notas=data.notas,
        action_token=secrets.token_urlsafe(32),
    )
    db.add(appt)
    db.flush()

    if cobrar:
        payment_link, charge = await _create_charge_safe(
            appt, studio, amount, getattr(data, "client_cpf_cnpj", None)
        )
    else:
        payment_link = f"{settings.FRONTEND_URL}/booking/{studio.slug}"
        charge = {"asaas_payment_id": None, "asaas_invoice_url": None}

    payment = Payment(
        appointment_id=appt.id,
        valor=amount,
        tipo=tipo,
        asaas_payment_id=charge.get("asaas_payment_id"),
        asaas_invoice_url=charge.get("asaas_invoice_url"),
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    db.commit()
    db.refresh(appt)

    await send_booking_confirmation(db, appt, studio, payment_link)

    # agenda lembretes 24h/2h (não deve quebrar o booking se o Celery/Redis falhar)
    try:
        from app.tasks.reminders import schedule_reminders

        schedule_reminders(appt)
    except Exception:
        logger.warning("Falha ao agendar lembretes (Celery indisponível?)", exc_info=True)

    if is_new:
        token = create_auth_token(db, cliente.id, AuthTokenType.SET_PASSWORD)
        db.commit()
        link = f"{settings.FRONTEND_URL}/auth/criar-senha/{token}"
        ok = await resend_service.send_set_password(cliente.email, cliente.name, link)
        db.add(
            NotificationLog(
                user_id=cliente.id,
                type=NotificationType.EMAIL_SET_PASSWORD,
                channel=NotificationChannel.EMAIL,
                recipient=cliente.email,
                success=ok,
            )
        )
        db.commit()
        from app.core.devlinks import log_link

        log_link("criar-senha-cliente", cliente.email, link, ok)

    return appt, payment_link


# ---------- booking público ----------
@router.post("/manual", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_manual_appointment(
    data: ManualBookingCreate,
    studio: Studio = Depends(get_current_studio),
    db: Session = Depends(get_db),
):
    """Nail designer cria agendamento manualmente; opcionalmente gera cobrança."""
    service = db.get(Service, data.service_id)
    if not service or service.studio_id != studio.id:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    total = float(service.price)
    if studio.payment_mode == PaymentMode.FULL_100:
        amount, tipo = total, PaymentType.FULL
    else:
        amount, tipo = round(total * 0.5, 2), PaymentType.DEPOSIT

    appt, payment_link = await _do_booking(db, studio, service, data, amount, tipo, cobrar=data.cobrar)
    return BookingResponse(
        appointment_id=appt.id,
        payment_link=payment_link,
        amount=amount,
        payment_mode=studio.payment_mode,
        message="Agendamento criado.",
    )


@router.post("/{slug}", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(slug: str, data: BookingCreate, db: Session = Depends(get_db)):
    studio = db.query(Studio).filter(Studio.slug == slug, Studio.is_active == True).first()  # noqa: E712
    if not studio:
        raise HTTPException(status_code=404, detail="Studio não encontrado")
    service = db.get(Service, data.service_id)
    if not service or service.studio_id != studio.id or not service.is_active:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    check_plan_limit(db, studio)

    total = float(service.price)
    if studio.payment_mode == PaymentMode.FULL_100:
        amount, tipo = total, PaymentType.FULL
    else:
        amount, tipo = round(total * 0.5, 2), PaymentType.DEPOSIT

    appt, payment_link = await _do_booking(db, studio, service, data, amount, tipo, cobrar=True)
    label = "Pague o valor para confirmar." if tipo == PaymentType.FULL else "Pague o sinal (50%) para confirmar."
    return BookingResponse(
        appointment_id=appt.id,
        payment_link=payment_link,
        amount=amount,
        payment_mode=studio.payment_mode,
        message=f"Agendamento criado! {label}",
    )


# ---------- ações do cliente por token ----------
@router.post("/{token}/confirmar")
def confirm_by_token(token: str, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.action_token == token).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    appt.confirmado_cliente_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Presença confirmada!"}


@router.post("/{token}/cancelar")
def cancel_by_token(token: str, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.action_token == token).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    if appt.status == AppointmentStatus.REALIZADO:
        raise HTTPException(status_code=400, detail="Agendamento já realizado")
    appt.status = AppointmentStatus.CANCELADO
    db.commit()
    return {"message": "Agendamento cancelado."}


@router.post("/{token}/remarcar")
def reschedule_by_token(token: str, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.action_token == token).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    appt.status = AppointmentStatus.REMARCADO
    db.commit()
    return {"message": "Solicitação de remarcação registrada. O studio entrará em contato."}


@router.get("/{token}/info")
def appointment_info(token: str, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.action_token == token).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return {
        "servico_nome": appt.servico_nome,
        "studio_name": appt.studio.name if appt.studio else None,
        "data": appt.data.isoformat(),
        "hora": appt.hora,
        "rating": appt.rating,
    }


@router.post("/{token}/avaliar")
def rate_by_token(token: str, data: RatingRequest, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.action_token == token).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    appt.rating = data.rating
    appt.rating_comment = data.comment
    db.commit()
    return {"message": "Obrigada pela avaliação! 💖"}


# ---------- listagens ----------
@router.get("/studio", response_model=list[AppointmentResponse])
def studio_appointments(
    status_filter: AppointmentStatus | None = Query(None, alias="status"),
    pendentes: bool = False,
    studio: Studio = Depends(get_current_studio),
    db: Session = Depends(get_db),
):
    q = db.query(Appointment).filter(Appointment.studio_id == studio.id)
    if status_filter:
        q = q.filter(Appointment.status == status_filter)
    if pendentes:
        # confirmados/agendados cujo horário já passou e cliente não confirmou presença
        now = datetime.now()
        q = q.filter(
            Appointment.scheduled_at <= now,
            Appointment.status.in_([AppointmentStatus.AGENDADO, AppointmentStatus.CONFIRMADO]),
            Appointment.confirmado_cliente_at.is_(None),
        )
    appts = q.order_by(Appointment.scheduled_at).all()
    return [_to_response(a, studio.name) for a in appts]


@router.get("/client", response_model=list[AppointmentResponse])
def client_appointments(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appts = (
        db.query(Appointment)
        .filter(Appointment.cliente_id == user.id)
        .order_by(Appointment.scheduled_at.desc())
        .all()
    )
    return [_to_response(a) for a in appts]


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: uuid.UUID,
    data: AppointmentUpdate,
    studio: Studio = Depends(get_current_studio),
    db: Session = Depends(get_db),
):
    appt = db.get(Appointment, appointment_id)
    if not appt or appt.studio_id != studio.id:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    was_realizado = appt.status == AppointmentStatus.REALIZADO
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(appt, field, value)
    db.commit()
    db.refresh(appt)

    # ao concluir o atendimento, pede avaliação por WhatsApp
    if not was_realizado and appt.status == AppointmentStatus.REALIZADO:
        try:
            link = f"{settings.FRONTEND_URL}/avaliar/{appt.action_token}"
            await zapi_service.send_rating_request(
                appt.client_phone, appt.client_name, link, studio.name
            )
        except Exception:
            logger.warning("Falha ao enviar pedido de avaliação", exc_info=True)

    return _to_response(appt, studio.name)
