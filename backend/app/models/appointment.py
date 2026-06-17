import uuid
from datetime import datetime, date

from sqlalchemy import String, Numeric, ForeignKey, DateTime, Date, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin, enum_col
from app.models.enums import AppointmentStatus, PaymentMode


class Appointment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "appointments"

    studio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("studios.id"), index=True)
    cliente_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id"))

    # snapshots no momento do agendamento (preço pode mudar depois)
    servico_nome: Mapped[str] = mapped_column(String(120))
    preco: Mapped[float] = mapped_column(Numeric(10, 2))
    payment_mode: Mapped[PaymentMode] = mapped_column(
        enum_col(PaymentMode), default=PaymentMode.DEPOSIT_50
    )

    data: Mapped[date] = mapped_column(Date)
    hora: Mapped[str] = mapped_column(String(5))  # HH:MM
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), index=True)

    status: Mapped[AppointmentStatus] = mapped_column(
        enum_col(AppointmentStatus), default=AppointmentStatus.AGENDADO
    )
    valor_pago: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    # dados de cliente avulso (quando não há conta) — mantidos como fallback
    client_name: Mapped[str] = mapped_column(String(120))
    client_email: Mapped[str] = mapped_column(String(255))
    client_phone: Mapped[str] = mapped_column(String(20))

    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    confirmado_cliente_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reminder_24h_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_2h_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    # avaliação pós-atendimento (1-5)
    rating: Mapped[int | None] = mapped_column(nullable=True)
    rating_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    studio: Mapped["Studio"] = relationship(back_populates="appointments")
    cliente: Mapped["User"] = relationship(back_populates="appointments")
    service: Mapped["Service"] = relationship(back_populates="appointments")
    payment: Mapped["Payment"] = relationship(back_populates="appointment", uselist=False)
    notification_logs: Mapped[list["NotificationLog"]] = relationship(
        back_populates="appointment"
    )
