"""Source health tracking and circuit-breaker logic."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    PAUSED = "PAUSED"


class SourceHealthRecord(BaseModel):
    source_id: UUID
    domain: str
    status: HealthStatus = HealthStatus.HEALTHY
    consecutive_failures: int = 0
    last_success_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    last_error_message: Optional[str] = None
    backoff_until: Optional[datetime] = None
    freshness_lag_seconds: Optional[int] = None


class CircuitBreaker:
    """Evaluates whether a source is healthy, degraded, or in exponential backoff."""

    def __init__(self, failure_threshold: int = 5) -> None:
        self.failure_threshold = failure_threshold

    def compute_backoff_duration(self, failures: int) -> timedelta:
        """Calculate exponential backoff: 5->1h, 6->4h, 7+->24h."""
        if failures < self.failure_threshold:
            return timedelta(seconds=0)
        elif failures == self.failure_threshold:
            return timedelta(hours=1)
        elif failures == self.failure_threshold + 1:
            return timedelta(hours=4)
        else:
            return timedelta(hours=24)

    def evaluate_status(
        self,
        consecutive_failures: int,
        last_success_at: Optional[datetime],
        now: Optional[datetime] = None,
    ) -> tuple[HealthStatus, Optional[datetime]]:
        """Determine health status and backoff expiration."""
        if now is None:
            now = datetime.now(timezone.utc)

        if consecutive_failures < 3:
            return HealthStatus.HEALTHY, None

        if consecutive_failures < self.failure_threshold:
            return HealthStatus.DEGRADED, None

        # Threshold exceeded -> PAUSED with exponential backoff
        backoff = self.compute_backoff_duration(consecutive_failures)
        backoff_until = now + backoff
        return HealthStatus.PAUSED, backoff_until

    def is_eligible_to_poll(
        self,
        consecutive_failures: int,
        backoff_until: Optional[datetime],
        now: Optional[datetime] = None,
    ) -> bool:
        """Check if source is eligible to poll (not in active backoff)."""
        if now is None:
            now = datetime.now(timezone.utc)

        if backoff_until and now < backoff_until:
            return False
        return True
