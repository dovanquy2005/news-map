"""Clustering worker task handler."""

from __future__ import annotations

import logging

from backend.app.common.db.connection import get_db_session
from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.schemas import JobPayload
from workers.clustering.worker import ClusteringWorker

logger = logging.getLogger("worker.clustering")

_WORKER = ClusteringWorker()


def handle_clustering_job(job: JobPayload) -> bool:
    """Consumes clustering job and merges article into event or creates new event."""
    logger.info("Processing clustering job %s (entity_id=%s)", job.job_id, job.entity_id)
    queue_mgr = QueueManager()
    with get_db_session() as session:
        return _WORKER.process_job(job, session, queue_manager=queue_mgr)
