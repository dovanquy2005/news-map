"""Integration tests for ExtractionWorker fan-out to geocoding and clustering."""

from datetime import datetime, timezone
import unittest
from uuid import uuid4

from backend.app.common.cache.redis import get_redis_client
from backend.app.common.db.connection import get_db_session
from backend.app.common.db.models.article import Article
from backend.app.common.db.models.source import Source
from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.schemas import JobPayload, JobType, QueueName
from workers.extraction.handler import handle_extraction_job


class TestExtractionWorkerIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.session_cm = get_db_session()
        self.db = self.session_cm.__enter__()
        self.redis_client = get_redis_client()
        self.queue_mgr = QueueManager(self.redis_client)

        # Clear relevant queues
        self.redis_client.delete(QueueName.EXTRACTION.value)
        self.redis_client.delete(QueueName.GEOCODING.value)
        self.redis_client.delete(QueueName.CLUSTERING.value)

        # Create test source
        self.source = Source(
            name=f"Source Extraction Test {uuid4().hex[:6]}",
            domain=f"ext-{uuid4().hex[:6]}.vn",
            source_type="RSS",
            active=True,
        )
        self.db.add(self.source)
        self.db.commit()

        # Create test article
        self.article = Article(
            source_id=self.source.id,
            url=f"https://{self.source.domain}/post-1.html",
            canonical_url=f"https://{self.source.domain}/post-1.html",
            title=f"Khởi công tuyến đường sắt đô thị số 2 {uuid4().hex[:6]}",
            content_excerpt="UBND TP Hà Nội chính thức khởi công dự án tuyến đường sắt đô thị số 2 Nam Thăng Long - Trần Hưng Đạo.",
            content_hash=f"{uuid4().hex}{uuid4().hex}",
            published_at=datetime.now(timezone.utc),
        )
        self.db.add(self.article)
        self.db.commit()

    def tearDown(self) -> None:
        self.redis_client.delete(QueueName.EXTRACTION.value)
        self.redis_client.delete(QueueName.GEOCODING.value)
        self.redis_client.delete(QueueName.CLUSTERING.value)
        self.db.rollback()
        self.session_cm.__exit__(None, None, None)

    def test_extraction_worker_processes_and_fans_out(self) -> None:
        job = JobPayload(
            job_type=JobType.EXTRACTION.value,
            entity_id=str(self.article.id),
            payload={"article_id": str(self.article.id)},
        )

        success = handle_extraction_job(job)
        self.assertTrue(success)

        # 1. Verify article metadata updated with extraction
        with get_db_session() as db:
            art = db.query(Article).filter(Article.id == self.article.id).first()
            self.assertIsNotNone(art)
            self.assertIn("extraction", art.raw_metadata)
            extraction_data = art.raw_metadata["extraction"]
            self.assertTrue(extraction_data["is_event"])
            self.assertIn("event_type", extraction_data)

        # 2. Verify geocoding job arrived
        geocode_job = self.queue_mgr.dequeue(QueueName.GEOCODING, timeout_seconds=1)
        self.assertIsNotNone(geocode_job)
        self.assertEqual(geocode_job.job_type, JobType.GEOCODING.value)
        self.assertEqual(geocode_job.entity_id, str(self.article.id))

        # 3. Verify clustering job arrived
        cluster_job = self.queue_mgr.dequeue(QueueName.CLUSTERING, timeout_seconds=1)
        self.assertIsNotNone(cluster_job)
        self.assertEqual(cluster_job.job_type, JobType.CLUSTERING.value)
        self.assertEqual(cluster_job.entity_id, str(self.article.id))


if __name__ == "__main__":
    unittest.main()
