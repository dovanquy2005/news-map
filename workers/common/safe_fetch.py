"""Worker-facing safe fetch utility module."""

from __future__ import annotations

from typing import Optional

from backend.app.common.security.http_client import SafeFetchResponse, SafeHttpClient


def safe_fetch(
    url: str,
    source_domain: Optional[str] = None,
    headers: Optional[dict[str, str]] = None,
    allow_http_for_dev: bool = False,
) -> SafeFetchResponse:
    """Convenience helper for workers to perform SSRF-safe feed and article fetching."""
    client = SafeHttpClient(allow_http_for_dev=allow_http_for_dev)
    return client.fetch(url, expected_domain=source_domain, headers=headers)
