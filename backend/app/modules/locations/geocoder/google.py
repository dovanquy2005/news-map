"""Google Maps Geocoding API adapter."""

from __future__ import annotations

import logging
import urllib.parse
from typing import Any, Dict, Optional

import httpx

from backend.app.common.config import load_settings
from backend.app.modules.locations.geocoder.base import BaseGeocoderAdapter
from backend.app.modules.locations.schemas import LocationLevel, ResolvedLocationDTO

logger = logging.getLogger(__name__)

GOOGLE_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


class GoogleMapsGeocoderAdapter(BaseGeocoderAdapter):
    """Adapter for Google Maps Geocoding API with Vietnamese bounds biasing."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout_seconds: float = 5.0,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self._api_key = api_key or load_settings().maps_server_key.get_secret_value()
        self._timeout = timeout_seconds
        self._http_client = http_client

    def geocode(
        self, query: str, bounds_bias: Optional[Dict[str, Any]] = None
    ) -> Optional[ResolvedLocationDTO]:
        """Geocode query string using Google Maps Geocoding API."""
        if not self._api_key:
            logger.debug("Google Maps server key is not configured. Skipping external call.")
            return None

        clean_query = query.strip()[:300]
        if not clean_query:
            return None

        params: Dict[str, str] = {
            "address": clean_query,
            "components": "country:VN",
            "language": "vi",
            "key": self._api_key,
        }

        if bounds_bias and "bbox" in bounds_bias:
            bbox = bounds_bias["bbox"]  # [min_lat, min_lng, max_lat, max_lng]
            if len(bbox) == 4:
                params["bounds"] = f"{bbox[0]},{bbox[1]}|{bbox[2]},{bbox[3]}"

        try:
            client = self._http_client or httpx.Client(timeout=self._timeout)
            response = client.get(GOOGLE_GEOCODE_URL, params=params)
            if response.status_code != 200:
                logger.warning(
                    "Google Maps Geocoding API returned status %d: %s",
                    response.status_code,
                    response.text[:200],
                )
                return None

            data = response.json()
            if data.get("status") != "OK" or not data.get("results"):
                logger.info("Google Maps Geocoding returned no results for '%s' (status: %s)", clean_query, data.get("status"))
                return None

            result = data["results"][0]
            loc = result["geometry"]["location"]
            lat = float(loc["lat"])
            lng = float(loc["lng"])
            address = result.get("formatted_address", clean_query)
            location_type = result.get("geometry", {}).get("location_type", "APPROXIMATE")

            if location_type == "ROOFTOP":
                confidence = 0.95
                is_approximate = False
                level = LocationLevel.STREET
            elif location_type == "RANGE_INTERPOLATED":
                confidence = 0.90
                is_approximate = False
                level = LocationLevel.STREET
            elif location_type == "GEOMETRIC_CENTER":
                confidence = 0.70
                is_approximate = True
                level = LocationLevel.WARD
            else:
                confidence = 0.50
                is_approximate = True
                level = LocationLevel.DISTRICT

            return ResolvedLocationDTO(
                latitude=lat,
                longitude=lng,
                resolved_address=address,
                location_level=level,
                location_confidence=confidence,
                is_approximate=is_approximate,
                provider="GOOGLE_MAPS",
                raw_response={"place_id": result.get("place_id"), "location_type": location_type},
            )

        except Exception as e:
            logger.warning("Google Maps geocoding error for '%s': %s", clean_query, e)
            return None
        finally:
            if not self._http_client and "client" in locals():
                client.close()
