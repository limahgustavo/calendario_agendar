from calendar import monthrange
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.availability import AvailabilitySlot
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.schemas.availability import (
    SlotBulkCreate,
    SlotResponse,
    CalendarSlotResponse,
)

router = APIRouter(prefix="/availability", tags=["availability"])


@router.get("", response_model=list[SlotResponse])
def list_slots(
    month_year: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(AvailabilitySlot)
        .filter(
            AvailabilitySlot.user_id == current_user.id,
            AvailabilitySlot.month_year == month_year,
        )
        .all()
    )


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def bulk_create_slots(
    data: SlotBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Replace all slots for the given month_year with the new configuration."""
    db.query(AvailabilitySlot).filter(
        AvailabilitySlot.user_id == current_user.id,
        AvailabilitySlot.month_year == data.month_year,
    ).delete()

    slots = [
        AvailabilitySlot(
            user_id=current_user.id,
            month_year=data.month_year,
            weekday=wd,
            time_str=t,
        )
        for wd in data.weekdays
        for t in data.times
    ]
    db.add_all(slots)
    db.commit()
    return {"created": len(slots)}


@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    slot = db.get(AvailabilitySlot, slot_id)
    if not slot or slot.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Slot não encontrado")
    db.delete(slot)
    db.commit()


@router.get("/calendar", response_model=list[CalendarSlotResponse])
def get_calendar(
    month_year: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
):
    """Public endpoint — returns all calendar slots with availability status."""
    year, month = int(month_year[:4]), int(month_year[5:])
    _, days_in_month = monthrange(year, month)

    # All configured slots for this month (all professionals — single professional for now)
    slots = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.month_year == month_year
    ).all()

    slot_set = {(s.weekday, s.time_str) for s in slots}

    # Already booked confirmed appointments
    from datetime import datetime
    month_start = datetime(year, month, 1)
    month_end = datetime(year, month, days_in_month, 23, 59, 59)
    booked = db.query(Appointment).filter(
        Appointment.scheduled_at >= month_start,
        Appointment.scheduled_at <= month_end,
        Appointment.status.in_([
            AppointmentStatus.PENDING_PAYMENT,
            AppointmentStatus.CONFIRMED,
        ]),
    ).all()

    booked_set = {
        (a.scheduled_at.date(), a.scheduled_at.strftime("%H:%M"))
        for a in booked
    }

    result = []
    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        weekday = d.weekday()  # 0=Monday
        for (wd, time_str) in slot_set:
            if wd == weekday:
                available = (d, time_str) not in booked_set
                result.append(
                    CalendarSlotResponse(
                        date=d.isoformat(),
                        time_str=time_str,
                        available=available,
                    )
                )

    result.sort(key=lambda x: (x.date, x.time_str))
    return result
