from pydantic import BaseModel, Field


class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None
    price: float = Field(..., gt=0)
    duration_minutes: int = Field(60, gt=0)


class ServiceUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    duration_minutes: int | None = Field(None, gt=0)
    is_active: bool | None = None


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    duration_minutes: int
    is_active: bool

    model_config = {"from_attributes": True}
