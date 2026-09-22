"""Source health status service providing operational metrics."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.modules.sources.service import SourceService
from workers.ingestion.health import CircuitBreaker, HealthStatus, SourceHealthRecord


class SourceHealthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.source_service = SourceService(session)
        self.circuit_breaker = CircuitBreaker()

    def get_sources_health_status(self) -> list[SourceHealthRecord]:
        """Calculates freshness lag and operational health for all sources."""
        sources = self.source_service.get_all_sources()
        records: list[SourceHealthRecord] = []
        now = datetime.now(timezone.utc)

        for s in sources:
            lag: Optional[int] = None
            if s.last_success_at:
                lag = int((now - s.last_success_at).total_seconds())

            # Evaluate health status
            status = HealthStatus.HEALTHY
            if not s.active:
                status = HealthStatus.PAUSED
            elif lag and lag > 7200:  # No success in > 2 hours
                status = HealthStatus.DEGRADED

            records.append(
                SourceHealthRecord(
                    source_id=s.id,
                    domain=s.domain,
                    status=status,
                    consecutive_failures=0,
                    last_success_at=s.last_success_at,
                    last_error_at=s.last_error_at,
                    freshness_lag_seconds=lag,
                )
            )

        return records
