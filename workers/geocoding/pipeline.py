"""Geocoding processing pipeline for article location enrichment."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.common.db.models.article import Article
from backend.app.modules.locations.service import LocationService

logger = logging.getLogger(__name__)


class GeocodingPipeline:
    """Coordinates resolving location for an article and linking it to the article metadata."""

    def __init__(self, session: Session, location_service: Optional[LocationService] = None) -> None:
        self._session = session
        self._location_service = location_service or LocationService(session)

    def process_article_location(
        self,
        article_id: UUID,
        location_text: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        ward: Optional[str] = None,
    ) -> bool:
        """Process geocoding for an article and update its metadata."""
        article = self._session.get(Article, article_id)
        if not article:
            logger.warning("Article %s not found in database for geocoding", article_id)
            return False

        # If location_text was not in payload, check article raw_metadata
        if not location_text:
            extraction_meta = article.raw_metadata.get("extraction", {})
            location_text = extraction_meta.get("location_text")

        if not location_text or not location_text.strip():
            logger.info("Article %s has no location text. Marking UNRESOLVED.", article_id)
            meta = dict(article.raw_metadata)
            meta["geocoding"] = {"status": "UNRESOLVED", "confidence": 0.0}
            article.raw_metadata = meta
            self._session.flush()
            return True

        location, resolved = self._location_service.resolve_and_persist(
            raw_text=location_text,
            hint_province=province,
            hint_district=district,
            hint_ward=ward,
        )

        meta = dict(article.raw_metadata)
        if location and resolved:
            meta["location_id"] = str(location.id)
            meta["geocoding"] = resolved.model_dump()
            logger.info(
                "Article %s successfully linked to location %s (%s)",
                article_id,
                location.id,
                resolved.resolved_address,
            )
        else:
            meta["geocoding"] = {"status": "UNRESOLVED", "confidence": 0.0}
            logger.info("Article %s could not be geocoded", article_id)

        article.raw_metadata = meta
        self._session.flush()
        return True
