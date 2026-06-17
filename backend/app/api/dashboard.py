from calendar import monthrange
from collections import Counter
from datetime import datetime, date, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_studio
from app.api.appointments import _to_response
from app.models.studio import Studio
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.enums import AppointmentStatus, PaymentStatus, PaymentMode
from app.schemas.dashboard import StudioDashboard, StudioReport, ReportMonth

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

ACTIVE = [AppointmentStatus.AGENDADO, AppointmentStatus.CONFIRMADO]
DONE = (AppointmentStatus.CONFIRMADO, AppointmentStatus.REALIZADO)


@router.get("/studio", response_model=StudioDashboard)
def studio_dashboard(studio: Studio = Depends(get_current_studio), db: Session = Depends(get_db)):
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    _, days = monthrange(now.year, now.month)
    d_start, d_end = date(now.year, now.month, 1), date(now.year, now.month, days)

    proximos = (
        db.query(Appointment)
        .filter(
            Appointment.studio_id == studio.id,
            Appointment.scheduled_at >= now,
            Appointment.status.in_(ACTIVE),
        )
        .order_by(Appointment.scheduled_at)
        .limit(10)
        .all()
    )

    recebido = (
        db.query(func.coalesce(func.sum(Payment.valor), 0))
        .join(Appointment, Payment.appointment_id == Appointment.id)
        .filter(
            Appointment.studio_id == studio.id,
            Payment.status == PaymentStatus.CONFIRMED,
            Payment.paid_at >= month_start,
        )
        .scalar()
    )

    appts_mes = (
        db.query(Appointment)
        .filter(
            Appointment.studio_id == studio.id,
            Appointment.data >= d_start,
            Appointment.data <= d_end,
        )
        .all()
    )
    total_mes = len(appts_mes)
    confirmados_mes = sum(1 for a in appts_mes if a.status in DONE)
    a_receber = sum(
        float(a.preco) * 0.5
        for a in appts_mes
        if a.status in DONE and a.payment_mode == PaymentMode.DEPOSIT_50
    )

    pendentes = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.studio_id == studio.id,
            Appointment.scheduled_at <= now,
            Appointment.status.in_(ACTIVE),
            Appointment.confirmado_cliente_at.is_(None),
        )
        .scalar()
    )

    return StudioDashboard(
        proximos=[_to_response(a, studio.name) for a in proximos],
        faturamento_mes_recebido=float(recebido or 0),
        faturamento_mes_a_receber=round(a_receber, 2),
        total_mes=total_mes,
        confirmados_mes=confirmados_mes,
        pendentes_count=int(pendentes or 0),
    )


@router.get("/studio/relatorio", response_model=StudioReport)
def studio_report(
    ano: int = Query(...),
    studio: Studio = Depends(get_current_studio),
    db: Session = Depends(get_db),
):
    year_start = datetime(ano, 1, 1, tzinfo=timezone.utc)
    year_end = datetime(ano, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    payments = (
        db.query(Payment)
        .join(Appointment, Payment.appointment_id == Appointment.id)
        .filter(
            Appointment.studio_id == studio.id,
            Payment.status == PaymentStatus.CONFIRMED,
            Payment.paid_at >= year_start,
            Payment.paid_at <= year_end,
        )
        .all()
    )
    appts = (
        db.query(Appointment)
        .filter(
            Appointment.studio_id == studio.id,
            Appointment.data >= date(ano, 1, 1),
            Appointment.data <= date(ano, 12, 31),
        )
        .all()
    )

    buckets = {m: {"recebido": 0.0, "total": 0, "realizados": 0, "cancelados": 0} for m in range(1, 13)}
    for p in payments:
        if p.paid_at:
            buckets[p.paid_at.month]["recebido"] += float(p.valor)
    for a in appts:
        b = buckets[a.data.month]
        b["total"] += 1
        if a.status == AppointmentStatus.REALIZADO:
            b["realizados"] += 1
        elif a.status == AppointmentStatus.CANCELADO:
            b["cancelados"] += 1

    meses = [
        ReportMonth(
            mes=m,
            recebido=round(buckets[m]["recebido"], 2),
            total=buckets[m]["total"],
            realizados=buckets[m]["realizados"],
            cancelados=buckets[m]["cancelados"],
        )
        for m in range(1, 13)
    ]

    rated = [a for a in appts if a.rating]
    media = round(sum(a.rating for a in rated) / len(rated), 2) if rated else None
    cnt = Counter(a.servico_nome for a in appts if a.status != AppointmentStatus.CANCELADO)
    top = [{"nome": n, "qtd": q} for n, q in cnt.most_common(5)]

    return StudioReport(
        ano=ano,
        meses=meses,
        media_avaliacao=media,
        total_avaliacoes=len(rated),
        servicos_top=top,
    )
