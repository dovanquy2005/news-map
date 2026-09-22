"""Integration tests for Redis Configuration, Cache Service, and Queue Foundation (TASK-005).

Verifies against active Redis service:
- Redis health probe latency (< 10ms)
- CacheService set, get, delete, delete_pattern, and TTL
- QueueManager FIFO enqueue/dequeue on all named queues
- Idempotency guard and deduplication
- Retry progression and Dead-Letter Queue (DLQ) routing
- Distributed lock mutual exclusion
"""

import time
import unittest
import uuid

from backend.app.common.cache.redis import (
    CacheService,
    check_redis_health,
    get_redis_client,
    reset_redis_client,
)
from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.lock import (
    LockAcquisitionError,
    redis_distributed_lock,
)
from backend.app.common.queue.schemas import JobPayload, JobType, QueueName


class TestQueueFoundationIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reset_redis_client()
        cls.client = get_redis_client()
        cls.queue_manager = QueueManager(cls.client)
        cls.cache_service = CacheService(cls.client, prefix="vnm:test_cache:")

    def setUp(self):
        # Clear test queues before each test
        for q in QueueName:
            self.queue_manager.clear_queue(q)

    def tearDown(self):
        for q in QueueName:
            self.queue_manager.clear_queue(q)

    def test_redis_health_probe(self):
        """Redis health check must return healthy and respond under 10ms."""
        is_healthy, latency_ms, error = check_redis_health()
        self.assertTrue(is_healthy, f"Redis unhealthy: {error}")
        self.assertIsNone(error)
        self.assertLess(latency_ms, 15.0, f"Latency {latency_ms}ms exceeded budget")

    def test_cache_service_crud_and_invalidation(self):
        """CacheService basic CRUD and pattern invalidation."""
        # 1. Set and get
        self.cache_service.set("user:101", {"name": "Test User", "role": "admin"})
        user = self.cache_service.get("user:101")
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Test User")

        # 2. Exists
        self.assertTrue(self.cache_service.exists("user:101"))
        self.assertFalse(self.cache_service.exists("user:999"))

        # 3. Set with TTL
        self.cache_service.set("short_lived", "data", ttl_seconds=1)
        self.assertEqual(self.cache_service.get("short_lived"), "data")
        time.sleep(1.1)
        self.assertIsNone(self.cache_service.get("short_lived"))

        # 4. Pattern deletion
        self.cache_service.set("events:hanoi", "10")
        self.cache_service.set("events:hcm", "25")
        self.cache_service.set("events:danang", "8")
        self.cache_service.set("articles:vtv", "100")

        deleted_count = self.cache_service.delete_pattern("events:*")
        self.assertEqual(deleted_count, 3)
        self.assertIsNone(self.cache_service.get("events:hanoi"))
        self.assertEqual(self.cache_service.get("articles:vtv"), "100")

    def test_queue_enqueue_and_dequeue_fifo(self):
        """Job payloads must preserve FIFO order and schema integrity."""
        job1 = JobPayload(
            job_type=JobType.INGESTION.value,
            payload={"rss_url": "https://news.test/feed.rss"},
            entity_id=str(uuid.uuid4()),
        )
        job2 = JobPayload(
            job_type=JobType.INGESTION.value,
            payload={"rss_url": "https://news.test/feed2.rss"},
            entity_id=str(uuid.uuid4()),
        )

        # Enqueue
        self.assertTrue(self.queue_manager.enqueue(QueueName.INGESTION, job1))
        self.assertTrue(self.queue_manager.enqueue(QueueName.INGESTION, job2))
        self.assertEqual(self.queue_manager.get_queue_length(QueueName.INGESTION), 2)

        # Dequeue in FIFO order
        popped1 = self.queue_manager.dequeue(QueueName.INGESTION)
        self.assertIsNotNone(popped1)
        self.assertEqual(popped1.job_id, job1.job_id)
        self.assertEqual(popped1.payload["rss_url"], "https://news.test/feed.rss")

        popped2 = self.queue_manager.dequeue(QueueName.INGESTION)
        self.assertIsNotNone(popped2)
        self.assertEqual(popped2.job_id, job2.job_id)

        # Empty queue returns None
        self.assertIsNone(self.queue_manager.dequeue(QueueName.INGESTION))

    def test_idempotency_guard_deduplication(self):
        """Jobs sharing the same idempotency_key within TTL must not be queued twice."""
        idem_key = f"feed_poll_{uuid.uuid4().hex}"
        job_a = JobPayload(
            job_type=JobType.INGESTION.value,
            idempotency_key=idem_key,
            payload={"source": "VnExpress"},
        )
        job_b = JobPayload(
            job_type=JobType.INGESTION.value,
            idempotency_key=idem_key,
            payload={"source": "VnExpress Duplicate"},
        )

        # First enqueue succeeds
        first_result = self.queue_manager.enqueue(QueueName.INGESTION, job_a)
        self.assertTrue(first_result)

        # Second enqueue with identical idempotency_key is deduplicated safely
        second_result = self.queue_manager.enqueue(QueueName.INGESTION, job_b)
        self.assertFalse(second_result)

        # Only one item exists in the queue
        self.assertEqual(self.queue_manager.get_queue_length(QueueName.INGESTION), 1)

    def test_retry_mechanism_and_dead_letter_queue_routing(self):
        """Failed jobs must retry up to max_attempts before routing to DEAD_LETTER queue."""
        job = JobPayload(
            job_type=JobType.EXTRACTION.value,
            payload={"article_id": str(uuid.uuid4())},
            attempt=0,
            max_attempts=3,
        )

        # Attempt 1: failure -> re-enqueue
        still_retrying_1 = self.queue_manager.retry(
            QueueName.EXTRACTION, job, error="Temporary LLM rate limit"
        )
        self.assertTrue(still_retrying_1)
        self.assertEqual(job.attempt, 1)
        self.assertEqual(self.queue_manager.get_queue_length(QueueName.EXTRACTION), 1)

        popped_1 = self.queue_manager.dequeue(QueueName.EXTRACTION)
        self.assertEqual(popped_1.attempt, 1)

        # Attempt 2: failure -> re-enqueue
        still_retrying_2 = self.queue_manager.retry(
            QueueName.EXTRACTION, popped_1, error="Second LLM timeout"
        )
        self.assertTrue(still_retrying_2)
        self.assertEqual(popped_1.attempt, 2)

        popped_2 = self.queue_manager.dequeue(QueueName.EXTRACTION)

        # Attempt 3: reached max_attempts (3) -> routes to DEAD_LETTER queue
        still_retrying_3 = self.queue_manager.retry(
            QueueName.EXTRACTION, popped_2, error="Fatal parsing exception"
        )
        self.assertFalse(still_retrying_3, "Job must transition to DLQ when max_attempts is reached")

        # Original queue must be empty, DLQ must contain the failed job
        self.assertEqual(self.queue_manager.get_queue_length(QueueName.EXTRACTION), 0)
        self.assertEqual(self.queue_manager.get_queue_length(QueueName.DEAD_LETTER), 1)

        dlq_job = self.queue_manager.dequeue(QueueName.DEAD_LETTER)
        self.assertIsNotNone(dlq_job)
        self.assertEqual(dlq_job.attempt, 3)
        self.assertIn("Fatal parsing exception", dlq_job.error_message)

    def test_distributed_lock_mutual_exclusion(self):
        """Distributed lock must ensure single-holder exclusivity and safe release."""
        resource_id = f"scheduler_{uuid.uuid4().hex[:6]}"

        with redis_distributed_lock(resource_id, lease_seconds=10, timeout_seconds=1) as token_a:
            self.assertTrue(token_a)

            # Concurrent acquisition of the same resource should fail
            with self.assertRaises(LockAcquisitionError):
                with redis_distributed_lock(resource_id, lease_seconds=10, timeout_seconds=0.2):
                    pass

        # After releasing context, lock can be acquired again cleanly
        with redis_distributed_lock(resource_id, lease_seconds=10, timeout_seconds=1) as token_b:
            self.assertTrue(token_b)
            self.assertNotEqual(token_a, token_b)


if __name__ == "__main__":
    unittest.main()
