from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_studio, get_studio_by_slug
from app.models.availability import Availability
from app.models.studio import Studio
from app.schemas.availability import AvailabilityUpsert, AvailabilityResponse, CalendarSlot
from app.services.calendar import compute_calendar

router = APIRouter(prefix="/availability", tags=["availability"])


@router.get("", response_model=AvailabilityResponse | None)
def get_config(
    ano: int = Query(...),
    mes: int = Query(..., ge=1, le=12),
    studio: Studio = Depends(get_current_studio),
    db: Session = Depends(get_db),
):
    return (
        db.query(Availability)
        .filter(
            Availability.studio_id == studio.id,
            Availability.ano == ano,
            Availability.mes == mes,
        )
        .first()
    )


@router.post("", response_model=AvailabilityResponse)
def upsert_config(
    data: AvailabilityUpsert,
    studio: Studio = Depends(get_current_studio),
    db: Session = Depends(get_db),
):
    config = (
        db.query(Availability)
        .filter(
            Availability.studio_id == studio.id,
            Availability.ano == data.ano,
            Availability.mes == data.mes,
        )
        .first()
    )
    if config:
        config.dias_semana = data.dias_semana
        config.horarios = data.horarios
    else:
        config = Availability(
            studio_id=studio.id,
            ano=data.ano,
            mes=data.mes,
            dias_semana=data.dias_semana,
            horarios=data.horarios,
        )
        db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.get("/{slug}/calendar", response_model=list[CalendarSlot])
def public_calendar(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    studio: Studio = Depends(get_studio_by_slug),
    db: Session = Depends(get_db),
):
    ano, mes = int(month[:4]), int(month[5:])
    return compute_calendar(db, studio.id, ano, mes)
