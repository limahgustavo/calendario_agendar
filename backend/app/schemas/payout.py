import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.enums import PayoutStatus


class PayoutResponse(BaseModel):
    id: uuid.UUID
    studio_id: uuid.UUID
    studio_name: str | None = None
    semana_inicio: date
    valor_bruto: float
    taxa_admin_pct: float
    taxa_admin_valor: float
    valor_liquido: float
    status: PayoutStatus
    asaas_transfer_id: str | None = None
    transferido_at: datetime | None = None

    model_config = {"from_attributes": True}
