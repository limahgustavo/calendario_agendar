"""Computa slots do calendário cruzando a config de disponibilidade com agendamentos."""
from calendar import monthrange
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.availability import Availability
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus

ACTIVE_STATUSES = [AppointmentStatus.AGENDADO, AppointmentStatus.CONFIRMADO]


def _booked_set(db: Session, studio_id, year: int, month: int) -> set:
    _, days = monthrange(year, month)
    start = datetime(year, month, 1)
    end = datetime(year, month, days, 23, 59, 59)
    booked = (
        db.query(Appointment)
        .filter(
            Appointment.studio_id == studio_id,
            Appointment.scheduled_at >= start,
            Appointment.scheduled_at <= end,
            Appointment.status.in_(ACTIVE_STATUSES),
        )
        .all()
    )
    return {(a.data, a.hora) for a in booked}


def compute_calendar(db: Session, studio_id, ano: int, mes: int) -> list[dict]:
    config = (
        db.query(Availability)
        .filter(
            Availability.studio_id == studio_id,
            Availability.ano == ano,
            Availability.mes == mes,
        )
        .first()
    )
    if not config:
        return []

    dias = set(config.dias_semana or [])
    horarios = sorted(config.horarios or [])
    booked = _booked_set(db, studio_id, ano, mes)
    today = date.today()
    _, days = monthrange(ano, mes)

    out: list[dict] = []
    for day in range(1, days + 1):
        d = date(ano, mes, day)
        if d.weekday() not in dias or d < today:
            continue
        for h in horarios:
            out.append(
                {"date": d.isoformat(), "time_str": h, "available": (d, h) not in booked}
            )
    return out


def is_slot_configured(db: Session, studio_id, d: date, hora: str) -> bool:
    config = (
        db.query(Availability)
        .filter(
            Availability.studio_id == studio_id,
            Availability.ano == d.year,
            Availability.mes == d.month,
        )
        .first()
    )
    if not config:
        return False
    return d.weekday() in set(config.dias_semana or []) and hora in set(config.horarios or [])


def is_slot_free(db: Session, studio_id, scheduled_at: datetime) -> bool:
    conflict = (
        db.query(Appointment)
        .filter(
            Appointment.studio_id == studio_id,
            Appointment.scheduled_at == scheduled_at,
            Appointment.status.in_(ACTIVE_STATUSES),
        )
        .first()
    )
    return conflict is None
