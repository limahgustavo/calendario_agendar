import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import AppointmentStatus, PaymentMode, PaymentStatus, PaymentType


class BookingCreate(BaseModel):
    service_id: uuid.UUID
    data: date
    hora: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    client_name: str = Field(..., min_length=2, max_length=120)
    client_email: EmailStr
    client_phone: str = Field(..., min_length=8, max_length=20)
    client_cpf_cnpj: str | None = Field(None, max_length=20)
    notas: str | None = None


class ManualBookingCreate(BaseModel):
    service_id: uuid.UUID
    data: date
    hora: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    client_name: str = Field(..., min_length=2, max_length=120)
    client_email: EmailStr
    client_phone: str = Field(..., min_length=8, max_length=20)
    client_cpf_cnpj: str | None = None
    notas: str | None = None
    cobrar: bool = True  # se False, cria sem gerar cobrança (cliente paga depois)


class BookingResponse(BaseModel):
    appointment_id: uuid.UUID
    payment_link: str
    amount: float
    payment_mode: PaymentMode
    message: str


class AppointmentUpdate(BaseModel):
    status: AppointmentStatus | None = None
    notas: str | None = None


class RatingRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


class PaymentInfo(BaseModel):
    valor: float
    tipo: PaymentType
    status: PaymentStatus
    asaas_invoice_url: str | None = None

    model_config = {"from_attributes": True}


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    studio_id: uuid.UUID
    studio_name: str | None = None
    servico_nome: str
    preco: float
    payment_mode: PaymentMode
    data: date
    hora: str
    scheduled_at: datetime
    status: AppointmentStatus
    valor_pago: float
    client_name: str
    client_email: str
    client_phone: str
    notas: str | None = None
    confirmado_cliente_at: datetime | None = None
    rating: int | None = None
    payment: PaymentInfo | None = None

    model_config = {"from_attributes": True}
