import uuid

from pydantic import BaseModel


class PlanResponse(BaseModel):
    id: uuid.UUID
    nome: str
    valor_mensal: float
    limite_agendamentos: int | None
    features: list
    is_active: bool

    model_config = {"from_attributes": True}


class SubscribeRequest(BaseModel):
    plan_id: uuid.UUID
