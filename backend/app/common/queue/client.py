"""Asynchronous Redis-backed job queue manager and retry mechanics.

Strictly complies with:
- docs/03-backend-architecture.md (Idempotency, Error handling)
- docs/05-ingestion-pipeline.md (Queue semantics, Exponential backoff)
- tasks/TASK-005-redis-queue-foundation.md
"""

from __future__ import annotations

import logging
from typing import Optional

import redis

from backend.app.common.cache.redis import get_redis_client
from backend.app.common.queue.schemas import JobPayload, QueueName

logger = logging.getLogger(__name__)

IDEMPOTENCY_PREFIX = "vnm:idempotency:"


class QueueManager:
    """Manages enqueueing, dequeueing, idempotency checks, and dead-letter queue routing."""

    def __init__(self, client: Optional[redis.Redis] = None):
        self.client = client or get_redis_client()

    def _idempotency_key(self, key: str) -> str:
        return f"{IDEMPOTENCY_PREFIX}{key}"

    def is_idempotent(self, idempotency_key: str) -> bool:
        """Check if an idempotency key is already registered."""
        return bool(self.client.exists(self._idempotency_key(idempotency_key)))

    def enqueue(
        self,
        queue_name: QueueName,
        job: JobPayload,
        ttl_idempotency_seconds: int = 3600,
    ) -> bool:
        """Enqueue a job payload into the target named queue.

        If the job carries an idempotency_key that was already processed within the
        TTL window, the operation safely deduplicates and returns False.
        """
        if job.idempotency_key:
            redis_key = self._idempotency_key(job.idempotency_key)
            # Atomically set if not exists (NX) with expiry (EX)
            acquired = self.client.set(
                redis_key, job.job_id, ex=ttl_idempotency_seconds, nx=True
            )
            if not acquired:
                logger.info(
                    "Job deduplicated: idempotency_key '%s' already registered",
                    job.idempotency_key,
                )
                return False

        self.client.rpush(queue_name.value, job.to_json())
        return True

    def dequeue(
        self, queue_name: QueueName, timeout_seconds: int = 0
    ) -> Optional[JobPayload]:
        """Pop the next job payload from the named queue (FIFO order).

        If timeout_seconds > 0, performs a blocking pop (BLPOP).
        """
        if timeout_seconds > 0:
            result = self.client.blpop(queue_name.value, timeout=timeout_seconds)
            if not result:
                return None
            _, raw_payload = result
        else:
            raw_payload = self.client.lpop(queue_name.value)
            if not raw_payload:
                return None

        try:
            return JobPayload.from_json(raw_payload)
        except Exception as exc:
            logger.error("Malformed queue message popped from %s: %s", queue_name.value, exc)
            # Route corrupt payload directly to Dead-Letter Queue for inspection
            self.client.rpush(
                QueueName.DEAD_LETTER.value,
                JobPayload(
                    job_type="corrupt_payload",
                    payload={"raw": str(raw_payload)},
                    error_message=f"Deserialization failed: {exc}",
                ).to_json(),
            )
            return None

    def retry(
        self,
        queue_name: QueueName,
        job: JobPayload,
        error: Exception | str,
    ) -> bool:
        """Handle task execution failure.

        Increments the attempt counter. If attempts reach max_attempts, routes the job
        to the DEAD_LETTER queue and returns False. Otherwise, re-enqueues to the original
        queue and returns True.
        """
        job.attempt += 1
        job.error_message = str(error)

        if job.attempt >= job.max_attempts:
            logger.warning(
                "Job %s exhausted max_attempts (%d/%d). Routing to DLQ.",
                job.job_id,
                job.attempt,
                job.max_attempts,
            )
            self.client.rpush(QueueName.DEAD_LETTER.value, job.to_json())
            return False

        # Re-enqueue for retry
        logger.info(
            "Re-enqueueing job %s (attempt %d/%d) to %s",
            job.job_id,
            job.attempt,
            job.max_attempts,
            queue_name.value,
        )
        self.client.rpush(queue_name.value, job.to_json())
        return True

    def get_queue_length(self, queue_name: QueueName) -> int:
        """Return the current number of pending items in the named queue."""
        return int(self.client.llen(queue_name.value))

    def clear_queue(self, queue_name: QueueName) -> None:
        """Clear all messages from the specified queue (useful in tests and maintenance)."""
        self.client.delete(queue_name.value)
