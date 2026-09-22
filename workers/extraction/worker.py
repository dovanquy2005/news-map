"""Extraction worker consuming articles from extraction_queue."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.schemas import JobPayload, JobType, QueueName
from workers.extraction.service import ExtractionService

logger = logging.getLogger(__name__)


class ExtractionWorker:
    """Consumes extraction jobs and fans out to geocoding and clustering queues."""

    def __init__(self, service: ExtractionService | None = None) -> None:
        self._service = service

    def process_job(
        self,
        job: JobPayload,
        session: Session,
        queue_manager: QueueManager,
    ) -> bool:
        article_id_str = job.payload.get("article_id") or job.entity_id
        if not article_id_str:
            raise ValueError(f"Job {job.job_id} missing article_id")

        article_id = UUID(article_id_str)
        service = self._service or ExtractionService(session)

        validated_dto = service.process_article(article_id)
        if not validated_dto:
            logger.info("Article %s yielded no event. Completing job.", article_id)
            return True

        if validated_dto.is_event:
            # 1. Enqueue Geocoding Job
            geocode_job = JobPayload(
                job_type=JobType.GEOCODING.value,
                entity_id=str(article_id),
                payload={
                    "article_id": str(article_id),
                    "location_text": validated_dto.location_text,
                    "province": validated_dto.province,
                    "district": validated_dto.district,
                    "ward": validated_dto.ward,
                },
                idempotency_key=f"geocode_{article_id}",
            )
            queue_manager.enqueue(QueueName.GEOCODING, geocode_job)

            # 2. Enqueue Clustering Job
            cluster_job = JobPayload(
                job_type=JobType.CLUSTERING.value,
                entity_id=str(article_id),
                payload={
                    "article_id": str(article_id),
                    "event_title": validated_dto.event_title,
                    "category": validated_dto.event_type.value,
                    "occurred_at": validated_dto.occurred_at.isoformat() if validated_dto.occurred_at else None,
                    "confidence_score": validated_dto.extraction_confidence,
                },
                idempotency_key=f"cluster_{article_id}",
            )
            queue_manager.enqueue(QueueName.CLUSTERING, cluster_job)

            logger.info(
                "Article %s dispatched to GEOCODING and CLUSTERING queues",
                article_id,
            )

        return True
