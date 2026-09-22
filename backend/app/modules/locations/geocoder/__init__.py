"""Geocoder package for spatial resolution and adapters."""

from backend.app.modules.locations.geocoder.base import BaseGeocoderAdapter
from backend.app.modules.locations.geocoder.gazetteer import InternalGazetteerGeocoder
from backend.app.modules.locations.geocoder.google import GoogleMapsGeocoderAdapter
from backend.app.modules.locations.geocoder.service import GeocoderService

__all__ = [
    "BaseGeocoderAdapter",
    "InternalGazetteerGeocoder",
    "GoogleMapsGeocoderAdapter",
    "GeocoderService",
]
