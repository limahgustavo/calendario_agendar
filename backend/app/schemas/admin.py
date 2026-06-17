import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import StudioPlan


class AdminDashboard(BaseModel):
    faturado_mes: float
    repasses_pendentes: float
    clientes_ativos: int
    studios_ativos: int
    taxa_padrao: float


class ClientRow(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    whatsapp: str | None = None
    total_agendamentos: int
    is_active: bool
    created_at: datetime


class StudioRow(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    owner_email: str | None = None
    plano: StudioPlan
    agendamentos_total: int
    is_active: bool
    bank_verified: bool
    created_at: datetime


class SettingsUpdate(BaseModel):
    default_fee_pct: float | None = None
    payout_weekday: int | None = None


class SettingsResponse(BaseModel):
    default_fee_pct: float
    payout_weekday: int
