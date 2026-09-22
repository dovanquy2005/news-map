"""EventTimeline entity model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.common.db.models.base import Base, UUIDPrimaryKeyMixin, utcnow

if TYPE_CHECKING:
    from backend.app.common.db.models.event import Event


class EventTimeline(Base, UUIDPrimaryKeyMixin):
    """Chronological updates or milestone occurrences in an event's lifecycle."""

    __tablename__ = "event_timeline"

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timeline_type: Mapped[str] = mapped_column(
        String(50), default="reported", nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_article_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("articles.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="timeline")
