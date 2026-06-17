import uuid

from sqlalchemy import String, Numeric, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin, enum_col
from app.models.enums import ServiceCategory


class Service(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "services"

    studio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("studios.id"), index=True)
    categoria: Mapped[ServiceCategory] = mapped_column(
        enum_col(ServiceCategory), default=ServiceCategory.OUTROS
    )
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    studio: Mapped["Studio"] = relationship(back_populates="services")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="service")
