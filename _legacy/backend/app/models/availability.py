from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AvailabilitySlot(Base):
    """
    Representa um slot de horário disponível configurado pela profissional.
    month_year: formato 'YYYY-MM' (ex: '2026-03')
    weekday: 0=Segunda ... 6=Domingo
    time_str: '08:00', '13:00', etc.
    """
    __tablename__ = "availability_slots"
    __table_args__ = (
        UniqueConstraint("user_id", "month_year", "weekday", "time_str", name="uq_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    month_year: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    weekday: Mapped[int] = mapped_column(Integer)        # 0-6
    time_str: Mapped[str] = mapped_column(String(5))     # HH:MM
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="availability_slots")
