"""Integration tests for GeocodingWorker and PostGIS Location persistence."""

from datetime import datetime, timezone
import unittest
import uuid

from sqlalchemy import func, select

from backend.app.common.db.connection import get_db_session
from backend.app.common.db.models.article import Article
from backend.app.common.db.models.location import Location
from backend.app.common.db.models.source import Source
from backend.app.common.queue.schemas import JobPayload, JobType
from workers.geocoding.worker import GeocodingWorker


class TestGeocodingWorkerIntegration(unittest.TestCase):
    """Integration test suite for geocoding pipeline and PostGIS persistence."""

    def setUp(self) -> None:
        self.worker = GeocodingWorker()

    def _create_test_article(self, session, title: str, location_text: str | None = None) -> Article:
        source = Source(
            name=f"GeoSource_{uuid.uuid4().hex[:6]}",
            domain=f"geotest-{uuid.uuid4().hex[:6]}.vn",
        )
        session.add(source)
        session.flush()

        raw_meta = {}
        if location_text:
            raw_meta["extraction"] = {"location_text": location_text}

        article = Article(
            source_id=source.id,
            url=f"https://example.com/geo-{uuid.uuid4().hex}.html",
            canonical_url=f"https://example.com/geo-{uuid.uuid4().hex}.html",
            title=title,
            published_at=datetime.now(timezone.utc),
            content_hash=uuid.uuid4().hex,
            raw_metadata=raw_meta,
        )
        session.add(article)
        session.flush()
        return article

    def test_geocoding_worker_persists_location_and_updates_article(self) -> None:
        """Worker processes valid location, persists PostGIS point, and updates article."""
        with get_db_session() as session:
            article = self._create_test_article(session, "Tai nạn giao thông tại Đà Nẵng")
            article_id = article.id
            session.commit()

        job = JobPayload(
            job_type=JobType.GEOCODING.value,
            entity_id=str(article_id),
            payload={
                "article_id": str(article_id),
                "location_text": "tại Đà Nẵng",
                "province": "Đà Nẵng",
            },
        )

        with get_db_session() as session:
            success = self.worker.process_job(job, session)
            self.assertTrue(success)

        # Verify Location entity in database
        with get_db_session() as session:
            updated_art = session.get(Article, article_id)
            self.assertIsNotNone(updated_art)
            loc_id_str = updated_art.raw_metadata.get("location_id")
            self.assertIsNotNone(loc_id_str)

            loc = session.get(Location, uuid.UUID(loc_id_str))
            self.assertIsNotNone(loc)
            self.assertEqual(loc.province, "Đà Nẵng")
            self.assertAlmostEqual(loc.latitude, 16.0544, places=3)
            self.assertAlmostEqual(loc.longitude, 108.2022, places=3)

            # Query PostGIS ST_X (longitude) and ST_Y (latitude) functions
            point_query = session.execute(
                select(func.ST_X(loc.geom), func.ST_Y(loc.geom))
            ).first()
            self.assertIsNotNone(point_query)
            geom_lng, geom_lat = point_query
            self.assertAlmostEqual(geom_lng, 108.2022, places=3)
            self.assertAlmostEqual(geom_lat, 16.0544, places=3)

    def test_geocoding_worker_deduplicates_nearby_locations(self) -> None:
        """Identical or nearby location queries within 50m must reuse existing Location row."""
        with get_db_session() as session:
            art1 = self._create_test_article(session, "Cháy lớn ở TP. Hồ Chí Minh")
            art2 = self._create_test_article(session, "Cứu hộ thành công ở Sài Gòn")
            art1_id = art1.id
            art2_id = art2.id
            session.commit()

        # Job 1
        job1 = JobPayload(
            job_type=JobType.GEOCODING.value,
            entity_id=str(art1_id),
            payload={"article_id": str(art1_id), "location_text": "TP. Hồ Chí Minh"},
        )
        with get_db_session() as session:
            self.worker.process_job(job1, session)

        # Job 2: Alias "Sài Gòn" resolves to the same centroid coordinates
        job2 = JobPayload(
            job_type=JobType.GEOCODING.value,
            entity_id=str(art2_id),
            payload={"article_id": str(art2_id), "location_text": "Sài Gòn"},
        )
        with get_db_session() as session:
            self.worker.process_job(job2, session)

        with get_db_session() as session:
            article1 = session.get(Article, art1_id)
            article2 = session.get(Article, art2_id)

            loc1_id = article1.raw_metadata.get("location_id")
            loc2_id = article2.raw_metadata.get("location_id")

            self.assertIsNotNone(loc1_id)
            self.assertIsNotNone(loc2_id)
            # Reuses same physical location
            self.assertEqual(loc1_id, loc2_id)

    def test_unresolvable_location_gracefully_handled(self) -> None:
        """Unresolvable or empty location texts are recorded as UNRESOLVED without error."""
        with get_db_session() as session:
            art = self._create_test_article(session, "Hội thảo kinh tế quốc tế")
            art_id = art.id
            session.commit()

        job = JobPayload(
            job_type=JobType.GEOCODING.value,
            entity_id=str(art_id),
            payload={
                "article_id": str(art_id),
                "location_text": "Hội nghị cấp cao không có địa chỉ thực tế",
            },
        )
        with get_db_session() as session:
            success = self.worker.process_job(job, session)
            self.assertTrue(success)

        with get_db_session() as session:
            article = session.get(Article, art_id)
            self.assertIsNone(article.raw_metadata.get("location_id"))
            geocoding_meta = article.raw_metadata.get("geocoding", {})
            self.assertEqual(geocoding_meta.get("status"), "UNRESOLVED")
            self.assertEqual(geocoding_meta.get("confidence"), 0.0)
