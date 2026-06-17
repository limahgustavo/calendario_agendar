import uuid
from datetime import datetime, date

from sqlalchemy import Numeric, ForeignKey, DateTime, Date, String, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin, enum_col
from app.models.enums import PayoutStatus


class Payout(Base, UUIDMixin, TimestampMixin):
    """Repasse semanal de um studio."""
    __tablename__ = "payouts"
    __table_args__ = (
        UniqueConstraint("studio_id", "semana_inicio", name="uq_payout_studio_week"),
    )

    studio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("studios.id"), index=True)
    semana_inicio: Mapped[date] = mapped_column(Date)  # segunda-feira da semana

    valor_bruto: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    taxa_admin_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    taxa_admin_valor: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    valor_liquido: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    status: Mapped[PayoutStatus] = mapped_column(
        enum_col(PayoutStatus), default=PayoutStatus.PENDENTE_APROVACAO
    )
    asaas_transfer_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # [{appointment_id, payment_id, valor}]
    detalhes: Mapped[list] = mapped_column(JSON, default=list)

    aprovado_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    transferido_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    studio: Mapped["Studio"] = relationship()
