"""EventArticle associative entity model (multi-source provenance)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.common.db.models.base import Base, utcnow

if TYPE_CHECKING:
    from backend.app.common.db.models.article import Article
    from backend.app.common.db.models.event import Event


class EventArticle(Base):
    """Associative entity linking articles to events with match provenance."""

    __tablename__ = "event_articles"

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True,
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    match_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    match_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="articles")
    article: Mapped["Article"] = relationship("Article", back_populates="event_associations")
