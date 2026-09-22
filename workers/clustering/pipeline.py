"""Event clustering pipeline for candidate retrieval, scoring, and provenance linking."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from backend.app.common.db.models.article import Article
from backend.app.common.db.models.event import Event
from backend.app.common.db.models.event_article import EventArticle
from backend.app.common.db.models.location import Location
from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.schemas import JobPayload, JobType, QueueName
from backend.app.modules.clustering.candidate_retriever import ClusteringCandidateRetriever
from backend.app.modules.clustering.schemas import ClusteringDecision
from backend.app.modules.clustering.scorer import ClusteringScorer

logger = logging.getLogger(__name__)


class ClusteringPipeline:
    """Orchestrates candidate retrieval, scoring, event merging, and provenance persistence."""

    def __init__(
        self,
        session: Session,
        retriever: Optional[ClusteringCandidateRetriever] = None,
        scorer: Optional[ClusteringScorer] = None,
        queue_manager: Optional[QueueManager] = None,
    ) -> None:
        self._session = session
        self._retriever = retriever or ClusteringCandidateRetriever(session)
        self._scorer = scorer or ClusteringScorer()
        self._queue_mgr = queue_manager

    def process_article_clustering(self, article_id: UUID) -> bool:
        """Evaluate article, merge into existing event or create new event with full provenance."""
        article = self._session.get(Article, article_id)
        if not article:
            logger.warning("Article %s not found for clustering", article_id)
            return False

        # Extract article features
        extraction = article.raw_metadata.get("extraction", {})
        title = extraction.get("title") or article.title
        category = extraction.get("event_type") or extraction.get("category") or "OTHER"
        entities = extraction.get("entities", [])
        facts = extraction.get("key_facts", [])

        # Parse occurred time
        occurred_str = extraction.get("occurred_at")
        if occurred_str:
            try:
                occurred_at = datetime.fromisoformat(occurred_str)
            except Exception:
                occurred_at = article.published_at
        else:
            occurred_at = article.published_at

        # Spatial data from location resolution
        location_id_str = article.raw_metadata.get("location_id")
        location: Optional[Location] = None
        if location_id_str:
            try:
                location = self._session.get(Location, UUID(location_id_str))
            except Exception:
                location = None

        lat = location.latitude if location else None
        lng = location.longitude if location else None
        province = location.province if location else extraction.get("province")
        location_label = location.address or location.raw_text if location else extraction.get("location_text")
        location_confidence = location.confidence if location else 0.40

        # Retrieve candidate events
        candidates = self._retriever.retrieve_candidates(
            reference_time=occurred_at,
            category=category,
            latitude=lat,
            longitude=lng,
            province=province,
            limit=25,
        )

        # Score candidates
        decision_dto = self._scorer.select_best_match(
            art_title=title,
            art_category=category,
            art_time=occurred_at,
            candidates=candidates,
            art_lat=lat,
            art_lng=lng,
            art_province=province,
            art_entities=[e.get("name", str(e)) if isinstance(e, dict) else str(e) for e in entities],
            art_facts=facts,
        )

        event: Optional[Event] = None
        if decision_dto.decision == ClusteringDecision.MERGE and decision_dto.target_event_id:
            # 1. Merge into target event
            event = self._session.get(Event, decision_dto.target_event_id)
            if event:
                logger.info(
                    "Merging article %s into existing event %s (score=%.2f, reason=%s)",
                    article_id,
                    event.id,
                    decision_dto.composite_score,
                    decision_dto.match_reason,
                )
                self._attach_article_to_event(
                    event=event,
                    article=article,
                    match_score=decision_dto.composite_score,
                    match_reason=decision_dto.match_reason,
                    location=location,
                )
        else:
            # 2. Create new event
            logger.info(
                "Creating new event for article %s (reason=%s)",
                article_id,
                decision_dto.match_reason,
            )
            event = self._create_new_event(
                article=article,
                title=title,
                category=category,
                occurred_at=occurred_at,
                location=location,
                location_label=location_label,
                location_confidence=location_confidence,
            )

        if event and self._queue_mgr:
            # Enqueue summary task
            summary_job = JobPayload(
                job_type=JobType.SUMMARY.value,
                entity_id=str(event.id),
                payload={"event_id": str(event.id)},
                idempotency_key=f"summary_{event.id}_{event.article_count}",
            )
            self._queue_mgr.enqueue(QueueName.SUMMARY, summary_job)

        self._session.commit()
        return True

    def _attach_article_to_event(
        self,
        event: Event,
        article: Article,
        match_score: float,
        match_reason: str,
        location: Optional[Location] = None,
    ) -> None:
        # Check idempotency
        stmt = select(EventArticle).where(
            EventArticle.event_id == event.id,
            EventArticle.article_id == article.id,
        )
        existing_assoc = self._session.scalars(stmt).first()
        if not existing_assoc:
            assoc = EventArticle(
                event_id=event.id,
                article_id=article.id,
                match_score=match_score,
                match_reason=match_reason,
            )
            self._session.add(assoc)
            self._session.flush()

        # Update event counters
        event.article_count += 1
        # Distinct source count
        src_stmt = (
            select(func.count(distinct(Article.source_id)))
            .join(EventArticle, EventArticle.article_id == Article.id)
            .where(EventArticle.event_id == event.id)
        )
        distinct_sources = self._session.scalar(src_stmt) or 1
        event.source_count = distinct_sources

        # Update timestamps
        if article.published_at > event.last_updated_at:
            event.last_updated_at = article.published_at

        # Update event status
        if event.status == "NEW":
            event.status = "DEVELOPING"
        elif event.status != "ARCHIVED":
            event.status = "UPDATED"

        # If incoming article location has higher confidence, promote its coordinates
        if location and location.confidence > event.location_confidence:
            event.latitude = location.latitude
            event.longitude = location.longitude
            event.location_label = location.address or location.raw_text
            event.location_confidence = location.confidence
            event.geom = f"SRID=4326;POINT({location.longitude} {location.latitude})"

    def _create_new_event(
        self,
        article: Article,
        title: str,
        category: str,
        occurred_at: datetime,
        location: Optional[Location] = None,
        location_label: Optional[str] = None,
        location_confidence: float = 0.5,
    ) -> Event:
        if location:
            lat = location.latitude
            lng = location.longitude
            geom_wkt = f"SRID=4326;POINT({lng} {lat})"
            conf = location.confidence
            label = location.address or location.raw_text
        else:
            # Default to center of Vietnam
            lat = 16.0544
            lng = 108.2022
            geom_wkt = f"SRID=4326;POINT({lng} {lat})"
            conf = 0.10
            label = location_label or "Việt Nam"

        event = Event(
            title=title,
            normalized_title=title.lower().strip(),
            category=category.upper(),
            summary=article.summary_raw or title,
            latitude=lat,
            longitude=lng,
            location_label=label,
            location_confidence=conf,
            geom=geom_wkt,
            occurred_at=occurred_at,
            first_reported_at=article.published_at,
            last_updated_at=article.published_at,
            status="NEW",
            confidence_score=0.5,
            article_count=1,
            source_count=1,
        )
        self._session.add(event)
        self._session.flush()

        # Link article
        assoc = EventArticle(
            event_id=event.id,
            article_id=article.id,
            match_score=1.0,
            match_reason="Initial event creator",
        )
        self._session.add(assoc)
        self._session.flush()
        return event
