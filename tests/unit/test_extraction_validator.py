"""Unit tests for ExtractionValidator and EventExtractionSchema."""

from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import unittest

from pydantic import ValidationError

from backend.app.modules.events.schemas.categories import EventCategory
from backend.app.modules.events.validators.extraction_validator import ExtractionValidator

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "llm_outputs"


class TestExtractionValidatorUnit(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = ExtractionValidator()

    def test_valid_json_fixture_passes(self) -> None:
        with open(FIXTURES_DIR / "valid_extraction.json", "r", encoding="utf-8") as f:
            raw = f.read()

        dto = self.validator.validate_extraction(raw)
        self.assertEqual(dto.event_type, EventCategory.INFRASTRUCTURE)
        self.assertEqual(dto.province, "TP. Hồ Chí Minh")
        self.assertEqual(len(dto.facts), 3)
        self.assertAlmostEqual(dto.extraction_confidence, 0.95)

    def test_markdown_wrapped_json_parsed_successfully(self) -> None:
        markdown_output = """Dưới đây là kết quả trích xuất dạng JSON:
```json
{
  "event_title": "Tai nạn giao thông nghiêm trọng trên Quốc lộ 1A",
  "event_type": "ACCIDENT",
  "location_text": "Huyện Thường Tín, Hà Nội",
  "province": "HN",
  "confidence_score": 0.90
}
```
Chúc một ngày tốt lành!"""
        dto = self.validator.validate_extraction(markdown_output)
        self.assertEqual(dto.event_title, "Tai nạn giao thông nghiêm trọng trên Quốc lộ 1A")
        self.assertEqual(dto.event_type, EventCategory.ACCIDENT)
        self.assertEqual(dto.province, "Hà Nội")

    def test_invalid_short_title_fails(self) -> None:
        payload = {
            "event_title": "Ngắn",  # Less than 10 characters
            "event_type": "FIRE",
        }
        with self.assertRaises(ValidationError):
            self.validator.validate_extraction(payload)

    def test_unknown_category_falls_back_to_other(self) -> None:
        payload = {
            "event_title": "Sự kiện thời sự diễn ra tại địa phương",
            "event_type": "UNKNOWN_CUSTOM_TYPE",
        }
        dto = self.validator.validate_extraction(payload)
        self.assertEqual(dto.event_type, EventCategory.OTHER)

    def test_temporal_sanity_caps_far_future_timestamp(self) -> None:
        now = datetime.now(timezone.utc)
        future_date = now + timedelta(days=5)  # 5 days in the future

        payload = {
            "event_title": "Dự báo thời tiết và diễn biến sự kiện",
            "occurred_at": future_date.isoformat(),
        }
        dto = self.validator.validate_extraction(payload, reference_time=now)
        # Should be capped to reference time now
        self.assertLessEqual(dto.occurred_at, now + timedelta(minutes=1))


if __name__ == "__main__":
    unittest.main()
