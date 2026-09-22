"""Extraction worker task handler."""

from __future__ import annotations

import logging

from backend.app.common.db.connection import get_db_session
from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.schemas import JobPayload
from workers.extraction.worker import ExtractionWorker

logger = logging.getLogger("worker.extraction")

_WORKER = ExtractionWorker()


def handle_extraction_job(job: JobPayload) -> bool:
    """Consumes extraction job, runs LLM extraction, and dispatches to geocoding/clustering."""
    logger.info("Processing extraction job %s (entity_id=%s)", job.job_id, job.entity_id)
    queue_mgr = QueueManager()
    with get_db_session() as session:
        return _WORKER.process_job(job, session, queue_mgr)
