"""Ingestion worker executing feed ingestion jobs from the queue."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.schemas import JobPayload
from workers.ingestion.pipeline import IngestionPipeline, IngestionSummary

logger = logging.getLogger(__name__)


class IngestSourceWorker:
    """Worker task handler executing IngestSourceJob."""

    def __init__(self) -> None:
        self.pipeline = IngestionPipeline()

    def process_job(
        self,
        job: JobPayload,
        session: Session,
        queue_manager: QueueManager,
    ) -> IngestionSummary:
        """Processes an incoming ingestion queue payload."""
        source_id_str = job.payload.get("source_id") or job.entity_id
        if not source_id_str:
            raise ValueError(f"Job {job.job_id} missing required 'source_id' field")

        source_id = UUID(source_id_str)
        summary = self.pipeline.process_source(source_id, session, queue_manager)

        if not summary.success and summary.error:
            raise RuntimeError(f"Ingestion failed for source {source_id}: {summary.error}")

        return summary
