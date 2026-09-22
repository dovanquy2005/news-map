"""Article entity model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.common.db.models.base import Base, UUIDPrimaryKeyMixin, utcnow

if TYPE_CHECKING:
    from backend.app.common.db.models.event_article import EventArticle
    from backend.app.common.db.models.source import Source


class Article(Base, UUIDPrimaryKeyMixin):
    """Raw / normalized ingested article item."""

    __tablename__ = "articles"

    source_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(10), default="vi", nullable=False)
    raw_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )

    # Relationships
    source: Mapped["Source"] = relationship("Source", back_populates="articles")
    event_associations: Mapped[List["EventArticle"]] = relationship(
        "EventArticle", back_populates="article", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_articles_source_published", "source_id", "published_at"),
    )
