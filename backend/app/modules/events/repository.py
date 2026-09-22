"""Event repository handling spatial bounding box filtering, details, and search."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import math
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from geoalchemy2 import Geography
from sqlalchemy import and_, case, cast, desc, func, or_, select
from sqlalchemy.orm import Session

from backend.app.common.db.models.article import Article
from backend.app.common.db.models.event import Event
from backend.app.common.db.models.event_article import EventArticle
from backend.app.common.db.models.event_fact import EventFact
from backend.app.common.db.models.event_timeline import EventTimeline
from backend.app.common.db.models.source import Source
from backend.app.modules.events.confidence import ConfidenceScoringEngine
from backend.app.modules.events.schemas.public import (
    ConfidencePublicDTO,
    EventDetailDTO,
    EventListItemDTO,
    FactPublicDTO,
    LocationPublicDTO,
    PaginationMeta,
    RelatedEventPublicDTO,
    SourcePublicDTO,
    TimelinePublicDTO,
)

logger = logging.getLogger(__name__)


class EventRepository:
    """Queries events with spatial bounding boxes, full-text search, and related details."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._confidence_engine = ConfidenceScoringEngine()

    def list_events(
        self,
        bbox: Optional[str] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        province: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        min_sources: int = 1,
        min_articles: int = 1,
        page: int = 1,
        limit: int = 50,
    ) -> Tuple[List[EventListItemDTO], PaginationMeta]:
        """Query events with spatial and temporal filters."""
        conditions = [Event.status != "ARCHIVED"]

        if from_time:
            conditions.append(Event.occurred_at >= from_time)
        if to_time:
            conditions.append(Event.occurred_at <= to_time)

        if province:
            conditions.append(Event.location_label.ilike(f"%{province.strip()}%"))

        if category:
            cats = [c.strip().upper() for c in category.split(",") if c.strip()]
            if len(cats) == 1:
                conditions.append(Event.category == cats[0])
            elif len(cats) > 1:
                conditions.append(Event.category.in_(cats))

        if status:
            conditions.append(Event.status == status.strip().upper())

        if min_sources > 1:
            conditions.append(Event.source_count >= min_sources)

        if min_articles > 1:
            conditions.append(Event.article_count >= min_articles)

        # Spatial bounding box: minLng,minLat,maxLng,maxLat
        if bbox:
            try:
                parts = [float(p.strip()) for p in bbox.split(",")]
                if len(parts) == 4:
                    min_lng, min_lat, max_lng, max_lat = parts
                    envelope = func.ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
                    conditions.append(func.ST_Intersects(Event.geom, envelope))
            except Exception as e:
                logger.warning("Invalid bbox format '%s': %s", bbox, e)

        # Total count query
        count_stmt = select(func.count(Event.id)).where(and_(*conditions))
        total = self._session.scalar(count_stmt) or 0

        # Paginated items
        safe_page = max(1, page)
        safe_limit = max(1, min(100, limit))
        offset = (safe_page - 1) * safe_limit

        items_stmt = (
            select(Event)
            .where(and_(*conditions))
            .order_by(Event.last_updated_at.desc())
            .offset(offset)
            .limit(safe_limit)
        )
        events = self._session.scalars(items_stmt).all()

        items = [
            EventListItemDTO(
                id=ev.id,
                title=ev.title,
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
            )
            for ev in events
        ]

        total_pages = math.ceil(total / safe_limit) if total > 0 else 1
        meta = PaginationMeta(
            page=safe_page,
            limit=safe_limit,
            total=total,
            total_pages=total_pages,
        )
        return items, meta

    def get_event_detail(self, event_id: UUID) -> Optional[EventDetailDTO]:
        """Fetch complete event representation including sources, timeline, and facts."""
        event = self._session.get(Event, event_id)
        if not event:
            return None

        # 1. Sources via EventArticle
        sources_stmt = (
            select(Source.name, Article.title, Article.url, Article.published_at)
            .join(Article, Article.source_id == Source.id)
            .join(EventArticle, EventArticle.article_id == Article.id)
            .where(EventArticle.event_id == event_id)
            .order_by(Article.published_at.asc())
        )
        sources_raw = self._session.execute(sources_stmt).all()
        sources = [
            SourcePublicDTO(
                source_name=row[0],
                article_title=row[1],
                original_url=row[2],
                published_at=row[3],
                source_type="MAJOR_NEWS",
            )
            for row in sources_raw
        ]

        # 2. Timeline
        timeline_stmt = (
            select(EventTimeline)
            .where(EventTimeline.event_id == event_id)
            .order_by(EventTimeline.timestamp.asc())
        )
        timelines_raw = self._session.scalars(timeline_stmt).all()
        timeline = [
            TimelinePublicDTO(
                timestamp=t.timestamp,
                type=t.timeline_type,
                text=t.text,
                source_article_id=t.source_article_id,
            )
            for t in timelines_raw
        ]

        # 3. Facts
        facts_stmt = (
            select(EventFact)
            .where(EventFact.event_id == event_id)
            .order_by(EventFact.fact_confidence.desc())
        )
        facts_raw = self._session.scalars(facts_stmt).all()
        facts = [
            FactPublicDTO(
                key=f.fact_key,
                value=f.fact_value,
                confidence=f.fact_confidence,
                supporting_articles=f.supporting_article_count,
            )
            for f in facts_raw
        ]

        # 4. Confidence breakdown
        time_span = abs((event.last_updated_at - event.first_reported_at).total_seconds()) / 3600.0
        has_conflicts = any(f.confidence < 0.60 for f in facts)
        has_official = any(t.type == "OFFICIAL_STATEMENT" for t in timeline)
        confidence_dto = self._confidence_engine.calculate_confidence(
            source_count=event.source_count,
            location_confidence=event.location_confidence,
            has_conflicts=has_conflicts,
            time_span_hours=time_span,
            has_official_source=has_official,
        )

        confidence_pub = ConfidencePublicDTO(
            score=confidence_dto.score,
            level=confidence_dto.level,
            factors=confidence_dto.factors,
            positive_indicators=confidence_dto.positive_indicators,
            warning_indicators=confidence_dto.warning_indicators,
        )

        # 5. Related events (same category within +/- 7 days, excluding self)
        related_stmt = (
            select(Event)
            .where(
                and_(
                    Event.id != event_id,
                    Event.category == event.category,
                    Event.status != "ARCHIVED",
                )
            )
            .order_by(Event.occurred_at.desc())
            .limit(5)
        )
        related_raw = self._session.scalars(related_stmt).all()
        related_events = [
            RelatedEventPublicDTO(
                id=r.id,
                title=r.title,
                category=r.category,
                occurred_at=r.occurred_at,
            )
            for r in related_raw
        ]

        return EventDetailDTO(
            id=event.id,
            title=event.title,
            category=event.category,
            status=event.status,
            summary=event.summary,
            location=LocationPublicDTO(
                latitude=event.latitude,
                longitude=event.longitude,
                label=event.location_label,
                confidence=event.location_confidence,
                is_approximate=event.location_confidence < 0.50,
            ),
            occurred_at=event.occurred_at,
            first_reported_at=event.first_reported_at,
            last_updated_at=event.last_updated_at,
            article_count=event.article_count,
            source_count=event.source_count,
            confidence=confidence_pub,
            sources=sources,
            timeline=timeline,
            facts=facts,
            related_events=related_events,
        )

    def search_events(
        self,
        q: str,
        province: Optional[str] = None,
        category: Optional[str] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[EventListItemDTO], PaginationMeta]:
        """Search events across title, summary, and location with relevance ranking."""
        clean_q = q.strip()
        conditions = [
            Event.status != "ARCHIVED",
            or_(
                Event.title.ilike(f"%{clean_q}%"),
                Event.summary.ilike(f"%{clean_q}%"),
                Event.location_label.ilike(f"%{clean_q}%"),
            ),
        ]

        if province:
            conditions.append(Event.location_label.ilike(f"%{province.strip()}%"))
        if category:
            conditions.append(Event.category == category.strip().upper())
        if from_time:
            conditions.append(Event.occurred_at >= from_time)
        if to_time:
            conditions.append(Event.occurred_at <= to_time)

        # Count
        count_stmt = select(func.count(Event.id)).where(and_(*conditions))
        total = self._session.scalar(count_stmt) or 0

        safe_page = max(1, page)
        safe_limit = max(1, min(50, limit))
        offset = (safe_page - 1) * safe_limit

        # Relevance order: exact title match > partial title > summary
        relevance = case(
            (Event.title.ilike(f"%{clean_q}%"), 3),
            (Event.location_label.ilike(f"%{clean_q}%"), 2),
            else_=1,
        )

        search_stmt = (
            select(Event)
            .where(and_(*conditions))
            .order_by(relevance.desc(), Event.last_updated_at.desc())
            .offset(offset)
            .limit(safe_limit)
        )
        events = self._session.scalars(search_stmt).all()

        items = [
            EventListItemDTO(
                id=ev.id,
                title=ev.title,
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
            )
            for ev in events
        ]

        total_pages = math.ceil(total / safe_limit) if total > 0 else 1
        meta = PaginationMeta(
            page=safe_page,
            limit=safe_limit,
            total=total,
            total_pages=total_pages,
        )
        return items, meta
