"""Event summary and confidence scoring worker."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.common.db.models.article import Article
from backend.app.common.db.models.event import Event
from backend.app.common.db.models.event_article import EventArticle
from backend.app.common.db.models.source import Source
from backend.app.common.queue.schemas import JobPayload
from backend.app.modules.events.confidence import ConfidenceScoringEngine
from backend.app.modules.events.facts_service import EventFactsService
from backend.app.modules.events.timeline_service import EventTimelineService
from workers.summarization.generator import SummaryGenerator

logger = logging.getLogger(__name__)


class SummaryWorker:
    """Worker processing event summarization and confidence recalculation."""

    def __init__(
        self,
        generator: Optional[SummaryGenerator] = None,
        timeline_service: Optional[EventTimelineService] = None,
        facts_service: Optional[EventFactsService] = None,
        confidence_engine: Optional[ConfidenceScoringEngine] = None,
    ) -> None:
        self._generator = generator or SummaryGenerator()
        self._confidence_engine = confidence_engine or ConfidenceScoringEngine()

    def process_job(self, job: JobPayload, session: Session) -> bool:
        """Process event summary generation and confidence scoring."""
        event_id_str = job.payload.get("event_id") or job.entity_id
        if not event_id_str:
            raise ValueError(f"Summary job {job.job_id} missing event_id")

        event_id = UUID(event_id_str)
        event = session.get(Event, event_id)
        if not event:
            logger.warning("Event %s not found for summary generation", event_id)
            return False

        timeline_svc = EventTimelineService(session)
        facts_svc = EventFactsService(session)

        # 1. Rebuild timeline milestones
        timeline_entries = timeline_svc.rebuild_timeline(event_id)

        # 2. Re-aggregate facts and detect conflicts
        event_facts = facts_svc.aggregate_facts(event_id)
        has_conflicts = any(f.fact_confidence < 0.60 for f in event_facts)

        # 3. Gathers source publisher names
        stmt = (
            select(Source.name)
            .join(Article, Article.source_id == Source.id)
            .join(EventArticle, EventArticle.article_id == Article.id)
            .where(EventArticle.event_id == event_id)
            .distinct()
        )
        source_names = list(session.scalars(stmt).all())

        # 4. Generate grounded summary
        fact_strings = [f"{f.fact_key}: {f.fact_value}" for f in event_facts]
        timeline_strings = [f"{t.timestamp.strftime('%H:%M %d/%m')}: {t.text}" for t in timeline_entries]

        summary_text = self._generator.generate(
            event_title=event.title,
            category=event.category,
            location_label=event.location_label or "Việt Nam",
            facts=fact_strings,
            timeline_items=timeline_strings,
            source_names=source_names,
        )

        event.summary = summary_text

        # 5. Compute explainable confidence score
        time_span = abs((event.last_updated_at - event.first_reported_at).total_seconds()) / 3600.0
        has_official = any(t.timeline_type == "OFFICIAL_STATEMENT" for t in timeline_entries)

        confidence_dto = self._confidence_engine.calculate_confidence(
            source_count=event.source_count,
            location_confidence=event.location_confidence,
            has_conflicts=has_conflicts,
            time_span_hours=time_span,
            has_official_source=has_official,
        )

        event.confidence_score = round(confidence_dto.score / 100.0, 2)

        session.commit()
        logger.info(
            "Event %s summary updated (confidence=%.2f, level=%s)",
            event_id,
            event.confidence_score,
            confidence_dto.level,
        )
        return True
