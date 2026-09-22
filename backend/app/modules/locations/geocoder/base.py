"""Base interface for geocoder adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from backend.app.modules.locations.schemas import ResolvedLocationDTO


class BaseGeocoderAdapter(ABC):
    """Abstract adapter defining the geocoding contract."""

    @abstractmethod
    def geocode(
        self, query: str, bounds_bias: Optional[Dict[str, Any]] = None
    ) -> Optional[ResolvedLocationDTO]:
        """Synchronously geocode a textual address query."""
        raise NotImplementedError

    async def async_geocode(
        self, query: str, bounds_bias: Optional[Dict[str, Any]] = None
    ) -> Optional[ResolvedLocationDTO]:
        """Asynchronously geocode a textual address query."""
        return self.geocode(query, bounds_bias)
