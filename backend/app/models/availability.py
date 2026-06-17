import uuid

from sqlalchemy import Integer, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Availability(Base, UUIDMixin, TimestampMixin):
    """
    Configuração de disponibilidade de um studio por mês.
    dias_semana: lista de inteiros [0..6] (0=Segunda ... 6=Domingo)
    horarios: lista de strings 'HH:MM' (ex: ['08:00', '13:00'])
    Os slots concretos do calendário são computados on-the-fly cruzando
    dias_semana x horarios x agendamentos existentes.
    """
    __tablename__ = "availability"
    __table_args__ = (
        UniqueConstraint("studio_id", "ano", "mes", name="uq_availability_studio_month"),
    )

    studio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("studios.id"), index=True)
    ano: Mapped[int] = mapped_column(Integer)
    mes: Mapped[int] = mapped_column(Integer)  # 1-12
    dias_semana: Mapped[list] = mapped_column(JSON, default=list)
    horarios: Mapped[list] = mapped_column(JSON, default=list)

    studio: Mapped["Studio"] = relationship()
