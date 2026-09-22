"""Internal offline gazetteer geocoder using precomputed administrative centroids."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from backend.app.modules.locations.geocoder.base import BaseGeocoderAdapter
from backend.app.modules.locations.normalizer import LocationNormalizer
from backend.app.modules.locations.schemas import LocationLevel, ResolvedLocationDTO

logger = logging.getLogger(__name__)

CENTROIDS_FILE = Path(__file__).resolve().parent.parent / "data" / "vn_centroids.json"


class InternalGazetteerGeocoder(BaseGeocoderAdapter):
    """Offline geocoder utilizing official Vietnamese administrative centroids."""

    def __init__(
        self,
        centroids_path: Optional[Path] = None,
        normalizer: Optional[LocationNormalizer] = None,
    ) -> None:
        self._path = centroids_path or CENTROIDS_FILE
        self._normalizer = normalizer or LocationNormalizer()
        self._centroids: Dict[str, Dict[str, Any]] = {}
        self._load_centroids()

    def _load_centroids(self) -> None:
        if not self._path.exists():
            logger.warning("Centroids data file not found at %s", self._path)
            return

        with open(self._path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._centroids = data.get("provinces", {})

    def get_province_centroid(self, province_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve centroid and bbox for a canonical province name."""
        return self._centroids.get(province_name)

    def geocode(
        self, query: str, bounds_bias: Optional[Dict[str, Any]] = None
    ) -> Optional[ResolvedLocationDTO]:
        """Resolve query to provincial centroid using gazetteer lookup."""
        normalized = self._normalizer.normalize(query)
        province = normalized.province

        if not province:
            return None

        centroid_info = self.get_province_centroid(province)
        if not centroid_info:
            return None

        # Level determines confidence and approximate flag
        is_approximate = normalized.location_level in [
            LocationLevel.PROVINCE,
            LocationLevel.COUNTRY,
            LocationLevel.UNKNOWN,
        ]
        label = (
            f"Vị trí gần đúng — chỉ xác định được {province}"
            if is_approximate
            else f"{province}, Việt Nam"
        )

        return ResolvedLocationDTO(
            latitude=centroid_info["lat"],
            longitude=centroid_info["lng"],
            resolved_address=label,
            location_level=normalized.location_level,
            location_confidence=normalized.baseline_confidence,
            is_approximate=is_approximate,
            provider="INTERNAL_GAZETTEER",
            raw_response={"bbox": centroid_info.get("bbox")},
        )
