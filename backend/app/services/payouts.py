"""Cálculo e aprovação de repasses semanais."""
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.crypto import decrypt
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.payout import Payout
from app.models.studio import Studio
from app.models.enums import PaymentStatus, PayoutStatus
from app.services.platform import fee_pct_for
from app.services.asaas import asaas_service
from app.services.resend import resend_service


def week_bounds(ref: date) -> tuple[date, date]:
    monday = ref - timedelta(days=ref.weekday())
    return monday, monday + timedelta(days=6)


def generate_payouts_for_week(db: Session, ref: date | None = None) -> list[Payout]:
    """Cria repasses (pendentes de aprovação) para a semana de `ref` (default: hoje)."""
    ref = ref or date.today()
    monday, sunday = week_bounds(ref)
    start = datetime.combine(monday, datetime.min.time())
    end = datetime.combine(sunday, datetime.max.time())

    created: list[Payout] = []
    studios = db.query(Studio).filter(Studio.is_active == True).all()  # noqa: E712
    for studio in studios:
        if db.query(Payout).filter(
            Payout.studio_id == studio.id, Payout.semana_inicio == monday
        ).first():
            continue  # já existe repasse para esta semana

        rows = (
            db.query(Payment, Appointment)
            .join(Appointment, Payment.appointment_id == Appointment.id)
            .filter(
                Appointment.studio_id == studio.id,
                Payment.status == PaymentStatus.CONFIRMED,
                Payment.paid_at >= start,
                Payment.paid_at <= end,
            )
            .all()
        )
        if not rows:
            continue

        bruto = round(sum(float(p.valor) for p, _ in rows), 2)
        if bruto <= 0:
            continue

        fee_pct = fee_pct_for(db, studio)
        fee_val = round(bruto * fee_pct / 100, 2)
        liquido = round(bruto - fee_val, 2)
        detalhes = [
            {"appointment_id": str(a.id), "payment_id": str(p.id), "valor": float(p.valor)}
            for p, a in rows
        ]
        payout = Payout(
            studio_id=studio.id,
            semana_inicio=monday,
            valor_bruto=bruto,
            taxa_admin_pct=fee_pct,
            taxa_admin_valor=fee_val,
            valor_liquido=liquido,
            detalhes=detalhes,
        )
        db.add(payout)
        created.append(payout)

    db.commit()
    return created


async def approve_payout(db: Session, payout: Payout) -> Payout:
    """Aprova e transfere o repasse via PIX (Asaas), notifica designer e clientes."""
    studio = payout.studio
    if not studio.bank_verified:
        raise ValueError("Dados bancários do studio ainda não foram verificados pelo admin.")
    pix = decrypt(studio.pix_key_enc)
    if not pix:
        raise ValueError("Studio não cadastrou chave PIX para receber o repasse.")

    res = await asaas_service.create_transfer(
        pix, float(payout.valor_liquido), f"Repasse semana {payout.semana_inicio.isoformat()}"
    )
    now = datetime.now(timezone.utc)
    payout.asaas_transfer_id = res.get("asaas_transfer_id")
    payout.status = PayoutStatus.TRANSFERIDO
    payout.aprovado_at = now
    payout.transferido_at = now
    db.commit()

    # notifica a designer
    to = studio.email or (studio.owner.email if studio.owner else None)
    if to:
        await resend_service.send_payout_notice(to, studio.name, float(payout.valor_liquido))

    # avisa clientes com saldo presencial (modo 50%)
    await _notify_clients_balance(db, payout, studio)
    return payout


async def _notify_clients_balance(db: Session, payout: Payout, studio: Studio) -> None:
    from app.models.appointment import Appointment
    from app.models.enums import PaymentMode

    for item in payout.detalhes or []:
        appt = db.get(Appointment, uuid.UUID(item["appointment_id"]))
        if not appt or appt.payment_mode != PaymentMode.DEPOSIT_50:
            continue
        restante = round(float(appt.preco) * 0.5, 2)
        await resend_service.send_balance_notice(
            appt.client_email, appt.client_name, restante, appt.servico_nome, studio.name
        )
