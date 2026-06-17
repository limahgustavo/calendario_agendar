import uuid

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import PaymentMode, StudioPlan


class StudioRegisterRequest(BaseModel):
    designer_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    whatsapp: str | None = None
    studio_name: str = Field(min_length=2, max_length=120)


class StudioUpdateRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    whatsapp: str | None = None
    payment_mode: PaymentMode | None = None
    pix_key: str | None = None
    bank_info: str | None = None


class StudioResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    email: str | None = None
    whatsapp: str | None = None
    payment_mode: PaymentMode
    plano: StudioPlan
    pix_key: str | None = None
    bank_info: str | None = None


class StudioPublicResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    payment_mode: PaymentMode
    whatsapp: str | None = None
