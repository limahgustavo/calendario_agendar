import uuid

from pydantic import BaseModel, Field

from app.models.enums import ServiceCategory


class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    categoria: ServiceCategory = ServiceCategory.OUTROS
    description: str | None = None
    price: float = Field(..., gt=0)
    duration_minutes: int = Field(60, gt=0)


class ServiceUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    categoria: ServiceCategory | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)
    duration_minutes: int | None = Field(None, gt=0)
    is_active: bool | None = None


class ServiceResponse(BaseModel):
    id: uuid.UUID
    studio_id: uuid.UUID
    categoria: ServiceCategory
    name: str
    description: str | None
    price: float
    duration_minutes: int
    is_active: bool

    model_config = {"from_attributes": True}
