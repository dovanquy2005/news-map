"""Source polling scheduler dispatching feed crawl jobs with distributed locking."""

from __future__ import annotations

import logging
import random
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.common.cache.redis import get_redis_client
from backend.app.common.db.connection import get_db_session
from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.lock import DistributedLock
from backend.app.common.queue.schemas import JobPayload, QueueName
from backend.app.modules.sources.service import SourceService
from workers.ingestion.health import CircuitBreaker

logger = logging.getLogger(__name__)

SCHEDULER_LOCK_KEY = "vnm:lock:source_scheduler"
SCHEDULER_LOCK_TTL_SECONDS = 50
DEFAULT_POLL_INTERVAL_MINUTES = 10


class SourceScheduler:
    """Dispatches feed ingestion jobs to ingestion_queue under a distributed lock."""

    def __init__(
        self,
        queue_manager: Optional[QueueManager] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ) -> None:
        self.redis_client = get_redis_client()
        self.queue_manager = queue_manager or QueueManager(self.redis_client)
        self.circuit_breaker = circuit_breaker or CircuitBreaker(failure_threshold=5)

    def is_source_due(
        self,
        last_success_at: Optional[datetime],
        poll_interval_minutes: int = DEFAULT_POLL_INTERVAL_MINUTES,
        now: Optional[datetime] = None,
        jitter_seconds: int = 0,
    ) -> bool:
        """Determines if enough time has passed since last success/crawl."""
        if last_success_at is None:
            return True
        if now is None:
            now = datetime.now(timezone.utc)

        interval = timedelta(minutes=poll_interval_minutes) + timedelta(seconds=jitter_seconds)
        return (now - last_success_at) >= interval

    def run_dispatch_cycle(self, db_session: Optional[Session] = None) -> int:
        """Runs a single scheduler dispatch pass under distributed lock.

        Returns the number of jobs enqueued.
        """
        lock = DistributedLock(
            self.redis_client,
            SCHEDULER_LOCK_KEY,
            ttl_seconds=SCHEDULER_LOCK_TTL_SECONDS,
        )

        if not lock.acquire():
            logger.info("Scheduler lock held by another instance. Skipping cycle.")
            return 0

        dispatched_count = 0
        try:
            now = datetime.now(timezone.utc)
            if db_session is not None:
                dispatched_count = self._dispatch_with_session(db_session, now)
            else:
                with get_db_session() as session:
                    dispatched_count = self._dispatch_with_session(session, now)
        finally:
            lock.release()

        logger.info("Scheduler cycle finished. Dispatched %d ingestion jobs.", dispatched_count)
        return dispatched_count

    def _dispatch_with_session(self, session: Session, now: datetime) -> int:
        service = SourceService(session)
        active_sources = service.get_active_sources()
        dispatched = 0

        for source in active_sources:
            if not source.rss_url:
                continue

            # Check eligibility and apply +/- 30s jitter
            jitter = random.randint(-30, 30)
            if not self.is_source_due(source.last_success_at, now=now, jitter_seconds=jitter):
                continue

            # Deterministic idempotency key per source and 5-minute time block
            time_bucket = int(now.timestamp()) // 300
            idempotency_key = f"source_poll_{source.id}_{time_bucket}"

            from backend.app.common.queue.schemas import JobType

            job = JobPayload(
                job_type=JobType.INGESTION.value,
                idempotency_key=idempotency_key,
                payload={
                    "source_id": str(source.id),
                    "domain": source.domain,
                    "rss_url": source.rss_url,
                    "priority": source.priority,
                },
            )

            enqueued = self.queue_manager.enqueue(QueueName.INGESTION, job)
            if enqueued:
                dispatched += 1
                logger.info(
                    "Dispatched ingestion job for source '%s' (%s)",
                    source.name,
                    source.domain,
                )

        return dispatched
