"""Extraction validator enforcing schema constraints and domain sanity checks."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
import json
import logging
import re
from typing import Any, Optional

from pydantic import ValidationError

from backend.app.modules.events.schemas.categories import EventCategory
from backend.app.modules.events.schemas.extraction import (
    EntityItem,
    EventExtractionSchema,
    ValidatedExtractionDTO,
)

logger = logging.getLogger(__name__)

MARKDOWN_JSON_REGEX = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)

VN_PROVINCES = [
    "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu", "Bắc Ninh",
    "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau",
    "Cần Thơ", "Cao Bằng", "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai",
    "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương",
    "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang",
    "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định",
    "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình",
    "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La",
    "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang",
    "TP. Hồ Chí Minh", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
]

PROVINCE_ALIAS_MAP: dict[str, str] = {
    "hcm": "TP. Hồ Chí Minh",
    "tp.hcm": "TP. Hồ Chí Minh",
    "tp hcm": "TP. Hồ Chí Minh",
    "tphcm": "TP. Hồ Chí Minh",
    "sài gòn": "TP. Hồ Chí Minh",
    "sai gon": "TP. Hồ Chí Minh",
    "hồ chí minh": "TP. Hồ Chí Minh",
    "hn": "Hà Nội",
    "hà nội": "Hà Nội",
    "ha noi": "Hà Nội",
    "đà nẵng": "Đà Nẵng",
    "da nang": "Đà Nẵng",
    "đn": "Đà Nẵng",
    "hải phòng": "Hải Phòng",
    "hai phong": "Hải Phòng",
    "cần thơ": "Cần Thơ",
    "can tho": "Cần Thơ",
}


class ExtractionValidator:
    """Validates raw LLM outputs against Pydantic schema and domain rules."""

    @staticmethod
    def parse_raw_json(raw_text: str) -> dict[str, Any]:
        """Parses JSON from raw string, falling back to markdown block extraction."""
        clean_text = raw_text.strip()

        # 1. Direct JSON parse
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            pass

        # 2. Markdown fence extraction
        match = MARKDOWN_JSON_REGEX.search(clean_text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 3. Outer bracket extraction
        start_idx = clean_text.find("{")
        end_idx = clean_text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(clean_text[start_idx : end_idx + 1])
            except json.JSONDecodeError:
                pass

        raise ValueError("Failed to extract valid JSON from LLM output")

    @classmethod
    def standardize_province(cls, province_raw: Optional[str]) -> Optional[str]:
        """Maps province name or alias to canonical Vietnamese province name."""
        if not province_raw:
            return None
        clean = province_raw.strip().lower()
        if clean.startswith("tỉnh ") or clean.startswith("thành phố ") or clean.startswith("tp. "):
            clean = clean.split(" ", 1)[1].strip()

        # Check alias map
        if clean in PROVINCE_ALIAS_MAP:
            return PROVINCE_ALIAS_MAP[clean]

        # Case-insensitive match against canonical list
        for p in VN_PROVINCES:
            if p.lower() == clean or p.lower() == province_raw.strip().lower():
                return p

        return province_raw.strip()

    @classmethod
    def validate_temporal_sanity(
        cls,
        occurred_at: Optional[datetime],
        reference_time: Optional[datetime] = None,
    ) -> Optional[datetime]:
        """Ensures occurred_at does not exceed future tolerance (+24h)."""
        if not occurred_at:
            return None

        now = reference_time or datetime.now(timezone.utc)
        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)

        # Future limit check: cannot be > 24 hours in the future
        if occurred_at > now + timedelta(days=1):
            logger.warning(
                "Extracted occurrence time %s is more than 24h into the future. Capping to reference time %s",
                occurred_at,
                now,
            )
            return now

        return occurred_at

    def validate_extraction(
        self,
        raw_output: str | dict[str, Any],
        reference_time: Optional[datetime] = None,
    ) -> ValidatedExtractionDTO:
        """Pipeline: raw input -> json parse -> pydantic validation -> domain sanity checks."""
        # 1. Parse JSON if string
        if isinstance(raw_output, str):
            payload = self.parse_raw_json(raw_output)
        else:
            payload = raw_output

        # Handle fallback if model returned 'title' instead of 'event_title'
        if "event_title" not in payload and "title" in payload:
            payload["event_title"] = payload["title"]
        if "event_type" not in payload and "category" in payload:
            payload["event_type"] = payload["category"]
        if "location_text" not in payload and "location_name" in payload:
            payload["location_text"] = payload["location_name"]
        if "facts" not in payload and "key_facts" in payload:
            payload["facts"] = payload["key_facts"]

        # 2. Pydantic validation
        validated = EventExtractionSchema.model_validate(payload)

        # 3. Domain sanity checks: province normalization
        canon_province = self.standardize_province(validated.province)

        # 4. Temporal sanity check
        safe_occurred_at = self.validate_temporal_sanity(validated.occurred_at, reference_time)

        return ValidatedExtractionDTO(
            event_title=validated.event_title.strip(),
            event_type=validated.event_type,
            is_event=validated.is_event,
            location_text=validated.location_text.strip() if validated.location_text else None,
            province=canon_province,
            district=validated.district.strip() if validated.district else None,
            ward=validated.ward.strip() if validated.ward else None,
            occurred_at=safe_occurred_at,
            facts=validated.facts,
            entities=validated.entities,
            uncertainty_notes=validated.uncertainty_notes,
            extraction_confidence=validated.extraction_confidence,
        )
