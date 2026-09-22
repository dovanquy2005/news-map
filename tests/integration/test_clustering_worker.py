"""Integration tests for ClusteringWorker, candidate retrieval, and event provenance."""

from datetime import datetime, timezone
import unittest
import uuid

from sqlalchemy import select

from backend.app.common.db.connection import get_db_session
from backend.app.common.db.models.article import Article
from backend.app.common.db.models.event import Event
from backend.app.common.db.models.event_article import EventArticle
from backend.app.common.db.models.location import Location
from backend.app.common.db.models.source import Source
from backend.app.common.queue.schemas import JobPayload, JobType
from workers.clustering.worker import ClusteringWorker


class TestClusteringWorkerIntegration(unittest.TestCase):
    """Integration test suite for ClusteringWorker and event lifecycle."""

    def setUp(self) -> None:
        self.worker = ClusteringWorker()

    def _create_article(
        self, session, title: str, category: str, location_id=None, province: str = "TP. Hồ Chí Minh"
    ) -> Article:
        source = Source(
            name=f"Src-{uuid.uuid4().hex[:8]}",
            domain=f"clustersrc-{uuid.uuid4().hex[:6]}.vn",
        )
        session.add(source)
        session.flush()

        raw_meta = {
            "extraction": {
                "title": title,
                "event_type": category,
                "location_text": f"Khu vực {province}",
                "province": province,
            }
        }
        if location_id:
            raw_meta["location_id"] = str(location_id)

        article = Article(
            source_id=source.id,
            url=f"https://example.com/cluster-{uuid.uuid4().hex}.html",
            canonical_url=f"https://example.com/cluster-{uuid.uuid4().hex}.html",
            title=title,
            published_at=datetime.now(timezone.utc),
            content_hash=uuid.uuid4().hex,
            raw_metadata=raw_meta,
        )
        session.add(article)
        session.flush()
        return article

    def _create_location(self, session, lat: float, lng: float, name: str, province: str = "TP. Hồ Chí Minh") -> Location:
        loc = Location(
            raw_text=name,
            normalized_text=name,
            province=province,
            latitude=lat,
            longitude=lng,
            provider="INTERNAL_GAZETTEER",
            confidence=0.90,
            geom=f"SRID=4326;POINT({lng} {lat})",
        )
        session.add(loc)
        session.flush()
        return loc

    def test_first_article_creates_new_event(self) -> None:
        """First incoming article creates a new Event and attaches EventArticle."""
        unique_token = uuid.uuid4().hex[:6]
        cat = f"TECH_{unique_token.upper()}"
        offset = (int(uuid.uuid4().hex[:4], 16) % 1000) * 0.001
        lat, lng = 5.0000 + offset, 100.0000 + offset
        prov = f"Tỉnh_{unique_token}"
        with get_db_session() as session:
            loc = self._create_location(session, lat, lng, f"Long Xuyên {unique_token}", province=prov)
            art = self._create_article(session, f"Triển khai 5G tại trung tâm {unique_token}", cat, loc.id, province=prov)
            art_id = art.id
            session.commit()

        job = JobPayload(
            job_type=JobType.CLUSTERING.value,
            entity_id=str(art_id),
            payload={"article_id": str(art_id)},
        )

        with get_db_session() as session:
            self.worker.process_job(job, session)

        # Verify Event and EventArticle
        with get_db_session() as session:
            assoc = session.scalars(select(EventArticle).where(EventArticle.article_id == art_id)).first()
            self.assertIsNotNone(assoc)
            self.assertEqual(assoc.match_score, 1.0)
            self.assertEqual(assoc.match_reason, "Initial event creator")

            event = session.get(Event, assoc.event_id)
            self.assertIsNotNone(event)
            self.assertEqual(event.category, cat)
            self.assertEqual(event.article_count, 1)
            self.assertEqual(event.status, "NEW")

    def test_second_article_merges_into_existing_event(self) -> None:
        """Second related article on the same incident merges into existing Event."""
        incident_id = uuid.uuid4().hex[:6]
        cat = f"ACCIDENT_{incident_id.upper()}"
        offset = (int(uuid.uuid4().hex[:4], 16) % 1000) * 0.001
        lat, lng = 6.0000 + offset, 101.0000 + offset
        prov = f"Tỉnh_{incident_id}"
        with get_db_session() as session:
            loc = self._create_location(session, lat, lng, f"Nha Trang {incident_id}", province=prov)
            art1 = self._create_article(session, f"Cháy lớn tại nhà kho {incident_id} lúc rạng sáng", cat, loc.id, province=prov)
            art2 = self._create_article(session, f"Vụ cháy nhà kho {incident_id}, thiêu rụi tài sản", cat, loc.id, province=prov)
            art1_id = art1.id
            art2_id = art2.id
            session.commit()

        # Process Job 1
        job1 = JobPayload(
            job_type=JobType.CLUSTERING.value,
            entity_id=str(art1_id),
            payload={"article_id": str(art1_id)},
        )
        with get_db_session() as session:
            self.worker.process_job(job1, session)

        # Process Job 2
        job2 = JobPayload(
            job_type=JobType.CLUSTERING.value,
            entity_id=str(art2_id),
            payload={"article_id": str(art2_id)},
        )
        with get_db_session() as session:
            self.worker.process_job(job2, session)

        # Verify both articles merged into ONE Event
        with get_db_session() as session:
            assoc1 = session.scalars(select(EventArticle).where(EventArticle.article_id == art1_id)).first()
            assoc2 = session.scalars(select(EventArticle).where(EventArticle.article_id == art2_id)).first()

            self.assertIsNotNone(assoc1)
            self.assertIsNotNone(assoc2)
            self.assertEqual(assoc1.event_id, assoc2.event_id)

            event = session.get(Event, assoc1.event_id)
            self.assertEqual(event.article_count, 2)
            self.assertEqual(event.source_count, 2)
            self.assertEqual(event.status, "DEVELOPING")
