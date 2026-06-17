from datetime import datetime, timezone

from sqlalchemy import Numeric, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin


class PlatformSettings(Base, UUIDMixin):
    """Configurações globais da plataforma (registro único / singleton)."""
    __tablename__ = "platform_settings"

    default_fee_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=20)
    payout_weekday: Mapped[int] = mapped_column(Integer, default=4)  # 0=seg ... 4=sex
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
