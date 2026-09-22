"""Ingestion pipeline orchestrating fetch, normalize, dedup, persist, and enqueue."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.schemas import JobPayload, JobType, QueueName
from backend.app.modules.articles.deduplicator import ArticleDeduplicator
from backend.app.modules.articles.normalizer import ArticleNormalizer
from backend.app.modules.articles.repository import ArticleRepository
from backend.app.modules.articles.schemas import NormalizedArticleDTO
from backend.app.modules.sources.adapters.registry import AdapterRegistry
from backend.app.modules.sources.service import SourceService

logger = logging.getLogger(__name__)


@dataclass
class IngestionSummary:
    source_id: UUID
    source_name: str
    items_fetched: int
    items_unique: int
    items_duplicate: int
    jobs_enqueued: int
    success: bool
    error: Optional[str] = None


class IngestionPipeline:
    """End-to-end ingestion pipeline runner for a single source."""

    def __init__(self) -> None:
        self.normalizer = ArticleNormalizer()

    def process_source(
        self,
        source_id: UUID,
        session: Session,
        queue_manager: QueueManager,
    ) -> IngestionSummary:
        source_service = SourceService(session)
        source = source_service.get_source_by_id(source_id)

        if not source:
            logger.warning("Source %s not found. Aborting ingestion.", source_id)
            return IngestionSummary(
                source_id=source_id,
                source_name="Unknown",
                items_fetched=0,
                items_unique=0,
                items_duplicate=0,
                jobs_enqueued=0,
                success=False,
                error="Source not found",
            )

        if not source.active:
            logger.info("Source %s is inactive. Halting crawl.", source.domain)
            return IngestionSummary(
                source_id=source_id,
                source_name=source.name,
                items_fetched=0,
                items_unique=0,
                items_duplicate=0,
                jobs_enqueued=0,
                success=True,
            )

        # 1. Adapter fetch
        adapter = AdapterRegistry.get_adapter(source.source_type or "RSS")
        feed_result = adapter.fetch(source)

        if feed_result.error_message or feed_result.status_code >= 400:
            err = feed_result.error_message or f"HTTP status {feed_result.status_code}"
            logger.error("Feed fetch failed for %s: %s", source.domain, err)
            source_service.record_source_crawl_result(source.id, success=False, error_msg=err)
            return IngestionSummary(
                source_id=source_id,
                source_name=source.name,
                items_fetched=0,
                items_unique=0,
                items_duplicate=0,
                jobs_enqueued=0,
                success=False,
                error=err,
            )

        # 2. Normalize and Deduplicate
        deduplicator = ArticleDeduplicator(session)
        unique_dtos: list[NormalizedArticleDTO] = []
        dup_count = 0

        for raw_item in feed_result.items:
            norm = self.normalizer.normalize(raw_item, base_url=f"https://{source.domain}")
            decision = deduplicator.evaluate_article(norm)
            if decision.is_duplicate:
                dup_count += 1
            else:
                unique_dtos.append(norm)

        # 3. Batch insert unique articles
        article_repo = ArticleRepository(session)
        created_articles = article_repo.save_unique_articles(unique_dtos)

        # 4. Enqueue extraction jobs for each newly inserted article
        enqueued_count = 0
        for article in created_articles:
            job = JobPayload(
                job_type=JobType.EXTRACTION.value,
                entity_id=str(article.id),
                payload={
                    "article_id": str(article.id),
                    "source_id": str(source.id),
                    "title": article.title,
                },
                idempotency_key=f"extract_article_{article.id}",
            )
            ok = queue_manager.enqueue(QueueName.EXTRACTION, job)
            if ok:
                enqueued_count += 1

        # 5. Record successful crawl outcome
        source_service.record_source_crawl_result(source.id, success=True)

        logger.info(
            "Ingestion completed for '%s': fetched=%d, unique=%d, dup=%d, enqueued=%d",
            source.name,
            feed_result.item_count,
            len(created_articles),
            dup_count,
            enqueued_count,
        )

        return IngestionSummary(
            source_id=source.id,
            source_name=source.name,
            items_fetched=feed_result.item_count,
            items_unique=len(created_articles),
            items_duplicate=dup_count,
            jobs_enqueued=enqueued_count,
            success=True,
        )
