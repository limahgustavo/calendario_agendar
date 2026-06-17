from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    EMAIL_CONFIRMATION = "email_confirmation"
    WHATSAPP_CONFIRMATION = "whatsapp_confirmation"
    WHATSAPP_REMINDER_24H = "whatsapp_reminder_24h"
    WHATSAPP_REMINDER_2H = "whatsapp_reminder_2h"
    EMAIL_REMINDER = "email_reminder"


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"))
    type: Mapped[NotificationType] = mapped_column(SAEnum(NotificationType))
    recipient: Mapped[str] = mapped_column(String(255))
    success: Mapped[bool] = mapped_column(default=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    appointment: Mapped["Appointment"] = relationship(back_populates="notification_logs")
