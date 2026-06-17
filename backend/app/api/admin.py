import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.models.studio import Studio
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.payout import Payout
from app.models.enums import UserRole, PaymentStatus, PayoutStatus
from app.schemas.admin import (
    AdminDashboard,
    ClientRow,
    StudioRow,
    SettingsUpdate,
    SettingsResponse,
)
from app.services.platform import get_settings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=AdminDashboard)
def dashboard(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    faturado = (
        db.query(func.coalesce(func.sum(Payment.valor), 0))
        .filter(Payment.status == PaymentStatus.CONFIRMED, Payment.paid_at >= month_start)
        .scalar()
    )
    pendentes = (
        db.query(func.coalesce(func.sum(Payout.valor_liquido), 0))
        .filter(Payout.status == PayoutStatus.PENDENTE_APROVACAO)
        .scalar()
    )
    clientes = db.query(func.count(User.id)).filter(
        User.role == UserRole.CLIENTE, User.is_active == True  # noqa: E712
    ).scalar()
    studios = db.query(func.count(Studio.id)).filter(Studio.is_active == True).scalar()  # noqa: E712
    return AdminDashboard(
        faturado_mes=float(faturado or 0),
        repasses_pendentes=float(pendentes or 0),
        clientes_ativos=int(clientes or 0),
        studios_ativos=int(studios or 0),
        taxa_padrao=float(get_settings(db).default_fee_pct),
    )


@router.get("/clients", response_model=list[ClientRow])
def list_clients(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    clients = db.query(User).filter(User.role == UserRole.CLIENTE).order_by(User.created_at.desc()).all()
    out = []
    for c in clients:
        total = db.query(func.count(Appointment.id)).filter(Appointment.cliente_id == c.id).scalar()
        out.append(
            ClientRow(
                id=c.id, name=c.name, email=c.email, whatsapp=c.whatsapp,
                total_agendamentos=int(total or 0), is_active=c.is_active, created_at=c.created_at,
            )
        )
    return out


@router.post("/clients/{client_id}/block")
def block_client(client_id: uuid.UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    c = db.get(User, client_id)
    if not c or c.role != UserRole.CLIENTE:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    c.is_active = not c.is_active
    db.commit()
    return {"is_active": c.is_active}


@router.get("/studios", response_model=list[StudioRow])
def list_studios(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    studios = db.query(Studio).order_by(Studio.created_at.desc()).all()
    out = []
    for s in studios:
        total = db.query(func.count(Appointment.id)).filter(Appointment.studio_id == s.id).scalar()
        out.append(
            StudioRow(
                id=s.id, name=s.name, slug=s.slug,
                owner_email=s.owner.email if s.owner else None,
                plano=s.plano, agendamentos_total=int(total or 0),
                is_active=s.is_active, bank_verified=s.bank_verified, created_at=s.created_at,
            )
        )
    return out


@router.post("/studios/{studio_id}/block")
def block_studio(studio_id: uuid.UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    s = db.get(Studio, studio_id)
    if not s:
        raise HTTPException(status_code=404, detail="Studio não encontrado")
    s.is_active = not s.is_active
    db.commit()
    return {"is_active": s.is_active}


@router.post("/studios/{studio_id}/verificar-banco")
def verify_bank(studio_id: uuid.UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    s = db.get(Studio, studio_id)
    if not s:
        raise HTTPException(status_code=404, detail="Studio não encontrado")
    s.bank_verified = not s.bank_verified
    db.commit()
    return {"bank_verified": s.bank_verified}


@router.get("/settings", response_model=SettingsResponse)
def get_platform_settings(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    s = get_settings(db)
    return SettingsResponse(default_fee_pct=float(s.default_fee_pct), payout_weekday=s.payout_weekday)


@router.put("/settings", response_model=SettingsResponse)
def update_platform_settings(
    data: SettingsUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)
):
    s = get_settings(db)
    if data.default_fee_pct is not None:
        s.default_fee_pct = data.default_fee_pct
    if data.payout_weekday is not None:
        s.payout_weekday = data.payout_weekday
    db.commit()
    db.refresh(s)
    return SettingsResponse(default_fee_pct=float(s.default_fee_pct), payout_weekday=s.payout_weekday)
