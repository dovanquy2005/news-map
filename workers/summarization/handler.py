"""Summarization worker task handler."""

from __future__ import annotations

import logging

from backend.app.common.db.connection import get_db_session
from backend.app.common.queue.schemas import JobPayload
from workers.summarization.worker import SummaryWorker

logger = logging.getLogger("worker.summarization")

_WORKER = SummaryWorker()


def handle_summarization_job(job: JobPayload) -> bool:
    """Consumes summarization job and updates event summary and confidence."""
    logger.info("Processing summarization job %s (entity_id=%s)", job.job_id, job.entity_id)
    with get_db_session() as session:
        return _WORKER.process_job(job, session)
