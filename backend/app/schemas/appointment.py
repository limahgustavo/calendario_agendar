from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    service_id: int
    scheduled_at: datetime
    client_name: str = Field(..., min_length=2, max_length=100)
    client_email: EmailStr
    client_phone: str = Field(..., min_length=8, max_length=20)
    notes: str | None = None


class AppointmentUpdate(BaseModel):
    status: AppointmentStatus | None = None
    notes: str | None = None


class ServiceSummary(BaseModel):
    id: int
    name: str
    price: float
    duration_minutes: int

    model_config = {"from_attributes": True}


class PaymentSummary(BaseModel):
    id: int
    amount: float
    status: str
    asaas_payment_link: str | None

    model_config = {"from_attributes": True}


class AppointmentResponse(BaseModel):
    id: int
    service: ServiceSummary
    client_name: str
    client_email: str
    client_phone: str
    scheduled_at: datetime
    status: AppointmentStatus
    notes: str | None
    payment: PaymentSummary | None
    reminder_24h_sent: bool
    reminder_2h_sent: bool
    client_confirmed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AppointmentBookingResponse(BaseModel):
    appointment_id: int
    payment_link: str
    message: str
