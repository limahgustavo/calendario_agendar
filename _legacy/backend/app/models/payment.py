from datetime import datetime, timezone
from sqlalchemy import String, Numeric, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"), unique=True)

    amount: Mapped[float] = mapped_column(Numeric(10, 2))  # 50% do serviço
    asaas_payment_id: Mapped[str] = mapped_column(String(100), nullable=True)
    asaas_payment_link: Mapped[str] = mapped_column(String(500), nullable=True)
    asaas_invoice_url: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus), default=PaymentStatus.PENDING
    )
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    appointment: Mapped["Appointment"] = relationship(back_populates="payment")
