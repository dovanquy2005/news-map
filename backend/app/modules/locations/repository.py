"""Location repository with PostGIS spatial querying and deduplication."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from geoalchemy2 import Geography
from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session

from backend.app.common.db.models.location import Location

logger = logging.getLogger(__name__)


class LocationRepository:
    """Handles spatial persistence and 50m deduplication for locations."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, location_id: UUID) -> Optional[Location]:
        """Fetch location by primary key."""
        return self._session.get(Location, location_id)

    def find_existing_nearby(
        self,
        latitude: float,
        longitude: float,
        tolerance_meters: float = 50.0,
        raw_text: Optional[str] = None,
    ) -> Optional[Location]:
        """Find an existing location within spatial tolerance or matching raw text."""
        # 1. Exact raw text match check
        if raw_text:
            stmt_text = select(Location).where(Location.raw_text == raw_text.strip()).limit(1)
            exact = self._session.scalars(stmt_text).first()
            if exact:
                return exact

        # 2. PostGIS spatial distance check (50m)
        target_point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
        stmt = (
            select(Location)
            .where(
                func.ST_DWithin(
                    cast(Location.geom, Geography),
                    cast(target_point, Geography),
                    tolerance_meters,
                )
            )
            .order_by(
                func.ST_Distance(
                    cast(Location.geom, Geography),
                    cast(target_point, Geography),
                )
            )
            .limit(1)
        )
        return self._session.scalars(stmt).first()

    def create(
        self,
        raw_text: str,
        normalized_text: str,
        latitude: float,
        longitude: float,
        provider: str,
        confidence: float,
        province: Optional[str] = None,
        district: Optional[str] = None,
        ward: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Location:
        """Create and persist a new Location with PostGIS Point geometry."""
        # Terrestrial boundary sanity check
        if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
            raise ValueError(f"Invalid terrestrial coordinates: lat={latitude}, lng={longitude}")

        point_wkt = f"SRID=4326;POINT({longitude} {latitude})"
        location = Location(
            raw_text=raw_text,
            normalized_text=normalized_text,
            province=province,
            district=district,
            ward=ward,
            address=address,
            latitude=latitude,
            longitude=longitude,
            provider=provider,
            confidence=confidence,
            geom=point_wkt,
        )
        self._session.add(location)
        self._session.flush()
        return location
