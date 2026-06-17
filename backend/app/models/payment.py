import uuid
from datetime import datetime

from sqlalchemy import String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin, enum_col
from app.models.enums import PaymentType, PaymentStatus


class Payment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payments"

    appointment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("appointments.id"), index=True
    )
    valor: Mapped[float] = mapped_column(Numeric(10, 2))
    tipo: Mapped[PaymentType] = mapped_column(enum_col(PaymentType), default=PaymentType.DEPOSIT)
    gateway: Mapped[str] = mapped_column(String(20), default="asaas")

    asaas_payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    asaas_invoice_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[PaymentStatus] = mapped_column(
        enum_col(PaymentStatus), default=PaymentStatus.PENDING
    )
    comprovante_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    appointment: Mapped["Appointment"] = relationship(back_populates="payment")
