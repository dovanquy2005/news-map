"""Location similarity calculation for event clustering."""

from __future__ import annotations

import math
from typing import Optional


def _haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def compute_location_similarity(
    art_lat: Optional[float],
    art_lng: Optional[float],
    art_province: Optional[str],
    cand_lat: float,
    cand_lng: float,
    cand_label: Optional[str] = None,
    distance_meters: Optional[float] = None,
) -> float:
    """Compute physical proximity and administrative match score (0.0 to 1.0)."""
    if art_lat is not None and art_lng is not None:
        dist = distance_meters
        if dist is None:
            dist = _haversine_meters(art_lat, art_lng, cand_lat, cand_lng)

        if dist <= 100.0:
            return 1.0
        elif dist <= 500.0:
            return 0.90
        elif dist <= 2000.0:
            return 0.75
        elif dist <= 10000.0:
            return 0.50
        elif dist <= 30000.0:
            return 0.30
        else:
            # Beyond 30km: check if same province
            if art_province and cand_label and art_province.lower() in cand_label.lower():
                return 0.20
            return 0.0

    # No coordinates on article: fallback to province string match
    if art_province and cand_label and art_province.lower() in cand_label.lower():
        return 0.40

    return 0.10
