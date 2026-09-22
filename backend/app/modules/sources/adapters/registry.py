"""Source adapter registry resolving adapters by parser type."""

from __future__ import annotations

from typing import Type

from backend.app.modules.sources.adapters.base import BaseSourceAdapter
from backend.app.modules.sources.adapters.rss import RSSFeedAdapter


class AdapterRegistry:
    """Registry maintaining available ingestion adapters."""

    _registry: dict[str, BaseSourceAdapter] = {}

    @classmethod
    def get_adapter(cls, parser_type: str = "RSS") -> BaseSourceAdapter:
        pt = parser_type.upper()
        if pt not in cls._registry:
            if pt in ("RSS", "ATOM", "FEED"):
                cls._registry[pt] = RSSFeedAdapter()
            else:
                raise ValueError(f"No adapter registered for parser type: {parser_type}")
        return cls._registry[pt]

    @classmethod
    def register_adapter(cls, parser_type: str, adapter: BaseSourceAdapter) -> None:
        cls._registry[parser_type.upper()] = adapter
