import uuid
from datetime import date

from sqlalchemy import ForeignKey, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin, enum_col
from app.models.enums import SubscriptionStatus


class Subscription(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    studio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("studios.id"), index=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plans.id"))
    status: Mapped[SubscriptionStatus] = mapped_column(
        enum_col(SubscriptionStatus), default=SubscriptionStatus.TRIALING
    )
    asaas_subscription_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    current_period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    current_period_end: Mapped[date | None] = mapped_column(Date, nullable=True)

    studio: Mapped["Studio"] = relationship()
    plan: Mapped["Plan"] = relationship()
