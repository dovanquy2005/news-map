"""Schemas for location normalization and spatial resolution."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class LocationLevel(str, Enum):
    """Administrative and spatial granularity levels for Vietnamese locations."""

    COUNTRY = "COUNTRY"
    PROVINCE = "PROVINCE"
    DISTRICT = "DISTRICT"
    WARD = "WARD"
    STREET = "STREET"
    POI = "POI"
    UNKNOWN = "UNKNOWN"


class NormalizedLocationDTO(BaseModel):
    """Normalized administrative hierarchy and baseline confidence."""

    raw_text: str
    country: str = "Việt Nam"
    province: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None
    street: Optional[str] = None
    landmark: Optional[str] = None
    location_level: LocationLevel = LocationLevel.UNKNOWN
    baseline_confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ResolvedLocationDTO(BaseModel):
    """Spatial coordinates and resolution metadata for a location."""

    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    resolved_address: str
    location_level: LocationLevel
    location_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    is_approximate: bool = False
    provider: str
    raw_response: Optional[Dict[str, Any]] = None
