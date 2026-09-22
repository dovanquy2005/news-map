"""Event entity model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.common.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.common.db.models.event_article import EventArticle
    from backend.app.common.db.models.event_fact import EventFact
    from backend.app.common.db.models.event_timeline import EventTimeline
    from backend.app.common.db.models.historical_snapshot import HistoricalSnapshot


class Event(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Clustered real-world event entity (represented as a marker on the map)."""

    __tablename__ = "events"

    title: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_title: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    location_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # PostGIS geometry for spatial bounding-box indexing
    geom = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    first_reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    article_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    source_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    articles: Mapped[List["EventArticle"]] = relationship(
        "EventArticle", back_populates="event", cascade="all, delete-orphan"
    )
    facts: Mapped[List["EventFact"]] = relationship(
        "EventFact", back_populates="event", cascade="all, delete-orphan"
    )
    timeline: Mapped[List["EventTimeline"]] = relationship(
        "EventTimeline", back_populates="event", cascade="all, delete-orphan"
    )
    snapshots: Mapped[List["HistoricalSnapshot"]] = relationship(
        "HistoricalSnapshot", back_populates="event", cascade="all, delete-orphan"
    )
