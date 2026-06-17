import uuid

from sqlalchemy import String, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin, enum_col
from app.models.enums import PaymentMode, StudioPlan


class Studio(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "studios"

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(20), nullable=True)

    payment_mode: Mapped[PaymentMode] = mapped_column(
        enum_col(PaymentMode), default=PaymentMode.DEPOSIT_50
    )
    plano: Mapped[StudioPlan] = mapped_column(enum_col(StudioPlan), default=StudioPlan.BASICO)
    # taxa da plataforma específica do studio; se nulo, usa o default global
    platform_fee_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # dados sensíveis (criptografados em repouso via app.core.crypto)
    pix_key_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    bank_info_enc: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # dados bancários verificados pelo admin (libera repasse)
    bank_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    owner: Mapped["User"] = relationship(back_populates="studio")
    services: Mapped[list["Service"]] = relationship(back_populates="studio")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="studio")
