"""Clustering worker consuming jobs from clustering_queue."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.schemas import JobPayload
from workers.clustering.pipeline import ClusteringPipeline

logger = logging.getLogger(__name__)


class ClusteringWorker:
    """Worker consuming clustering jobs to group articles into single-marker events."""

    def __init__(self, pipeline: Optional[ClusteringPipeline] = None) -> None:
        self._pipeline = pipeline

    def process_job(
        self,
        job: JobPayload,
        session: Session,
        queue_manager: Optional[QueueManager] = None,
    ) -> bool:
        """Process a single article clustering job."""
        article_id_str = job.payload.get("article_id") or job.entity_id
        if not article_id_str:
            raise ValueError(f"Clustering job {job.job_id} missing article_id")

        article_id = UUID(article_id_str)
        pipeline = self._pipeline or ClusteringPipeline(session, queue_manager=queue_manager)

        logger.info("Executing clustering evaluation for article %s", article_id)
        return pipeline.process_article_clustering(article_id)
