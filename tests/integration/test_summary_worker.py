"""Integration tests for SummaryWorker, timeline extraction, and facts aggregation."""

from datetime import datetime, timezone, timedelta
import unittest
import uuid

from sqlalchemy import select

from backend.app.common.db.connection import get_db_session
from backend.app.common.db.models.article import Article
from backend.app.common.db.models.event import Event
from backend.app.common.db.models.event_article import EventArticle
from backend.app.common.db.models.event_fact import EventFact
from backend.app.common.db.models.event_timeline import EventTimeline
from backend.app.common.db.models.source import Source
from backend.app.common.queue.schemas import JobPayload, JobType
from workers.summarization.worker import SummaryWorker


class TestSummaryWorkerIntegration(unittest.TestCase):
    """Integration test suite for event summary generation and confidence scoring."""

    def setUp(self) -> None:
        self.worker = SummaryWorker()
        self.now = datetime.now(timezone.utc)

    def test_summary_worker_builds_timeline_facts_and_confidence(self) -> None:
        """Worker rebuilds timeline, aggregates facts, generates summary, and sets confidence."""
        token = uuid.uuid4().hex[:6]

        with get_db_session() as session:
            # 1. Create Sources
            s1 = Source(name=f"SourceA_{token}", domain=f"source-a-{token}.vn")
            s2 = Source(name=f"SourceB_{token}", domain=f"source-b-{token}.vn")
            session.add_all([s1, s2])
            session.flush()

            # 2. Create Event
            event = Event(
                title=f"Tai nạn liên hoàn trên quốc lộ 1A {token}",
                normalized_title=f"tai nan lien hoan tren quoc lo 1a {token}",
                category="ACCIDENT",
                latitude=10.8231,
                longitude=106.6297,
                location_label="Quốc lộ 1A, Bình Chánh, TP. Hồ Chí Minh",
                location_confidence=0.90,
                geom="SRID=4326;POINT(106.6297 10.8231)",
                occurred_at=self.now - timedelta(hours=2),
                first_reported_at=self.now - timedelta(hours=1),
                last_updated_at=self.now,
                status="DEVELOPING",
                article_count=2,
                source_count=2,
            )
            session.add(event)
            session.flush()
            event_id = event.id

            # 3. Create Articles with key facts
            art1 = Article(
                source_id=s1.id,
                url=f"https://example.com/art1-{token}.html",
                canonical_url=f"https://example.com/art1-{token}.html",
                title=f"Tai nạn giao thông nghiêm trọng quốc lộ 1A {token}",
                published_at=self.now - timedelta(hours=1),
                content_hash=uuid.uuid4().hex,
                raw_metadata={"extraction": {"key_facts": ["thương_vong: 2 người bị thương", "phương_tiện: 3 xe tải"]}},
            )
            art2 = Article(
                source_id=s2.id,
                url=f"https://example.com/art2-{token}.html",
                canonical_url=f"https://example.com/art2-{token}.html",
                title=f"Công an điều tra vụ tai nạn trên quốc lộ 1A {token}",
                published_at=self.now,
                content_hash=uuid.uuid4().hex,
                raw_metadata={"extraction": {"key_facts": ["thương_vong: 2 người bị thương", "nguyên_nhân: nổ lốp xe"]}},
            )
            session.add_all([art1, art2])
            session.flush()

            # Link to event
            session.add(EventArticle(event_id=event_id, article_id=art1.id, match_score=1.0, match_reason="Initial"))
            session.add(EventArticle(event_id=event_id, article_id=art2.id, match_score=0.9, match_reason="Merge"))
            session.commit()

        # Execute Summary Job
        job = JobPayload(
            job_type=JobType.SUMMARY.value,
            entity_id=str(event_id),
            payload={"event_id": str(event_id)},
        )

        with get_db_session() as session:
            success = self.worker.process_job(job, session)
            self.assertTrue(success)

        # Verification
        with get_db_session() as session:
            ev = session.get(Event, event_id)
            self.assertIsNotNone(ev)
            self.assertIsNotNone(ev.summary)
            self.assertGreater(len(ev.summary), 20)
            self.assertGreaterEqual(ev.confidence_score, 0.50)

            # Check Timeline
            timelines = list(session.scalars(select(EventTimeline).where(EventTimeline.event_id == event_id)).all())
            self.assertGreaterEqual(len(timelines), 2)
            types = [t.timeline_type for t in timelines]
            self.assertIn("OCCURRED", types)
            self.assertIn("FIRST_REPORTED", types)

            # Check Facts
            facts = list(session.scalars(select(EventFact).where(EventFact.event_id == event_id)).all())
            self.assertGreaterEqual(len(facts), 1)
            keys = [f.fact_key for f in facts]
            self.assertIn("thương_vong", keys)
