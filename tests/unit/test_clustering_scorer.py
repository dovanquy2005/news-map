"""Unit tests for ClusteringScorer and multi-signal similarity evaluation."""

from datetime import datetime, timezone, timedelta
import unittest
import uuid

from backend.app.modules.clustering.schemas import ClusteringDecision, EventCandidateDTO
from backend.app.modules.clustering.scorer import ClusteringScorer


class TestClusteringScorerUnit(unittest.TestCase):
    """Test suite for ClusteringScorer."""

    def setUp(self) -> None:
        self.scorer = ClusteringScorer()
        self.now = datetime.now(timezone.utc)

    def _create_candidate(
        self,
        title: str,
        category: str = "ACCIDENT",
        lat: float = 10.7769,
        lng: float = 106.7009,
        location_label: str = "Quận 1, TP. Hồ Chí Minh",
        occurred_at: datetime | None = None,
    ) -> EventCandidateDTO:
        t = occurred_at or self.now
        return EventCandidateDTO(
            event_id=uuid.uuid4(),
            title=title,
            normalized_title=title.lower(),
            category=category,
            status="active",
            latitude=lat,
            longitude=lng,
            location_label=location_label,
            occurred_at=t,
            first_reported_at=t,
            last_updated_at=t,
            article_count=2,
            source_count=2,
            confidence_score=0.8,
            distance_meters=50.0,
        )

    def test_same_incident_yields_merge_decision(self) -> None:
        """Articles covering the exact same event must trigger MERGE with high score."""
        cand = self._create_candidate("Cháy lớn tại quán bar Quận 1 lúc rạng sáng")
        art_title = "Vụ cháy quán bar ở Quận 1, thiêu rụi nhiều tài sản"
        art_category = "ACCIDENT"
        art_time = self.now + timedelta(minutes=30)

        decision, score, breakdown, reason = self.scorer.evaluate_candidate(
            art_title=art_title,
            art_category=art_category,
            art_time=art_time,
            art_lat=10.7770,
            art_lng=106.7010,
            art_province="TP. Hồ Chí Minh",
            candidate=cand,
        )

        self.assertEqual(decision, ClusteringDecision.MERGE)
        self.assertGreaterEqual(score, 0.70)
        self.assertGreaterEqual(breakdown.location_similarity, 0.9)
        self.assertGreaterEqual(breakdown.time_similarity, 0.9)

    def test_incompatible_category_strictly_forbids_merge(self) -> None:
        """Events with incompatible categories (CRIME vs WEATHER) can never merge."""
        cand = self._create_candidate("Bão số 3 đổ bộ gây mưa lớn ở Quảng Ninh", category="WEATHER")
        art_title = "Triệt phá đường dây buôn lậu lớn tại Quảng Ninh"
        art_category = "CRIME"

        decision, score, breakdown, reason = self.scorer.evaluate_candidate(
            art_title=art_title,
            art_category=art_category,
            art_time=self.now,
            art_lat=cand.latitude,
            art_lng=cand.longitude,
            art_province="Quảng Ninh",
            candidate=cand,
        )

        self.assertEqual(decision, ClusteringDecision.CREATE_NEW_EVENT)
        self.assertEqual(score, 0.0)
        self.assertIn("incompatible", reason.lower())

    def test_safety_guard_same_location_different_incident(self) -> None:
        """Same road/province but divergent topics and time must not falsely merge."""
        cand = self._create_candidate("Tai nạn giao thông trên đường Nguyễn Huệ lúc 6h sáng")
        art_title = "Lễ hội ẩm thực đường phố sôi động tại phố đi bộ Nguyễn Huệ"
        art_category = "CULTURE"
        art_time = self.now + timedelta(days=2)  # 48 hours later

        decision, score, breakdown, reason = self.scorer.evaluate_candidate(
            art_title=art_title,
            art_category=art_category,
            art_time=art_time,
            art_lat=cand.latitude,
            art_lng=cand.longitude,
            art_province="TP. Hồ Chí Minh",
            candidate=cand,
        )

        self.assertEqual(decision, ClusteringDecision.CREATE_NEW_EVENT)
        self.assertLess(score, 0.40)

    def test_select_best_match_picks_highest_scoring_candidate(self) -> None:
        """select_best_match correctly identifies the most suitable candidate event."""
        cand_unrelated = self._create_candidate("Khai mạc triển lãm sách Hà Nội", lat=21.0285, lng=105.8542)
        cand_matching = self._create_candidate("Cháy kho hàng tại Quận 7 TP.HCM")

        art_title = "Cảnh sát dập tắt đám cháy kho hàng Quận 7"
        art_category = "ACCIDENT"

        res = self.scorer.select_best_match(
            art_title=art_title,
            art_category=art_category,
            art_time=self.now,
            candidates=[cand_unrelated, cand_matching],
            art_lat=10.7769,
            art_lng=106.7009,
            art_province="TP. Hồ Chí Minh",
        )

        self.assertEqual(res.decision, ClusteringDecision.MERGE)
        self.assertEqual(res.target_event_id, cand_matching.event_id)
        self.assertGreaterEqual(res.composite_score, 0.75)
