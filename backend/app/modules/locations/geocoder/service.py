"""Spatial resolution and geocoding orchestration service."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, Optional

import redis

from backend.app.modules.locations.geocoder.base import BaseGeocoderAdapter
from backend.app.modules.locations.geocoder.gazetteer import InternalGazetteerGeocoder
from backend.app.modules.locations.geocoder.google import GoogleMapsGeocoderAdapter
from backend.app.modules.locations.normalizer import LocationNormalizer
from backend.app.modules.locations.schemas import (
    LocationLevel,
    NormalizedLocationDTO,
    ResolvedLocationDTO,
)

logger = logging.getLogger(__name__)

CACHE_PREFIX = "vnm:cache:geocode:"
CACHE_TTL_SECONDS = 30 * 86400  # 30 days


class GeocoderService:
    """Orchestrates normalization, caching, external geocoding, and centroid fallback."""

    def __init__(
        self,
        normalizer: Optional[LocationNormalizer] = None,
        primary_geocoder: Optional[BaseGeocoderAdapter] = None,
        gazetteer: Optional[InternalGazetteerGeocoder] = None,
        redis_client: Optional[redis.Redis] = None,
    ) -> None:
        self._normalizer = normalizer or LocationNormalizer()
        self._gazetteer = gazetteer or InternalGazetteerGeocoder(normalizer=self._normalizer)
        self._primary = primary_geocoder or GoogleMapsGeocoderAdapter()
        self._redis = redis_client

    def resolve(
        self,
        query: str,
        hint_province: Optional[str] = None,
        hint_district: Optional[str] = None,
        hint_ward: Optional[str] = None,
    ) -> Optional[ResolvedLocationDTO]:
        """Resolve a textual address to spatial coordinates respecting centroid fallback rules."""
        if not query or not query.strip():
            return None

        # 1. Hierarchical normalization
        normalized: NormalizedLocationDTO = self._normalizer.normalize(
            query,
            hint_province=hint_province,
            hint_district=hint_district,
            hint_ward=hint_ward,
        )

        # 2. Strict centroid fallback rule:
        # If the location is ONLY resolved at Province or Country level,
        # we MUST NOT guess or query an arbitrary street address.
        if normalized.location_level == LocationLevel.PROVINCE and normalized.province:
            return self._resolve_province_centroid(normalized.province)

        if normalized.location_level == LocationLevel.COUNTRY:
            # Fallback to general Vietnam centroid (Hà Nội administrative center)
            centroid = self._gazetteer.get_province_centroid("Hà Nội")
            if centroid:
                return ResolvedLocationDTO(
                    latitude=centroid["lat"],
                    longitude=centroid["lng"],
                    resolved_address="Vị trí gần đúng — chỉ xác định được toàn quốc Việt Nam",
                    location_level=LocationLevel.COUNTRY,
                    location_confidence=0.20,
                    is_approximate=True,
                    provider="INTERNAL_GAZETTEER",
                )

        if normalized.location_level == LocationLevel.UNKNOWN:
            logger.info("Location '%s' could not be resolved to any administrative division", query)
            return None

        # 3. For fine-grained locations (DISTRICT, WARD, STREET, POI):
        # Check cache
        cache_key = self._generate_cache_key(query)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        # Try primary geocoder (e.g. Google Maps)
        bounds_bias = None
        if normalized.province:
            centroid_data = self._gazetteer.get_province_centroid(normalized.province)
            if centroid_data and "bbox" in centroid_data:
                bounds_bias = {"bbox": centroid_data["bbox"]}

        resolved = self._primary.geocode(query, bounds_bias=bounds_bias)
        if resolved:
            self._set_cached(cache_key, resolved)
            return resolved

        # 4. Fallback to gazetteer using province if primary geocoder fails or unavailable
        if normalized.province:
            logger.info("Primary geocoder yielded no results for '%s'. Falling back to gazetteer.", query)
            fallback = self._resolve_province_centroid(normalized.province)
            if fallback:
                return fallback

        return None

    def _resolve_province_centroid(self, province: str) -> Optional[ResolvedLocationDTO]:
        centroid = self._gazetteer.get_province_centroid(province)
        if not centroid:
            return None

        return ResolvedLocationDTO(
            latitude=centroid["lat"],
            longitude=centroid["lng"],
            resolved_address=f"Vị trí gần đúng — chỉ xác định được {province}",
            location_level=LocationLevel.PROVINCE,
            location_confidence=0.40,
            is_approximate=True,
            provider="INTERNAL_GAZETTEER",
            raw_response={"bbox": centroid.get("bbox")},
        )

    def _generate_cache_key(self, query: str) -> str:
        clean = query.strip().lower()
        digest = hashlib.sha256(clean.encode("utf-8")).hexdigest()
        return f"{CACHE_PREFIX}{digest}"

    def _get_cached(self, key: str) -> Optional[ResolvedLocationDTO]:
        if not self._redis:
            return None
        try:
            val = self._redis.get(key)
            if val:
                data = json.loads(val.decode("utf-8") if isinstance(val, bytes) else val)
                return ResolvedLocationDTO.model_validate(data)
        except Exception as e:
            logger.warning("Redis geocode cache read failed for key %s: %s", key, e)
        return None

    def _set_cached(self, key: str, resolved: ResolvedLocationDTO) -> None:
        if not self._redis:
            return
        try:
            val = resolved.model_dump_json()
            self._redis.setex(key, CACHE_TTL_SECONDS, val)
        except Exception as e:
            logger.warning("Redis geocode cache write failed for key %s: %s", key, e)
