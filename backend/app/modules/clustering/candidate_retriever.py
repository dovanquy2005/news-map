"""Candidate event retrieval service for clustering."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
from typing import List, Optional
from uuid import UUID

from geoalchemy2 import Geography
from sqlalchemy import and_, cast, func, or_, select
from sqlalchemy.orm import Session

from backend.app.common.db.models.event import Event
from backend.app.modules.clustering.schemas import EventCandidateDTO

logger = logging.getLogger(__name__)

COMPATIBLE_CATEGORIES: dict[str, list[str]] = {
    "ACCIDENT": ["ACCIDENT", "TRAFFIC", "OTHER"],
    "TRAFFIC": ["TRAFFIC", "ACCIDENT", "INFRASTRUCTURE"],
    "FIRE": ["FIRE", "ACCIDENT", "DISASTER"],
    "WEATHER": ["WEATHER", "DISASTER", "ENVIRONMENT"],
    "DISASTER": ["DISASTER", "WEATHER", "ENVIRONMENT", "FIRE"],
    "INFRASTRUCTURE": ["INFRASTRUCTURE", "TRAFFIC", "ECONOMY"],
    "CRIME": ["CRIME", "SOCIETY", "OTHER"],
    "SOCIETY": ["SOCIETY", "CRIME", "CULTURE", "HEALTH"],
    "ECONOMY": ["ECONOMY", "INFRASTRUCTURE", "SOCIETY"],
    "HEALTH": ["HEALTH", "SOCIETY", "ENVIRONMENT"],
    "ENVIRONMENT": ["ENVIRONMENT", "WEATHER", "DISASTER"],
    "SPORTS": ["SPORTS", "CULTURE"],
    "CULTURE": ["CULTURE", "SPORTS", "SOCIETY"],
    "TECHNOLOGY": ["TECHNOLOGY", "ECONOMY"],
    "EDUCATION": ["EDUCATION", "SOCIETY"],
    "OTHER": ["OTHER", "ACCIDENT", "SOCIETY"],
}


class ClusteringCandidateRetriever:
    """Fast spatial-temporal-categorical retrieval for candidate events."""

    def __init__(self, session: Session, time_window_hours: int = 72) -> None:
        self._session = session
        self._time_window = timedelta(hours=time_window_hours)

    def retrieve_candidates(
        self,
        reference_time: datetime,
        category: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        province: Optional[str] = None,
        location_level: Optional[str] = None,
        limit: int = 25,
    ) -> List[EventCandidateDTO]:
        """Query bounded subset of existing events within spatial/temporal window."""
        cat_upper = category.upper()
        allowed_categories = COMPATIBLE_CATEGORIES.get(cat_upper, [cat_upper])

        min_time = reference_time - self._time_window
        max_time = reference_time + self._time_window

        # Base conditions: active status, compatible category, temporal window
        conditions = [
            Event.status != "ARCHIVED",
            Event.category.in_(allowed_categories),
            or_(
                Event.occurred_at.between(min_time, max_time),
                Event.last_updated_at.between(min_time, max_time),
            ),
        ]

        has_spatial = (
            latitude is not None
            and longitude is not None
            and -90.0 <= latitude <= 90.0
            and -180.0 <= longitude <= 180.0
        )

        if has_spatial:
            # Determine radius based on granularity
            if location_level in ["STREET", "POI"]:
                radius_meters = 2000.0  # 2km
            elif location_level in ["WARD", "DISTRICT"]:
                radius_meters = 10000.0  # 10km
            else:
                radius_meters = 50000.0  # 50km for province

            target_point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
            spatial_cond = func.ST_DWithin(
                cast(Event.geom, Geography),
                cast(target_point, Geography),
                radius_meters,
            )

            # If province is provided, allow same-province events as secondary spatial match
            if province:
                spatial_cond = or_(
                    spatial_cond,
                    Event.location_label.ilike(f"%{province}%"),
                )

            conditions.append(spatial_cond)

            distance_col = func.ST_Distance(
                cast(Event.geom, Geography),
                cast(target_point, Geography),
            ).label("distance_meters")

            stmt = (
                select(Event, distance_col)
                .where(and_(*conditions))
                .order_by(distance_col.asc(), Event.last_updated_at.desc())
                .limit(limit)
            )

            results = self._session.execute(stmt).all()
            candidates: List[EventCandidateDTO] = []
            for ev, dist in results:
                candidates.append(
                    EventCandidateDTO(
                        event_id=ev.id,
                        title=ev.title,
                        normalized_title=ev.normalized_title,
                        category=ev.category,
                        status=ev.status,
                        latitude=ev.latitude,
                        longitude=ev.longitude,
                        location_label=ev.location_label,
                        location_confidence=ev.location_confidence,
                        occurred_at=ev.occurred_at,
                        first_reported_at=ev.first_reported_at,
                        last_updated_at=ev.last_updated_at,
                        article_count=ev.article_count,
                        source_count=ev.source_count,
                        confidence_score=ev.confidence_score,
                        summary=ev.summary,
                        distance_meters=float(dist) if dist is not None else None,
                    )
                )
            return candidates

        # Non-spatial fallback
        stmt = (
            select(Event)
            .where(and_(*conditions))
            .order_by(Event.last_updated_at.desc())
            .limit(limit)
        )
        events = self._session.scalars(stmt).all()
        return [
            EventCandidateDTO(
                event_id=ev.id,
                title=ev.title,
                normalized_title=ev.normalized_title,
                category=ev.category,
                status=ev.status,
                latitude=ev.latitude,
                longitude=ev.longitude,
                location_label=ev.location_label,
                location_confidence=ev.location_confidence,
                occurred_at=ev.occurred_at,
                first_reported_at=ev.first_reported_at,
                last_updated_at=ev.last_updated_at,
                article_count=ev.article_count,
                source_count=ev.source_count,
                confidence_score=ev.confidence_score,
                summary=ev.summary,
                distance_meters=None,
            )
            for ev in events
        ]
