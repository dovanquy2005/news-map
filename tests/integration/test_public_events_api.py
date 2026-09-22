"""Integration tests for Public Events APIs (GET /events, GET /events/{id}, GET /events/search)."""

from datetime import datetime, timezone, timedelta
import unittest
import uuid

from fastapi.testclient import TestClient

from backend.app.common.db.connection import get_db_session
from backend.app.common.db.models.article import Article
from backend.app.common.db.models.event import Event
from backend.app.common.db.models.event_article import EventArticle
from backend.app.common.db.models.event_fact import EventFact
from backend.app.common.db.models.event_timeline import EventTimeline
from backend.app.common.db.models.source import Source
from backend.app.main import app


class TestPublicEventsAPIIntegration(unittest.TestCase):
    """Integration test suite for public event API contracts."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.now = datetime.now(timezone.utc)

    def _seed_test_event(self) -> uuid.UUID:
        token = uuid.uuid4().hex[:6]
        with get_db_session() as session:
            # Source & Article
            source = Source(name=f"VnExpress_{token}", domain=f"vnexpress-{token}.net")
            session.add(source)
            session.flush()

            article = Article(
                source_id=source.id,
                url=f"https://example.com/api-art-{token}.html",
                canonical_url=f"https://example.com/api-art-{token}.html",
                title=f"Khởi công tuyến metro số 2 {token}",
                published_at=self.now,
                content_hash=uuid.uuid4().hex,
            )
            session.add(article)
            session.flush()

            # Event
            event = Event(
                title=f"Khởi công dự án metro số 2 {token}",
                normalized_title=f"khoi cong du an metro so 2 {token}",
                category="INFRASTRUCTURE",
                latitude=10.7769,
                longitude=106.7009,
                location_label="Quận 1, TP. Hồ Chí Minh",
                location_confidence=0.95,
                geom="SRID=4326;POINT(106.7009 10.7769)",
                occurred_at=self.now - timedelta(hours=1),
                first_reported_at=self.now - timedelta(hours=1),
                last_updated_at=self.now,
                status="NEW",
                article_count=1,
                source_count=1,
                confidence_score=0.85,
                summary="Dự án metro số 2 chính thức được khởi động tại TP.HCM.",
            )
            session.add(event)
            session.flush()

            session.add(EventArticle(event_id=event.id, article_id=article.id, match_score=1.0, match_reason="Initial"))
            session.add(EventTimeline(event_id=event.id, timestamp=self.now, timeline_type="OCCURRED", text="Lễ khởi công diễn ra"))
            session.add(EventFact(event_id=event.id, fact_key="tổng_mức_đầu_tư", fact_value="47.000 tỷ đồng", fact_confidence=0.95))
            session.commit()
            return event.id

    def test_list_events_default_success(self) -> None:
        """GET /api/v1/events returns standardized paginated list."""
        event_id = self._seed_test_event()

        response = self.client.get("/api/v1/events")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("data", data)
        self.assertIn("pagination", data)
        self.assertIsInstance(data["data"], list)
        self.assertGreaterEqual(len(data["data"]), 1)

        # Check required fields
        item = data["data"][0]
        self.assertIn("id", item)
        self.assertIn("title", item)
        self.assertIn("category", item)
        self.assertIn("latitude", item)
        self.assertIn("longitude", item)

    def test_list_events_spatial_bbox_filter(self) -> None:
        """GET /api/v1/events with bbox filters geographically."""
        event_id = self._seed_test_event()

        # Bounding box covering Ho Chi Minh City: minLng,minLat,maxLng,maxLat
        hcm_bbox = "106.0,10.0,107.0,11.5"
        res = self.client.get(f"/api/v1/events?bbox={hcm_bbox}")
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertTrue(any(item["id"] == str(event_id) for item in data))

        # Bounding box in northern Vietnam (should NOT contain the HCMC event)
        north_bbox = "105.0,20.0,106.5,22.0"
        res_north = self.client.get(f"/api/v1/events?bbox={north_bbox}")
        self.assertEqual(res_north.status_code, 200)
        data_north = res_north.json()["data"]
        self.assertFalse(any(item["id"] == str(event_id) for item in data_north))

    def test_list_events_rejects_window_over_30_days(self) -> None:
        """Query with date range > 30 days is rejected with HTTP 400."""
        from_date = (self.now - timedelta(days=40)).isoformat()
        to_date = self.now.isoformat()

        res = self.client.get("/api/v1/events", params={"from": from_date, "to": to_date})
        self.assertEqual(res.status_code, 400)
        body = res.json()
        self.assertEqual(body["error"]["code"], "WINDOW_TOO_LARGE")

    def test_get_event_detail_success(self) -> None:
        """GET /api/v1/events/{eventId} returns full detail with sources, timeline, facts."""
        event_id = self._seed_test_event()

        res = self.client.get(f"/api/v1/events/{event_id}")
        self.assertEqual(res.status_code, 200)
        detail = res.json()

        self.assertEqual(detail["id"], str(event_id))
        self.assertIn("metro số 2", detail["title"])
        self.assertEqual(detail["category"], "INFRASTRUCTURE")
        self.assertIsNotNone(detail["summary"])

        # Check nested structures
        self.assertIn("location", detail)
        self.assertIn("confidence", detail)
        self.assertIn("sources", detail)
        self.assertIn("timeline", detail)
        self.assertIn("facts", detail)

        self.assertGreaterEqual(len(detail["sources"]), 1)
        self.assertGreaterEqual(len(detail["timeline"]), 1)
        self.assertGreaterEqual(len(detail["facts"]), 1)

    def test_get_event_detail_not_found(self) -> None:
        """GET /api/v1/events/{random_uuid} returns standardized 404 envelope."""
        non_existent = uuid.uuid4()
        res = self.client.get(f"/api/v1/events/{non_existent}")
        self.assertEqual(res.status_code, 404)
        body = res.json()
        self.assertEqual(body["error"]["code"], "EVENT_NOT_FOUND")

    def test_search_events_success_and_validation(self) -> None:
        """GET /api/v1/events/search searches by keyword and enforces query bounds."""
        event_id = self._seed_test_event()

        # Query too short (< 2 chars) -> 400
        res_short = self.client.get("/api/v1/events/search?q=a")
        self.assertEqual(res_short.status_code, 422)  # FastAPI Query min_length

        # Valid search
        res_search = self.client.get("/api/v1/events/search?q=metro")
        self.assertEqual(res_search.status_code, 200)
        data = res_search.json()
        self.assertIn("data", data)
        self.assertTrue(any(item["id"] == str(event_id) for item in data["data"]))
