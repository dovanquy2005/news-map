"""Base source adapter contract and raw article DTO definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from backend.app.common.db.models.source import Source


@dataclass
class RawArticleDTO:
    """Standardized representation of a single extracted feed item before normalization."""

    source_id: UUID
    source_url: str
    title: str
    summary_raw: Optional[str] = None
    published_at_raw: Optional[str] = None
    author_raw: Optional[str] = None
    image_url: Optional[str] = None
    raw_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RawFeedResult:
    """Result of fetching and parsing an external source feed."""

    source_id: UUID
    items: list[RawArticleDTO] = field(default_factory=list)
    item_count: int = 0
    status_code: int = 200
    error_message: Optional[str] = None
    fetched_at: Optional[datetime] = None


@dataclass
class AdapterHealthStatus:
    is_healthy: bool
    response_time_ms: float
    error_message: Optional[str] = None


class BaseSourceAdapter(ABC):
    """Abstract base class for all ingestion adapters (RSS, Sitemap, API, Crawler)."""

    @abstractmethod
    def fetch(self, source: Source) -> RawFeedResult:
        """Fetch and parse feed items for the given source."""
        pass

    @abstractmethod
    def health(self, source: Source) -> AdapterHealthStatus:
        """Perform a lightweight health probe against the source."""
        pass
