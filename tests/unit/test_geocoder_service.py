"""Unit tests for GeocoderService, Centroid Fallback rule, and caching."""

import json
import unittest
from unittest.mock import MagicMock

from backend.app.modules.locations.geocoder.base import BaseGeocoderAdapter
from backend.app.modules.locations.geocoder.gazetteer import InternalGazetteerGeocoder
from backend.app.modules.locations.geocoder.service import GeocoderService
from backend.app.modules.locations.normalizer import LocationNormalizer
from backend.app.modules.locations.schemas import LocationLevel, ResolvedLocationDTO


class MockPrimaryGeocoder(BaseGeocoderAdapter):
    """Mock geocoder for external provider testing."""

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.call_count = 0

    def geocode(self, query: str, bounds_bias=None):
        self.call_count += 1
        if self.should_fail:
            return None

        return ResolvedLocationDTO(
            latitude=10.7769,
            longitude=106.6953,
            resolved_address="135 Hai Bà Trưng, Bến Nghé, Quận 1, TP. Hồ Chí Minh",
            location_level=LocationLevel.STREET,
            location_confidence=0.95,
            is_approximate=False,
            provider="GOOGLE_MAPS",
        )


class TestGeocoderServiceUnit(unittest.TestCase):
    """Test suite for GeocoderService."""

    def setUp(self) -> None:
        self.normalizer = LocationNormalizer()
        self.gazetteer = InternalGazetteerGeocoder(normalizer=self.normalizer)
        self.mock_primary = MockPrimaryGeocoder(should_fail=False)
        self.mock_redis = MagicMock()
        # By default, mock redis has no cached keys
        self.mock_redis.get.return_value = None

        self.service = GeocoderService(
            normalizer=self.normalizer,
            primary_geocoder=self.mock_primary,
            gazetteer=self.gazetteer,
            redis_client=self.mock_redis,
        )

    def test_province_level_centroid_fallback_rule(self) -> None:
        """Province-level mention must return official centroid with approximate flag."""
        query = "tại Đà Nẵng"
        resolved = self.service.resolve(query)

        self.assertIsNotNone(resolved)
        self.assertTrue(resolved.is_approximate)
        self.assertEqual(resolved.location_level, LocationLevel.PROVINCE)
        self.assertEqual(
            resolved.resolved_address,
            "Vị trí gần đúng — chỉ xác định được Đà Nẵng",
        )
        self.assertEqual(resolved.provider, "INTERNAL_GAZETTEER")
        self.assertAlmostEqual(resolved.latitude, 16.0544, places=3)
        self.assertAlmostEqual(resolved.longitude, 108.2022, places=3)
        # Verify external primary geocoder was NEVER called for province-only mention
        self.assertEqual(self.mock_primary.call_count, 0)

    def test_full_address_calls_primary_and_caches(self) -> None:
        """Specific street address calls primary geocoder and caches in Redis."""
        query = "135 Hai Bà Trưng, Quận 1, TP.HCM"
        resolved = self.service.resolve(query)

        self.assertIsNotNone(resolved)
        self.assertFalse(resolved.is_approximate)
        self.assertEqual(resolved.provider, "GOOGLE_MAPS")
        self.assertGreaterEqual(resolved.location_confidence, 0.85)
        self.assertEqual(self.mock_primary.call_count, 1)

        # Verify cached in Redis with 30-day TTL
        self.mock_redis.setex.assert_called_once()
        args, kwargs = self.mock_redis.setex.call_args
        self.assertTrue(args[0].startswith("vnm:cache:geocode:"))
        self.assertEqual(args[1], 30 * 86400)

    def test_cache_hit_bypasses_primary_geocoder(self) -> None:
        """Redis cache hit returns immediately without calling external adapter."""
        cached_dto = ResolvedLocationDTO(
            latitude=21.0285,
            longitude=105.8542,
            resolved_address="Phố Tràng Tiền, Hoàn Kiếm, Hà Nội",
            location_level=LocationLevel.STREET,
            location_confidence=0.90,
            is_approximate=False,
            provider="GOOGLE_MAPS",
        )
        self.mock_redis.get.return_value = cached_dto.model_dump_json().encode("utf-8")

        query = "Phố Tràng Tiền, Quận Hoàn Kiếm, Hà Nội"
        resolved = self.service.resolve(query)

        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.resolved_address, "Phố Tràng Tiền, Hoàn Kiếm, Hà Nội")
        self.assertEqual(self.mock_primary.call_count, 0)

    def test_primary_failure_falls_back_to_gazetteer(self) -> None:
        """When primary geocoder fails, service falls back to provincial centroid."""
        failing_primary = MockPrimaryGeocoder(should_fail=True)
        service = GeocoderService(
            normalizer=self.normalizer,
            primary_geocoder=failing_primary,
            gazetteer=self.gazetteer,
            redis_client=self.mock_redis,
        )

        query = "Đường Lạ Không Tồn Tại, Quận 1, TP.HCM"
        resolved = service.resolve(query)

        self.assertIsNotNone(resolved)
        self.assertTrue(resolved.is_approximate)
        self.assertEqual(resolved.provider, "INTERNAL_GAZETTEER")
        self.assertEqual(
            resolved.resolved_address,
            "Vị trí gần đúng — chỉ xác định được TP. Hồ Chí Minh",
        )

    def test_unknown_location_returns_none(self) -> None:
        """Non-geographical queries return None."""
        query = "Hội nghị kinh tế đối ngoại toàn cầu"
        resolved = self.service.resolve(query)
        self.assertIsNone(resolved)
        self.assertEqual(self.mock_primary.call_count, 0)
