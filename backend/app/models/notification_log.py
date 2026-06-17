import uuid
from datetime import datetime, timezone

from sqlalchemy import String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin, enum_col
from app.models.enums import NotificationType, NotificationChannel


class NotificationLog(Base, UUIDMixin):
    __tablename__ = "notification_logs"

    appointment_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("appointments.id"), nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    type: Mapped[NotificationType] = mapped_column(enum_col(NotificationType))
    channel: Mapped[NotificationChannel] = mapped_column(enum_col(NotificationChannel))
    recipient: Mapped[str] = mapped_column(String(255))
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    appointment: Mapped["Appointment"] = relationship(back_populates="notification_logs")
