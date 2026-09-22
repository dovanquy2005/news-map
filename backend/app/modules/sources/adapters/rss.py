"""RSS and Atom feed adapter implementation."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

import feedparser

from backend.app.common.db.models.source import Source
from backend.app.common.security.http_client import SafeHttpClient
from backend.app.modules.sources.adapters.base import (
    AdapterHealthStatus,
    BaseSourceAdapter,
    RawArticleDTO,
    RawFeedResult,
)

logger = logging.getLogger(__name__)


class RSSFeedAdapter(BaseSourceAdapter):
    """Parses standard RSS 2.0, Atom 1.0, and Media RSS feeds safely."""

    def __init__(self, http_client: Optional[SafeHttpClient] = None) -> None:
        self.http_client = http_client or SafeHttpClient()

    def parse_xml_content(
        self,
        xml_text_or_bytes: str | bytes,
        source_id: UUID,
    ) -> list[RawArticleDTO]:
        """Parses raw XML string or bytes and returns list of raw article DTOs."""
        # feedparser uses expat/sax with external entity resolution disabled
        parsed = feedparser.parse(xml_text_or_bytes)

        if parsed.bozo and not parsed.entries:
            # Fatal bozo exception where zero entries could be parsed
            logger.warning(
                "Malformed feed for source %s: %s",
                source_id,
                getattr(parsed, "bozo_exception", "Unknown XML error"),
            )
            return []

        articles: list[RawArticleDTO] = []
        for entry in parsed.entries:
            try:
                item = self._extract_entry(entry, source_id)
                if item:
                    articles.append(item)
            except Exception as err:
                # Isolate item failure: do not crash batch
                logger.warning(
                    "Skipping malformed feed entry for source %s: %s",
                    source_id,
                    err,
                )

        return articles

    def _extract_entry(self, entry: Any, source_id: UUID) -> Optional[RawArticleDTO]:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()

        if not title or not link:
            return None

        # Extract summary / description
        summary = entry.get("summary") or entry.get("description")

        # Extract publication timestamp string
        published = entry.get("published") or entry.get("pubDate") or entry.get("updated")

        # Extract author
        author = entry.get("author") or (entry.get("authors")[0].get("name") if entry.get("authors") else None)

        # Extract image URL from media tags or enclosures
        image_url: Optional[str] = None
        if "media_content" in entry and entry.media_content:
            image_url = entry.media_content[0].get("url")
        elif "enclosures" in entry and entry.enclosures:
            for enc in entry.enclosures:
                if enc.get("type", "").startswith("image/"):
                    image_url = enc.get("href")
                    break
        elif "media_thumbnail" in entry and entry.media_thumbnail:
            image_url = entry.media_thumbnail[0].get("url")

        return RawArticleDTO(
            source_id=source_id,
            source_url=link,
            title=title,
            summary_raw=summary,
            published_at_raw=published,
            author_raw=author,
            image_url=image_url,
            raw_metadata={"id": entry.get("id", link)},
        )

    def fetch(self, source: Source) -> RawFeedResult:
        """Fetches feed content via SSRF-safe client and parses into RawFeedResult."""
        if not source.rss_url:
            return RawFeedResult(
                source_id=source.id,
                status_code=400,
                error_message=f"Source '{source.name}' has no configured rss_url",
            )

        now = datetime.now(timezone.utc)
        try:
            resp = self.http_client.fetch(source.rss_url, expected_domain=source.domain)
            items = self.parse_xml_content(resp.content, source.id)

            return RawFeedResult(
                source_id=source.id,
                items=items,
                item_count=len(items),
                status_code=resp.status_code,
                fetched_at=now,
            )
        except Exception as err:
            logger.error("Failed to fetch RSS for %s (%s): %s", source.name, source.domain, err)
            return RawFeedResult(
                source_id=source.id,
                status_code=500,
                error_message=str(err),
                fetched_at=now,
            )

    def health(self, source: Source) -> AdapterHealthStatus:
        """Executes a lightweight fetch to check source endpoint status."""
        start = time.perf_counter()
        if not source.rss_url:
            return AdapterHealthStatus(
                is_healthy=False,
                response_time_ms=0,
                error_message="Missing RSS URL",
            )

        try:
            resp = self.http_client.fetch(source.rss_url, expected_domain=source.domain)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return AdapterHealthStatus(
                is_healthy=resp.status_code == 200,
                response_time_ms=elapsed_ms,
            )
        except Exception as err:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return AdapterHealthStatus(
                is_healthy=False,
                response_time_ms=elapsed_ms,
                error_message=str(err),
            )
