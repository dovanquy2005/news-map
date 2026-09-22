"""Geocoding worker task handler."""

from __future__ import annotations

import logging

from backend.app.common.db.connection import get_db_session
from backend.app.common.queue.schemas import JobPayload
from workers.geocoding.worker import GeocodingWorker

logger = logging.getLogger("worker.geocoding")

_WORKER = GeocodingWorker()


def handle_geocoding_job(job: JobPayload) -> bool:
    """Consumes geocoding job and resolves location for article."""
    logger.info("Processing geocoding job %s (entity_id=%s)", job.job_id, job.entity_id)
    with get_db_session() as session:
        return _WORKER.process_job(job, session)
