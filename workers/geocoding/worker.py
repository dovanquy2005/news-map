"""Geocoding worker consuming jobs from geocoding_queue."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.common.queue.schemas import JobPayload
from workers.geocoding.pipeline import GeocodingPipeline

logger = logging.getLogger(__name__)


class GeocodingWorker:
    """Worker consuming geocoding jobs, executing spatial resolution, and persisting location links."""

    def __init__(self, pipeline: Optional[GeocodingPipeline] = None) -> None:
        self._pipeline = pipeline

    def process_job(self, job: JobPayload, session: Session) -> bool:
        """Process a single geocoding job atomically."""
        article_id_str = job.payload.get("article_id") or job.entity_id
        if not article_id_str:
            raise ValueError(f"Geocoding job {job.job_id} missing article_id")

        article_id = UUID(article_id_str)
        location_text = job.payload.get("location_text")
        province = job.payload.get("province")
        district = job.payload.get("district")
        ward = job.payload.get("ward")

        pipeline = self._pipeline or GeocodingPipeline(session)

        logger.info(
            "Executing geocoding for article %s (location='%s', province='%s')",
            article_id,
            location_text,
            province,
        )

        success = pipeline.process_article_location(
            article_id=article_id,
            location_text=location_text,
            province=province,
            district=district,
            ward=ward,
        )

        session.commit()
        return success
