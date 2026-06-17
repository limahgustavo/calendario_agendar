from sqlalchemy import String, Numeric, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Plan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "plans"

    nome: Mapped[str] = mapped_column(String(40), unique=True)
    valor_mensal: Mapped[float] = mapped_column(Numeric(10, 2))
    # nulo = ilimitado
    limite_agendamentos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    features: Mapped[list] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
