from calendar import monthrange
from datetime import datetime, date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.appointment import Appointment, AppointmentStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.schemas.dashboard import DashboardSummary, RevenueSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _revenue_for_month(db: Session, year: int, month: int) -> RevenueSummary:
    _, days = monthrange(year, month)
    start = datetime(year, month, 1)
    end = datetime(year, month, days, 23, 59, 59)

    appts = db.query(Appointment).filter(
        Appointment.scheduled_at >= start,
        Appointment.scheduled_at <= end,
    ).all()

    total = len(appts)
    confirmed = sum(1 for a in appts if a.status == AppointmentStatus.CONFIRMED)
    completed = sum(1 for a in appts if a.status == AppointmentStatus.COMPLETED)
    cancelled = sum(1 for a in appts if a.status == AppointmentStatus.CANCELLED)

    confirmed_payments = db.query(func.sum(Payment.amount)).join(Appointment).filter(
        Appointment.scheduled_at >= start,
        Appointment.scheduled_at <= end,
        Payment.status == PaymentStatus.CONFIRMED,
    ).scalar() or 0

    pending_total = sum(
        float(a.service.price) * 0.5
        for a in appts
        if a.status in (AppointmentStatus.CONFIRMED, AppointmentStatus.COMPLETED)
    )

    return RevenueSummary(
        month_year=f"{year:04d}-{month:02d}",
        total_appointments=total,
        confirmed_appointments=confirmed,
        completed_appointments=completed,
        cancelled_appointments=cancelled,
        revenue_confirmed=float(confirmed_payments),
        revenue_pending=pending_total - float(confirmed_payments),
    )


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    today = date.today()
    week_end = today + timedelta(days=7)

    today_count = db.query(Appointment).filter(
        func.date(Appointment.scheduled_at) == today,
        Appointment.status != AppointmentStatus.CANCELLED,
    ).count()

    week_count = db.query(Appointment).filter(
        func.date(Appointment.scheduled_at) >= today,
        func.date(Appointment.scheduled_at) <= week_end,
        Appointment.status != AppointmentStatus.CANCELLED,
    ).count()

    upcoming = db.query(Appointment).filter(
        Appointment.scheduled_at >= datetime.now(),
        Appointment.status.in_([AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING_PAYMENT]),
    ).order_by(Appointment.scheduled_at).limit(10).all()

    upcoming_data = [
        {
            "id": a.id,
            "client_name": a.client_name,
            "service_name": a.service.name,
            "scheduled_at": a.scheduled_at.isoformat(),
            "status": a.status.value,
        }
        for a in upcoming
    ]

    return DashboardSummary(
        today_appointments=today_count,
        week_appointments=week_count,
        current_month=_revenue_for_month(db, today.year, today.month),
        upcoming=upcoming_data,
    )


@router.get("/revenue")
def revenue_by_month(
    month_year: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    year, month = int(month_year[:4]), int(month_year[5:])
    return _revenue_for_month(db, year, month)
