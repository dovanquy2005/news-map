"""Unit tests for Vietnamese location extraction and normalization."""

import time
import unittest

from backend.app.modules.locations.normalizer import LocationNormalizer
from backend.app.modules.locations.schemas import LocationLevel


class TestLocationNormalizerUnit(unittest.TestCase):
    """Test suite for LocationNormalizer."""

    def setUp(self) -> None:
        self.normalizer = LocationNormalizer()

    def test_full_address_high_confidence(self) -> None:
        raw = "Đường Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP.HCM"
        res = self.normalizer.normalize(raw)

        self.assertEqual(res.country, "Việt Nam")
        self.assertEqual(res.province, "TP. Hồ Chí Minh")
        self.assertEqual(res.district, "Quận 1")
        self.assertEqual(res.ward, "Phường Bến Nghé")
        self.assertEqual(res.street, "Đường Nguyễn Huệ")
        self.assertIn(res.location_level, [LocationLevel.STREET, LocationLevel.POI])
        self.assertGreaterEqual(res.baseline_confidence, 0.85)

    def test_district_level_medium_confidence(self) -> None:
        raw = "Quận 7, TP. Hồ Chí Minh"
        res = self.normalizer.normalize(raw)

        self.assertEqual(res.province, "TP. Hồ Chí Minh")
        self.assertEqual(res.district, "Quận 7")
        self.assertIsNone(res.ward)
        self.assertIsNone(res.street)
        self.assertEqual(res.location_level, LocationLevel.DISTRICT)
        self.assertGreaterEqual(res.baseline_confidence, 0.50)
        self.assertLessEqual(res.baseline_confidence, 0.69)

    def test_province_level_low_medium_confidence(self) -> None:
        raw = "tại Đà Nẵng"
        res = self.normalizer.normalize(raw)

        self.assertEqual(res.province, "Đà Nẵng")
        self.assertIsNone(res.district)
        self.assertIsNone(res.ward)
        self.assertEqual(res.location_level, LocationLevel.PROVINCE)
        self.assertGreaterEqual(res.baseline_confidence, 0.30)
        self.assertLessEqual(res.baseline_confidence, 0.49)

    def test_alias_resolution_sai_gon(self) -> None:
        raw = "Sài Gòn"
        res = self.normalizer.normalize(raw)

        self.assertEqual(res.province, "TP. Hồ Chí Minh")
        self.assertEqual(res.location_level, LocationLevel.PROVINCE)

    def test_alias_resolution_hanoi_and_danang(self) -> None:
        res_hn = self.normalizer.normalize("ở HN")
        self.assertEqual(res_hn.province, "Hà Nội")

        res_dn = self.normalizer.normalize("khu vực ĐN")
        self.assertEqual(res_dn.province, "Đà Nẵng")

    def test_landmark_poi_high_confidence(self) -> None:
        raw = "Chợ Bến Thành, Quận 1, TP. Hồ Chí Minh"
        res = self.normalizer.normalize(raw)

        self.assertEqual(res.province, "TP. Hồ Chí Minh")
        self.assertEqual(res.district, "Quận 1")
        self.assertEqual(res.landmark, "Chợ Bến Thành")
        self.assertEqual(res.location_level, LocationLevel.POI)
        self.assertGreaterEqual(res.baseline_confidence, 0.85)

    def test_malformed_non_geographical_text(self) -> None:
        raw = "Hội nghị bàn tròn về trí tuệ nhân tạo và kinh tế số"
        res = self.normalizer.normalize(raw)

        self.assertEqual(res.location_level, LocationLevel.UNKNOWN)
        self.assertLess(res.baseline_confidence, 0.30)
        self.assertIsNone(res.province)

    def test_empty_input_returns_unknown(self) -> None:
        res = self.normalizer.normalize("")
        self.assertEqual(res.location_level, LocationLevel.UNKNOWN)
        self.assertEqual(res.baseline_confidence, 0.0)

    def test_redos_protection_and_sanitization(self) -> None:
        # 1000 characters input
        long_text = "Đường Giải Phóng, " * 100
        start = time.perf_counter()
        res = self.normalizer.normalize(long_text)
        duration = time.perf_counter() - start

        self.assertLess(duration, 0.05)  # Well within bounds
        self.assertLessEqual(len(res.raw_text), 500)

    def test_performance_sub_5ms(self) -> None:
        sample = "Số 123 Đường Nam Kỳ Khởi Nghĩa, Phường Võ Thị Sáu, Quận 3, TP.HCM"
        # Warmup
        self.normalizer.normalize(sample)

        start = time.perf_counter()
        iterations = 50
        for _ in range(iterations):
            self.normalizer.normalize(sample)
        elapsed_per_call = (time.perf_counter() - start) / iterations

        # Target is < 5ms (0.005s)
        self.assertLess(elapsed_per_call, 0.005)
