"""Integration test for full end-to-end ingestion pipeline."""

from datetime import datetime, timezone
import unittest
from uuid import uuid4

from backend.app.common.cache.redis import get_redis_client
from backend.app.common.db.connection import get_db_session
from backend.app.common.db.models.article import Article
from backend.app.common.db.models.source import Source
from backend.app.common.queue.client import QueueManager
from backend.app.common.queue.schemas import JobPayload, JobType, QueueName
from backend.app.modules.sources.adapters.base import (
    AdapterHealthStatus,
    BaseSourceAdapter,
    RawArticleDTO,
    RawFeedResult,
)
from backend.app.modules.sources.adapters.registry import AdapterRegistry
from workers.ingestion.handler import handle_ingestion_job


class MockPipelineAdapter(BaseSourceAdapter):
    def __init__(self, raw_items: list[RawArticleDTO]) -> None:
        self.raw_items = raw_items

    def fetch(self, source: Source) -> RawFeedResult:
        return RawFeedResult(
            source_id=source.id,
            items=self.raw_items,
            item_count=len(self.raw_items),
            status_code=200,
            fetched_at=datetime.now(timezone.utc),
        )

    def health(self, source: Source) -> AdapterHealthStatus:
        return AdapterHealthStatus(is_healthy=True, response_time_ms=5.0)


class TestIngestionPipelineIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.session_cm = get_db_session()
        self.db = self.session_cm.__enter__()
        self.redis_client = get_redis_client()
        self.queue_mgr = QueueManager(self.redis_client)

        # Clean test queues
        self.redis_client.delete(QueueName.INGESTION.value)
        self.redis_client.delete(QueueName.EXTRACTION.value)

        # Create test source
        self.source = Source(
            name=f"Pipeline Test Source {uuid4().hex[:6]}",
            domain=f"pipeline-{uuid4().hex[:6]}.vn",
            source_type="MOCK_RSS",
            rss_url="https://example.com/rss.xml",
            active=True,
            priority=80,
        )
        self.db.add(self.source)
        self.db.commit()

        self.article_url = f"https://{self.source.domain}/tin-nong-metro-{uuid4().hex[:6]}.htm"
        self.article_title = f"Khánh thành tuyến metro số 2 Bến Thành {uuid4().hex[:6]}"
        self.mock_items = [
            RawArticleDTO(
                source_id=self.source.id,
                source_url=self.article_url,
                title=self.article_title,
                summary_raw="<p>Dự án metro số 2 TP.HCM chính thức khởi công xây dựng sáng nay.</p>",
                published_at_raw="2026-03-16T08:00:00Z",
            )
        ]
        AdapterRegistry.register_adapter("MOCK_RSS", MockPipelineAdapter(self.mock_items))

    def tearDown(self) -> None:
        self.redis_client.delete(QueueName.INGESTION.value)
        self.redis_client.delete(QueueName.EXTRACTION.value)
        self.db.rollback()
        self.session_cm.__exit__(None, None, None)

    def test_full_pipeline_ingestion_and_idempotency(self) -> None:
        job = JobPayload(
            job_type=JobType.INGESTION.value,
            entity_id=str(self.source.id),
            payload={
                "source_id": str(self.source.id),
                "domain": self.source.domain,
                "rss_url": self.source.rss_url,
            },
        )

        # 1. Run pipeline via handler
        success = handle_ingestion_job(job)
        self.assertTrue(success)

        # 2. Check article was saved in PostgreSQL
        with get_db_session() as db:
            saved_article = db.query(Article).filter(Article.canonical_url == self.article_url).first()
            self.assertIsNotNone(saved_article)
            self.assertEqual(saved_article.title, self.article_title)

            # Check source last_success_at
            updated_source = db.query(Source).filter(Source.id == self.source.id).first()
            self.assertIsNotNone(updated_source.last_success_at)

        # 3. Check extraction queue received job
        extraction_job = self.queue_mgr.dequeue(QueueName.EXTRACTION, timeout_seconds=1)
        self.assertIsNotNone(extraction_job)
        self.assertEqual(extraction_job.job_type, JobType.EXTRACTION.value)
        self.assertEqual(extraction_job.entity_id, str(saved_article.id))

        # 4. Idempotency test: run same job again with same feed data
        success_second_run = handle_ingestion_job(job)
        self.assertTrue(success_second_run)

        # No duplicate article created
        with get_db_session() as db:
            count = db.query(Article).filter(Article.canonical_url == self.article_url).count()
            self.assertEqual(count, 1)

        # No extra extraction job queued
        no_extra_job = self.queue_mgr.dequeue(QueueName.EXTRACTION, timeout_seconds=0)
        self.assertIsNone(no_extra_job)


if __name__ == "__main__":
    unittest.main()
