"""Source repository providing queries for active publishers and crawl recording."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.app.common.db.models.source import Source
from backend.app.common.db.repositories.base import BaseRepository


class SourceRepository(BaseRepository[Source]):
    def __init__(self, session: Session) -> None:
        super().__init__(Source, session)

    def get_active_sources(self) -> list[Source]:
        """Returns all enabled sources ordered by priority descending."""
        stmt = (
            select(Source)
            .where(Source.active.is_(True))
            .order_by(desc(Source.priority), Source.name)
        )
        return list(self.session.scalars(stmt).all())

    def get_by_domain(self, domain: str) -> Optional[Source]:
        """Look up a source by domain name."""
        stmt = select(Source).where(Source.domain == domain.strip().lower())
        return self.session.scalars(stmt).first()

    def record_crawl_result(
        self,
        source_id: UUID,
        success: bool,
        error_msg: Optional[str] = None,
    ) -> Optional[Source]:
        """Update last_success_at or last_error_at timestamps."""
        source = self.get_by_id(source_id)
        if not source:
            return None

        now = datetime.now(timezone.utc)
        if success:
            source.last_success_at = now
        else:
            source.last_error_at = now
        source.updated_at = now
        self.session.commit()
        self.session.refresh(source)
        return source
