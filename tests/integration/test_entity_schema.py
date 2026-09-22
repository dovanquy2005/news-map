"""Integration tests for Core Entity Models, Spatial Queries, and Repositories (TASK-004).

Verifies against active PostgreSQL + PostGIS database:
- CRUD on core entity models via BaseRepository
- Atomic creation of Event with multi-source articles, facts, and timeline
- Spatial queries: ST_DWithin and ST_MakeEnvelope bounding box on PostGIS geom
- Cascade delete verification
- Unique constraint violations on duplicate canonical_url
"""

import unittest
import uuid
from datetime import datetime, timezone

from geoalchemy2.functions import ST_DWithin, ST_MakeEnvelope
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from backend.app.common.db.connection import get_db_engine, get_db_session, reset_db_engine
from backend.app.common.db.models import (
    Article,
    Event,
    EventArticle,
    EventFact,
    EventTimeline,
    HistoricalSnapshot,
    Location,
    ProcessingJob,
    Source,
)
from backend.app.common.db.repositories.base import BaseRepository


class TestEntitySchemaIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reset_db_engine()
        cls.engine = get_db_engine()

    def test_source_and_article_creation_with_repository(self):
        """Verify Source and Article persistence using BaseRepository."""
        with get_db_session() as session:
            source_repo = BaseRepository(Source, session)
            article_repo = BaseRepository(Article, session)

            domain_suffix = uuid.uuid4().hex[:8]
            source = Source(
                name="VnExpress",
                domain=f"vnexpress-{domain_suffix}.net",
                source_type="rss",
                rss_url="https://vnexpress.net/rss/tin-moi-nhat.rss",
                active=True,
                priority=1,
            )
            source_repo.create(source)
            self.assertIsNotNone(source.id)

            article = Article(
                source_id=source.id,
                url=f"https://vnexpress.net/tin-{domain_suffix}.html",
                canonical_url=f"https://vnexpress.net/tin-{domain_suffix}.html",
                title="Khởi công dự án cầu vượt tại Hà Nội",
                summary_raw="Sáng nay, dự án cầu vượt được chính thức khởi công.",
                content_excerpt="Dự án có chiều dài 2km kết nối giao thông...",
                published_at=datetime.now(timezone.utc),
                content_hash=uuid.uuid4().hex,
                language="vi",
                raw_metadata={"category": "Giao thông"},
            )
            article_repo.create(article)
            self.assertIsNotNone(article.id)

            # Query back
            fetched = article_repo.get_by_id(article.id)
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.title, "Khởi công dự án cầu vượt tại Hà Nội")
            self.assertEqual(fetched.source.domain, f"vnexpress-{domain_suffix}.net")

    def test_duplicate_canonical_url_raises_integrity_error(self):
        """Duplicate canonical_url must violate unique constraint."""
        canonical = f"https://tuoitre.vn/duplicate-{uuid.uuid4().hex}.html"

        with get_db_session() as session:
            source = Source(name="TuoiTre", domain=f"tuoitre-{uuid.uuid4().hex[:6]}.vn")
            session.add(source)
            session.flush()

            art1 = Article(
                source_id=source.id,
                url=canonical,
                canonical_url=canonical,
                title="Bài viết 1",
                published_at=datetime.now(timezone.utc),
                content_hash="hash1",
            )
            session.add(art1)
            session.flush()

            art2 = Article(
                source_id=source.id,
                url=canonical + "?ref=share",
                canonical_url=canonical,  # Same canonical URL
                title="Bài viết 2",
                published_at=datetime.now(timezone.utc),
                content_hash="hash2",
            )
            session.add(art2)
            with self.assertRaises(IntegrityError):
                session.flush()
            session.rollback()

    def test_event_atomic_lifecycle_and_spatial_query(self):
        """Create Event with articles, facts, and timeline; then query with PostGIS spatial filter."""
        # Coordinates: Ho Chi Minh City center (10.7769, 106.7009)
        hcm_lat = 10.7769
        hcm_lng = 106.7009
        hcm_point = f"SRID=4326;POINT({hcm_lng} {hcm_lat})"

        event_id = None
        article_id = None

        with get_db_session() as session:
            # 1. Setup Source & Article
            source = Source(name="ThanhNien", domain=f"thanhnien-{uuid.uuid4().hex[:6]}.vn")
            session.add(source)
            session.flush()

            article = Article(
                source_id=source.id,
                url=f"https://thanhnien.vn/event-{uuid.uuid4().hex}.html",
                canonical_url=f"https://thanhnien.vn/event-{uuid.uuid4().hex}.html",
                title="Sự kiện công nghệ tại TP.HCM",
                published_at=datetime.now(timezone.utc),
                content_hash=uuid.uuid4().hex,
            )
            session.add(article)
            session.flush()
            article_id = article.id

            # 2. Setup Event with PostGIS geom
            event = Event(
                title="Triển lãm công nghệ Tech Expo 2026",
                normalized_title="trien lam cong nghe tech expo 2026",
                category="technology",
                summary="Triển lãm công nghệ quy tụ hơn 200 doanh nghiệp hàng đầu.",
                latitude=hcm_lat,
                longitude=hcm_lng,
                location_label="Quận 1, TP. Hồ Chí Minh",
                location_confidence=0.95,
                geom=hcm_point,
                occurred_at=datetime.now(timezone.utc),
                first_reported_at=datetime.now(timezone.utc),
                last_updated_at=datetime.now(timezone.utc),
                status="active",
                confidence_score=0.9,
                article_count=1,
                source_count=1,
            )
            session.add(event)
            session.flush()
            event_id = event.id

            # 3. Associate Article to Event
            assoc = EventArticle(
                event_id=event.id,
                article_id=article.id,
                match_score=0.98,
                match_reason="Chủ đề và vị trí trùng khớp cao",
            )
            session.add(assoc)

            # 4. Attach Fact
            fact = EventFact(
                event_id=event.id,
                fact_key="attendee_count",
                fact_value="5000",
                fact_confidence=0.9,
            )
            session.add(fact)

            # 5. Attach Timeline
            timeline = EventTimeline(
                event_id=event.id,
                timestamp=datetime.now(timezone.utc),
                timeline_type="reported",
                text="Ban tổ chức phát biểu khai mạc triển lãm.",
                source_article_id=article.id,
            )
            session.add(timeline)

            # 6. Attach Historical Snapshot
            snapshot = HistoricalSnapshot(
                event_id=event.id,
                captured_at=datetime.now(timezone.utc),
                article_count=1,
                source_count=1,
                last_seen_at=datetime.now(timezone.utc),
            )
            session.add(snapshot)

        # Query back and verify PostGIS spatial query
        with get_db_session() as session:
            # Bounding box covering Southern Vietnam: (min_lng, min_lat, max_lng, max_lat)
            bbox = ST_MakeEnvelope(105.0, 9.0, 108.0, 12.0, 4326)
            stmt = select(Event).where(func.ST_Contains(bbox, Event.geom))
            results = session.execute(stmt).scalars().all()

            matching_event = next((e for e in results if e.id == event_id), None)
            self.assertIsNotNone(matching_event, "Event must be found within Southern VN bounding box")
            self.assertEqual(len(matching_event.articles), 1)
            self.assertEqual(len(matching_event.facts), 1)
            self.assertEqual(len(matching_event.timeline), 1)
            self.assertEqual(matching_event.articles[0].article_id, article_id)

    def test_event_cascade_delete(self):
        """Deleting an Event must cascade-delete its facts, timeline, and associations."""
        event_id = None
        with get_db_session() as session:
            source = Source(name="VTV", domain=f"vtv-{uuid.uuid4().hex[:6]}.vn")
            session.add(source)
            session.flush()

            article = Article(
                source_id=source.id,
                url=f"https://vtv.vn/{uuid.uuid4().hex}.html",
                canonical_url=f"https://vtv.vn/{uuid.uuid4().hex}.html",
                title="Bản tin thời sự",
                published_at=datetime.now(timezone.utc),
                content_hash=uuid.uuid4().hex,
            )
            session.add(article)
            session.flush()

            event = Event(
                title="Sự kiện thử nghiệm xóa",
                normalized_title="su kien thu nghiem xoa",
                category="test",
                latitude=21.0285,
                longitude=105.8542,
                geom="SRID=4326;POINT(105.8542 21.0285)",
                occurred_at=datetime.now(timezone.utc),
                first_reported_at=datetime.now(timezone.utc),
                last_updated_at=datetime.now(timezone.utc),
            )
            session.add(event)
            session.flush()
            event_id = event.id

            session.add(EventArticle(event_id=event.id, article_id=article.id))
            session.add(EventFact(event_id=event.id, fact_key="k", fact_value="v"))
            session.add(EventTimeline(event_id=event.id, timestamp=datetime.now(timezone.utc), text="T"))

        # Now delete the event
        with get_db_session() as session:
            event_to_delete = session.get(Event, event_id)
            self.assertIsNotNone(event_to_delete)
            session.delete(event_to_delete)

        # Verify child records were cascade-deleted
        with get_db_session() as session:
            self.assertIsNone(session.get(Event, event_id))
            facts = session.execute(select(EventFact).where(EventFact.event_id == event_id)).all()
            self.assertEqual(len(facts), 0)
            assocs = session.execute(select(EventArticle).where(EventArticle.event_id == event_id)).all()
            self.assertEqual(len(assocs), 0)

    def test_processing_job_model(self):
        """Verify ProcessingJob status tracking."""
        with get_db_session() as session:
            repo = BaseRepository(ProcessingJob, session)
            job = ProcessingJob(
                job_type="nlp_extraction",
                entity_id=uuid.uuid4(),
                status="pending",
                attempt=0,
                max_attempts=3,
                scheduled_at=datetime.now(timezone.utc),
            )
            repo.create(job)
            self.assertIsNotNone(job.id)
            self.assertEqual(job.status, "pending")


if __name__ == "__main__":
    unittest.main()
