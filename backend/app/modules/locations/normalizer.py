"""Location extraction and hierarchical normalization service."""

from __future__ import annotations

import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.app.modules.locations.schemas import LocationLevel, NormalizedLocationDTO

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).resolve().parent / "data" / "vn_administrative.json"


class LocationNormalizer:
    """Deterministic parser and normalizer for Vietnamese administrative hierarchies."""

    def __init__(self, data_path: Optional[Path] = None) -> None:
        path = data_path or DATA_FILE
        self._provinces_data: List[Dict[str, Any]] = []
        self._alias_map: Dict[str, str] = {}
        self._province_names: set[str] = set()
        self._province_districts: Dict[str, List[str]] = {}
        self._district_prefixes: List[str] = []
        self._ward_prefixes: List[str] = []
        self._street_prefixes: List[str] = []
        self._poi_prefixes: List[str] = []

        self._load_data(path)

    def _load_data(self, path: Path) -> None:
        if not path.exists():
            logger.warning("Administrative dataset not found at %s. Using fallback data.", path)
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._provinces_data = data.get("provinces", [])
        self._district_prefixes = data.get("district_prefixes", [])
        self._ward_prefixes = data.get("ward_prefixes", [])
        self._street_prefixes = data.get("street_prefixes", [])
        self._poi_prefixes = data.get("poi_prefixes", [])

        for p in self._provinces_data:
            name = p["name"]
            self._province_names.add(name)
            self._alias_map[name.lower()] = name
            for alias in p.get("aliases", []):
                self._alias_map[alias.lower().strip()] = name
            self._province_districts[name] = p.get("districts", [])

    def sanitize_input(self, raw_text: str) -> str:
        """Sanitize input string and bound its length to prevent ReDoS."""
        if not raw_text:
            return ""
        # Strip control characters
        cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", raw_text)
        # Cap length
        cleaned = cleaned[:500]
        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def normalize(
        self,
        raw_text: str,
        hint_province: Optional[str] = None,
        hint_district: Optional[str] = None,
        hint_ward: Optional[str] = None,
    ) -> NormalizedLocationDTO:
        """Parse raw text into hierarchical administrative components and assign confidence."""
        text = self.sanitize_input(raw_text)
        if not text:
            return NormalizedLocationDTO(
                raw_text="",
                location_level=LocationLevel.UNKNOWN,
                baseline_confidence=0.0,
            )

        province = self._resolve_province(text, hint_province)
        district = self._resolve_district(text, province, hint_district)
        ward = self._resolve_ward(text, hint_ward)
        street = self._resolve_street(text)
        landmark = self._resolve_landmark(text)

        # Check for national reference if no province
        is_vietnam = "việt nam" in text.lower() or "viet nam" in text.lower()

        # Determine level and baseline confidence
        if landmark:
            level = LocationLevel.POI
            confidence = 0.95
        elif street:
            level = LocationLevel.STREET
            confidence = 0.90
        elif ward:
            level = LocationLevel.WARD
            confidence = 0.75
        elif district:
            level = LocationLevel.DISTRICT
            confidence = 0.60
        elif province:
            level = LocationLevel.PROVINCE
            confidence = 0.40
        elif is_vietnam:
            level = LocationLevel.COUNTRY
            confidence = 0.20
        else:
            level = LocationLevel.UNKNOWN
            confidence = 0.10

        return NormalizedLocationDTO(
            raw_text=text,
            country="Việt Nam",
            province=province,
            district=district,
            ward=ward,
            street=street,
            landmark=landmark,
            location_level=level,
            baseline_confidence=confidence,
        )

    def _resolve_province(self, text: str, hint: Optional[str] = None) -> Optional[str]:
        if hint and hint.lower().strip() in self._alias_map:
            return self._alias_map[hint.lower().strip()]

        # Split text into comma-separated segments (checked right to left)
        segments = [s.strip() for s in text.split(",") if s.strip()]
        for seg in reversed(segments):
            seg_lower = seg.lower()
            # Strip common preposition/prefixes
            clean_seg = re.sub(r"^(tại|ở|khu vực|tỉnh|thành phố|tp\.?)\s+", "", seg_lower).strip()
            if clean_seg in self._alias_map:
                return self._alias_map[clean_seg]
            if seg_lower in self._alias_map:
                return self._alias_map[seg_lower]

        # Scan text with sorted alias lengths (longer aliases first)
        sorted_aliases = sorted(self._alias_map.keys(), key=len, reverse=True)
        text_lower = text.lower()
        for alias in sorted_aliases:
            # Skip very short aliases (like "hn", "đn") unless surrounded by boundaries or non-alphanumeric
            if len(alias) <= 3:
                pattern = rf"(?:\b|\W){re.escape(alias)}(?:\b|\W|$)"
                if re.search(pattern, text_lower):
                    return self._alias_map[alias]
            else:
                if alias in text_lower:
                    return self._alias_map[alias]

        return None

    def _resolve_district(
        self, text: str, province: Optional[str] = None, hint: Optional[str] = None
    ) -> Optional[str]:
        if hint:
            return hint.strip()

        segments = [s.strip() for s in text.split(",") if s.strip()]

        # Check segments with district prefixes
        for seg in segments:
            seg_lower = seg.lower()
            for prefix in self._district_prefixes:
                if seg_lower.startswith(prefix + " "):
                    val = seg.strip()
                    # Clean up if comma or extra text
                    return val

        # If province is known, check known districts in that province
        if province and province in self._province_districts:
            text_lower = text.lower()
            for d in self._province_districts[province]:
                d_lower = d.lower()
                pattern = rf"(?:\b|\W){re.escape(d_lower)}(?:\b|\W|$)"
                if re.search(pattern, text_lower):
                    # Prefer with prefix if present
                    return d

        return None

    def _resolve_ward(self, text: str, hint: Optional[str] = None) -> Optional[str]:
        if hint:
            return hint.strip()

        segments = [s.strip() for s in text.split(",") if s.strip()]
        for seg in segments:
            seg_lower = seg.lower()
            for prefix in self._ward_prefixes:
                if seg_lower.startswith(prefix + " "):
                    return seg.strip()

        # Regex search for ward in unstructured text
        match = re.search(r"\b(phường|xã|thị trấn|p\.)\s+([A-Za-z0-9À-ỹ\s]+?)(?=,|\bquận|\bhuyện|\btp|\bthành phố|$)", text, re.IGNORECASE)
        if match:
            return match.group(0).strip()

        return None

    def _resolve_street(self, text: str) -> Optional[str]:
        segments = [s.strip() for s in text.split(",") if s.strip()]
        for seg in segments:
            seg_lower = seg.lower()
            for prefix in self._street_prefixes:
                if seg_lower.startswith(prefix + " "):
                    return seg.strip()

        match = re.search(
            r"\b(đường|phố|đại lộ|quốc lộ|ql\.|ql|cao tốc|cầu|ngõ|hẻm)\s+([A-Za-z0-9À-ỹ\s\.\-]+?)(?=,|\bphường|\bxã|\bquận|\bhuyện|\btp|$)",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(0).strip()

        return None

    def _resolve_landmark(self, text: str) -> Optional[str]:
        segments = [s.strip() for s in text.split(",") if s.strip()]
        for seg in segments:
            seg_lower = seg.lower()
            for prefix in self._poi_prefixes:
                # Do not treat pure bridges like 'cầu sài gòn' as POI if street prefix already matches
                if seg_lower.startswith(prefix + " "):
                    return seg.strip()

        match = re.search(
            r"\b(chợ|bệnh viện|bv|trường đại học|trường|sân bay|cảng|toà nhà|tòa nhà|landmark|công viên|ga)\s+([A-Za-z0-9À-ỹ\s]+?)(?=,|\bđường|\bphường|\bquận|$)",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(0).strip()

        return None
