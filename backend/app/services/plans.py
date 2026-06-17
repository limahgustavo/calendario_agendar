from calendar import monthrange
from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.plan import Plan
from app.models.appointment import Appointment
from app.models.studio import Studio
from app.models.enums import AppointmentStatus


def check_plan_limit(db: Session, studio: Studio) -> None:
    """Bloqueia novo agendamento se o studio excedeu o limite mensal do plano."""
    plan = db.query(Plan).filter(Plan.nome == studio.plano.value).first()
    if not plan or plan.limite_agendamentos is None:
        return  # sem plano cadastrado ou ilimitado

    now = datetime.now()
    _, days = monthrange(now.year, now.month)
    d_start, d_end = date(now.year, now.month, 1), date(now.year, now.month, days)
    count = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.studio_id == studio.id,
            Appointment.data >= d_start,
            Appointment.data <= d_end,
            Appointment.status != AppointmentStatus.CANCELADO,
        )
        .scalar()
    )
    if count is not None and count >= plan.limite_agendamentos:
        raise HTTPException(
            status_code=403,
            detail="Este studio atingiu o limite de agendamentos do plano deste mês.",
        )
