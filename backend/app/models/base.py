import uuid
from datetime import datetime, timezone

from sqlalchemy import Uuid, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column


def enum_col(enum_cls, **kw):
    """Coluna de enum armazenada como VARCHAR com os valores do enum (não o nome)."""
    return SAEnum(
        enum_cls,
        native_enum=False,
        length=40,
        values_callable=lambda e: [m.value for m in e],
        **kw,
    )


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
