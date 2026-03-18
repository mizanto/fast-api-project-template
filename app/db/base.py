from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    General base class for all ORM models.
    Later all models will inherit from it:
    class ExampleModel(Base): ...
    """

    pass


class IDMixin:
    """
    Opt-in integer auto-increment primary key.
    If you prefer UUID primary keys, swap to `Mapped[uuid.UUID]` and provide a default.
    """

    id: Mapped[int] = mapped_column(primary_key=True)


class TimestampMixin:
    """Opt-in created_at/updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# Usage:
# class User(IDMixin, TimestampMixin, Base):
#     __tablename__ = "users"
#     name: Mapped[str]
