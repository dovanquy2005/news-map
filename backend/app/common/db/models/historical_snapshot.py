"""HistoricalSnapshot entity model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.common.db.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.common.db.models.event import Event


class HistoricalSnapshot(Base, UUIDPrimaryKeyMixin):
    """Periodic snapshots capturing event article and source counts over time."""

    __tablename__ = "historical_snapshots"

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    article_count: Mapped[int] = mapped_column(Integer, nullable=False)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="snapshots")

    __table_args__ = (
        Index("idx_snapshots_event_captured", "event_id", "captured_at"),
    )
