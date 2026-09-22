"""Location domain service for resolution and persistence orchestration."""

from __future__ import annotations

import logging
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.common.db.models.location import Location
from backend.app.common.metrics import get_metrics
from backend.app.modules.locations.geocoder.service import GeocoderService
from backend.app.modules.locations.repository import LocationRepository
from backend.app.modules.locations.schemas import ResolvedLocationDTO

logger = logging.getLogger(__name__)


class LocationService:
    """Orchestrates geocoding resolution, 50m spatial deduplication, and persistence."""

    def __init__(
        self,
        session: Session,
        geocoder: Optional[GeocoderService] = None,
        repository: Optional[LocationRepository] = None,
    ) -> None:
        self._session = session
        self._geocoder = geocoder or GeocoderService()
        self._repo = repository or LocationRepository(session)
        self._metrics = get_metrics()

    def resolve_and_persist(
        self,
        raw_text: str,
        hint_province: Optional[str] = None,
        hint_district: Optional[str] = None,
        hint_ward: Optional[str] = None,
    ) -> Tuple[Optional[Location], Optional[ResolvedLocationDTO]]:
        """Resolve raw location text and persist or reuse existing Location."""
        if not raw_text or not raw_text.strip():
            self._metrics.inc_counter("geocode_failure_total", 1.0, {"reason": "empty_query"})
            return None, None

        resolved: Optional[ResolvedLocationDTO] = self._geocoder.resolve(
            query=raw_text,
            hint_province=hint_province,
            hint_district=hint_district,
            hint_ward=hint_ward,
        )

        if not resolved:
            logger.info("Could not resolve location for query: '%s'", raw_text)
            self._metrics.inc_counter("geocode_failure_total", 1.0, {"reason": "unresolvable"})
            return None, None

        # Check for deduplication within 50 meters
        existing = self._repo.find_existing_nearby(
            latitude=resolved.latitude,
            longitude=resolved.longitude,
            tolerance_meters=50.0,
            raw_text=raw_text,
        )

        if existing:
            logger.info(
                "Reusing existing location %s for query '%s' (lat=%.4f, lng=%.4f)",
                existing.id,
                raw_text,
                resolved.latitude,
                resolved.longitude,
            )
            self._metrics.inc_counter("geocode_success_total", 1.0, {"reused": "true"})
            if resolved.is_approximate:
                self._metrics.inc_counter("geocode_approximate_total", 1.0)
            return existing, resolved

        # Persist new location
        new_location = self._repo.create(
            raw_text=raw_text.strip(),
            normalized_text=resolved.resolved_address,
            latitude=resolved.latitude,
            longitude=resolved.longitude,
            provider=resolved.provider,
            confidence=resolved.location_confidence,
            province=hint_province,
            district=hint_district,
            ward=hint_ward,
            address=resolved.resolved_address,
        )

        logger.info(
            "Created new location %s for '%s' (lat=%.4f, lng=%.4f, approx=%s)",
            new_location.id,
            raw_text,
            resolved.latitude,
            resolved.longitude,
            resolved.is_approximate,
        )
        self._metrics.inc_counter("geocode_success_total", 1.0, {"reused": "false"})
        if resolved.is_approximate:
            self._metrics.inc_counter("geocode_approximate_total", 1.0)

        return new_location, resolved
