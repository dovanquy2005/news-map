"""EventFact entity model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.common.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.common.db.models.event import Event


class EventFact(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Specific key facts extracted for an event."""

    __tablename__ = "event_facts"

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fact_key: Mapped[str] = mapped_column(String(100), nullable=False)
    fact_value: Mapped[str] = mapped_column(Text, nullable=False)
    fact_confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    supporting_article_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="facts")
