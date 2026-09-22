"""Article normalization and sanitization pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import re
import unicodedata
from typing import Optional

from bs4 import BeautifulSoup

from backend.app.modules.articles.schemas import NormalizedArticleDTO
from backend.app.modules.articles.url_cleaner import canonicalize_url
from backend.app.modules.sources.adapters.base import RawArticleDTO

WHITESPACE_REGEX = re.compile(r"\s+")


class ArticleNormalizer:
    """Normalizes URLs, timestamps, sanitizes HTML, and hashes article content."""

    @staticmethod
    def strip_html_tags(raw_html: Optional[str]) -> Optional[str]:
        """Strips HTML markup and returns safe plaintext."""
        if not raw_html:
            return None
        soup = BeautifulSoup(raw_html, "html.parser")
        for tag in soup(["script", "style", "iframe", "noscript"]):
            tag.decompose()
        text = soup.get_text()
        return text

    @staticmethod
    def normalize_text(text: Optional[str]) -> str:
        """Normalizes Unicode (NFC) and collapses excessive whitespace."""
        if not text:
            return ""
        nfc_text = unicodedata.normalize("NFC", text)
        clean = WHITESPACE_REGEX.sub(" ", nfc_text).strip()
        clean = re.sub(r"\s+([,.:;!?])", r"\1", clean)
        return clean

    @staticmethod
    def parse_datetime(date_raw: Optional[str], fallback: Optional[datetime] = None) -> datetime:
        """Parses various date format variants into UTC datetime."""
        if fallback is None:
            fallback = datetime.now(timezone.utc)

        if not date_raw:
            return fallback

        s = date_raw.strip()
        # 1. Try RFC 822 / RFC 2822 (standard RSS dates e.g. Mon, 16 Mar 2026 09:00:00 +0700)
        try:
            dt = parsedate_to_datetime(s)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass

        # 2. Try ISO 8601 (standard Atom dates e.g. 2026-03-16T08:00:00Z)
        try:
            clean_iso = s.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_iso)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass

        return fallback

    @staticmethod
    def compute_content_hash(title: str, excerpt: Optional[str]) -> str:
        """Generates deterministic SHA-256 hash over normalized title and excerpt."""
        text_payload = f"{title} {excerpt or ''}".strip()
        return hashlib.sha256(text_payload.encode("utf-8")).hexdigest()

    def normalize(
        self,
        raw: RawArticleDTO,
        base_url: str = "",
        fetched_at: Optional[datetime] = None,
    ) -> NormalizedArticleDTO:
        """Transforms a RawArticleDTO into a NormalizedArticleDTO."""
        now = fetched_at or datetime.now(timezone.utc)

        # 1. URL Canonicalization
        canonical_url = canonicalize_url(raw.source_url, base_url=base_url)

        # 2. Text sanitization
        clean_title = self.normalize_text(self.strip_html_tags(raw.title))[:500]

        summary_text = self.strip_html_tags(raw.summary_raw)
        clean_excerpt = self.normalize_text(summary_text)[:2000] if summary_text else None

        # 3. Timestamp conversion
        published_at = self.parse_datetime(raw.published_at_raw, fallback=now)

        # 4. Content Hash
        content_hash = self.compute_content_hash(clean_title, clean_excerpt)

        return NormalizedArticleDTO(
            source_id=raw.source_id,
            url=raw.source_url,
            canonical_url=canonical_url,
            title=clean_title,
            summary_raw=raw.summary_raw,
            content_excerpt=clean_excerpt,
            published_at=published_at,
            content_hash=content_hash,
            language="vi",
            image_url=raw.image_url,
            raw_metadata=raw.raw_metadata,
        )
