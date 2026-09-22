"""Ingestion worker task handler."""

from __future__ import annotations

import logging

from backend.app.common.db.connection import get_db_session
from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.schemas import JobPayload
from workers.ingestion.worker import IngestSourceWorker

logger = logging.getLogger("worker.ingestion")

_WORKER = IngestSourceWorker()


def handle_ingestion_job(job: JobPayload) -> bool:
    """Process an ingestion job (RSS poll, article fetch, normalize, dedup, persist, enqueue)."""
    logger.info("Processing ingestion job %s (type=%s)", job.job_id, job.job_type)
    queue_mgr = QueueManager()
    with get_db_session() as session:
        summary = _WORKER.process_job(job, session, queue_mgr)
        logger.info(
            "Completed ingestion for source %s: %d new articles saved, %d jobs enqueued",
            summary.source_id,
            summary.items_unique,
            summary.jobs_enqueued,
        )
    return True
