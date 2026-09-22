"""Source domain management service."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.common.db.models.source import Source
from backend.app.modules.sources.repository import SourceRepository
from backend.app.modules.sources.schemas import SourceCreateRequest, SourceUpdateRequest

logger = logging.getLogger(__name__)


class SourceService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = SourceRepository(session)

    def register_source(self, data: SourceCreateRequest) -> Source:
        """Register a new news publisher source."""
        existing = self.repo.get_by_domain(data.domain)
        if existing:
            raise ValueError(f"Source with domain '{data.domain}' already exists.")

        source = Source(
            name=data.name,
            domain=data.domain,
            source_type=data.source_type,
            rss_url=data.rss_url,
            active=data.active,
            priority=data.priority,
        )
        return self.repo.create(source)

    def update_source(self, source_id: UUID, data: SourceUpdateRequest) -> Source:
        """Update existing source configuration."""
        source = self.repo.get_by_id(source_id)
        if not source:
            raise ValueError(f"Source '{source_id}' not found.")

        update_fields = data.model_dump(exclude_unset=True)
        for key, value in update_fields.items():
            setattr(source, key, value)

        return self.repo.update(source)

    def toggle_source_status(self, source_id: UUID, active: bool) -> Source:
        """Enable or disable a source. Disabling immediately stops all crawls."""
        source = self.repo.get_by_id(source_id)
        if not source:
            raise ValueError(f"Source '{source_id}' not found.")

        source.active = active
        updated = self.repo.update(source)
        logger.info(
            "Source '%s' (%s) active status changed to %s",
            source.name,
            source.domain,
            active,
        )
        return updated

    def get_active_sources(self) -> list[Source]:
        """Fetch all active sources ordered by priority."""
        return self.repo.get_active_sources()

    def get_all_sources(self) -> list[Source]:
        """Fetch all configured sources."""
        return self.repo.list_all()

    def get_source_by_id(self, source_id: UUID) -> Optional[Source]:
        """Fetch source by UUID."""
        return self.repo.get_by_id(source_id)

    def record_source_crawl_result(
        self,
        source_id: UUID,
        success: bool,
        error_msg: Optional[str] = None,
    ) -> Optional[Source]:
        """Record the outcome of a crawl job."""
        return self.repo.record_crawl_result(source_id, success, error_msg)
