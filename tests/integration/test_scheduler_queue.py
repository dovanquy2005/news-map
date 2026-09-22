"""Integration tests for SourceScheduler queue dispatch and distributed locking."""

import unittest
from uuid import uuid4

from backend.app.common.cache.redis import get_redis_client
from backend.app.common.db.connection import get_db_session
from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.schemas import QueueName
from backend.app.modules.sources.schemas import SourceCreateRequest
from backend.app.modules.sources.service import SourceService
from workers.ingestion.scheduler import SourceScheduler


class TestSchedulerQueueIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.session_cm = get_db_session()
        self.db = self.session_cm.__enter__()
        self.redis_client = get_redis_client()
        self.queue_mgr = QueueManager(self.redis_client)
        self.scheduler = SourceScheduler(self.queue_mgr)

        # Clear ingestion queue for clean test
        self.redis_client.delete(QueueName.INGESTION.value)

    def tearDown(self) -> None:
        self.redis_client.delete(QueueName.INGESTION.value)
        self.db.rollback()
        self.session_cm.__exit__(None, None, None)

    def test_scheduler_dispatches_due_sources(self) -> None:
        service = SourceService(self.db)
        unique_domain = f"scheduler-test-{uuid4().hex[:8]}.vn"
        data = SourceCreateRequest(
            name="Scheduler Due Source",
            domain=unique_domain,
            rss_url=f"https://{unique_domain}/rss.xml",
            priority=99,
            active=True,
        )
        created = service.register_source(data)

        # Run scheduler dispatch
        dispatched = self.scheduler.run_dispatch_cycle(db_session=self.db)
        self.assertGreaterEqual(dispatched, 1)

        # Verify job is in Redis queue
        job = self.queue_mgr.dequeue(QueueName.INGESTION, timeout_seconds=1)
        self.assertIsNotNone(job)
        self.assertIn("source_id", job.payload)
        self.assertIn("rss_url", job.payload)


if __name__ == "__main__":
    unittest.main()
