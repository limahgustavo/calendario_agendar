from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class AppointmentStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    professional_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))

    # Client info (not a registered user — just data)
    client_name: Mapped[str] = mapped_column(String(100))
    client_email: Mapped[str] = mapped_column(String(255))
    client_phone: Mapped[str] = mapped_column(String(20))

    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[AppointmentStatus] = mapped_column(
        SAEnum(AppointmentStatus), default=AppointmentStatus.PENDING_PAYMENT
    )
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Confirmation token sent via WhatsApp link
    action_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    # Reminder control
    reminder_24h_sent: Mapped[bool] = mapped_column(default=False)
    reminder_2h_sent: Mapped[bool] = mapped_column(default=False)
    client_confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    professional: Mapped["User"] = relationship(back_populates="appointments")
    service: Mapped["Service"] = relationship(back_populates="appointments")
    payment: Mapped["Payment"] = relationship(back_populates="appointment", uselist=False)
    notification_logs: Mapped[list["NotificationLog"]] = relationship(back_populates="appointment")
