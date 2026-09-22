"""Unit tests for ConfidenceScoringEngine."""

import unittest

from backend.app.modules.events.confidence import ConfidenceScoringEngine


class TestConfidenceScoringUnit(unittest.TestCase):
    """Test suite for event confidence calculation."""

    def setUp(self) -> None:
        self.engine = ConfidenceScoringEngine()

    def test_high_confidence_multi_source_precise_location(self) -> None:
        """5+ sources, street-level precision, no conflicts -> HIGH confidence."""
        res = self.engine.calculate_confidence(
            source_count=5,
            location_confidence=0.95,
            has_conflicts=False,
            time_span_hours=4.0,
            has_official_source=True,
        )

        self.assertEqual(res.level, "HIGH")
        self.assertGreaterEqual(res.score, 85)
        self.assertTrue(any("5 nguồn" in p for p in res.positive_indicators))

    def test_medium_confidence_two_sources(self) -> None:
        """2 sources, district level -> MEDIUM confidence."""
        res = self.engine.calculate_confidence(
            source_count=2,
            location_confidence=0.60,
            has_conflicts=False,
            time_span_hours=10.0,
            has_official_source=False,
        )

        self.assertEqual(res.level, "MEDIUM")
        self.assertGreaterEqual(res.score, 50)
        self.assertLess(res.score, 80)

    def test_low_confidence_single_source_conflicts(self) -> None:
        """1 source, province only, conflicting facts -> LOW confidence."""
        res = self.engine.calculate_confidence(
            source_count=1,
            location_confidence=0.40,
            has_conflicts=True,
            time_span_hours=72.0,
            has_official_source=False,
        )

        self.assertEqual(res.level, "LOW")
        self.assertLess(res.score, 50)
        self.assertTrue(any("1 nguồn" in w for w in res.warning_indicators))
        self.assertTrue(any("chưa thống nhất" in w for w in res.warning_indicators))
