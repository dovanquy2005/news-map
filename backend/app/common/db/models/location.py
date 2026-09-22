"""Location entity model with PostGIS spatial geometry."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.common.db.models.base import Base, UUIDPrimaryKeyMixin, utcnow


class Location(Base, UUIDPrimaryKeyMixin):
    """Resolved geospatial entity with administrative hierarchy and PostGIS point."""

    __tablename__ = "locations"

    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False)

    province: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ward: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    provider: Mapped[str] = mapped_column(String(50), default="internal", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # PostGIS spatial point SRID 4326 (WGS 84)
    geom = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
