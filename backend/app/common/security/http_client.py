"""SSRF-Safe HTTP client for feed crawling and external article fetching."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx

from backend.app.common.security.ip_validator import (
    SSRFValidationError,
    resolve_and_validate_hostname,
)

logger = logging.getLogger(__name__)

USER_AGENT = "VietnamNewsMapBot/1.0 (+https://vietnamnewsmap.vn/bot)"
MAX_RESPONSE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
MAX_REDIRECTS = 3
CONNECT_TIMEOUT = 5.0
READ_TIMEOUT = 15.0


@dataclass
class SafeFetchResponse:
    status_code: int
    content: bytes
    text: str
    headers: dict[str, str]
    final_url: str


class SafeHttpClient:
    """Centralized HTTP fetch client defending against SSRF and resource exhaustion."""

    def __init__(
        self,
        allow_http_for_dev: bool = False,
        timeout: float = READ_TIMEOUT,
    ) -> None:
        self.allow_http_for_dev = allow_http_for_dev
        self.timeout = timeout

    def _validate_url_and_domain(
        self,
        target_url: str,
        expected_domain: Optional[str] = None,
    ) -> tuple[str, str]:
        """Validates scheme, domain, and pre-request IP resolution."""
        parsed = urlparse(target_url)

        # 1. Check scheme
        if parsed.scheme != "https":
            if not (self.allow_http_for_dev and parsed.scheme == "http"):
                raise SSRFValidationError(
                    f"Insecure scheme '{parsed.scheme}': only HTTPS is allowed"
                )

        # 2. Check host presence
        hostname = parsed.hostname
        if not hostname:
            raise SSRFValidationError(f"Invalid URL: missing host in '{target_url}'")

        # 3. Domain allowlist check
        if expected_domain:
            expected_clean = expected_domain.strip().lower()
            host_clean = hostname.strip().lower()
            if host_clean != expected_clean and not host_clean.endswith(f".{expected_clean}"):
                raise SSRFValidationError(
                    f"Domain mismatch: host '{host_clean}' is not part of expected domain '{expected_clean}'"
                )

        # 4. Resolve and validate IP address
        resolve_and_validate_hostname(hostname)

        return parsed.scheme, hostname

    def fetch(
        self,
        url: str,
        expected_domain: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> SafeFetchResponse:
        """Performs SSRF-safe synchronous fetch with redirect and size limits."""
        req_headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, text/xml, application/xml, text/html",
        }
        if headers:
            req_headers.update(headers)

        current_url = url
        redirect_count = 0

        with httpx.Client(
            timeout=httpx.Timeout(self.timeout, connect=CONNECT_TIMEOUT),
            follow_redirects=False,
            verify=True,
        ) as client:
            while True:
                self._validate_url_and_domain(current_url, expected_domain)

                response = client.get(current_url, headers=req_headers)

                # Handle redirects manually to re-verify host and destination IP on every hop
                if response.is_redirect:
                    redirect_count += 1
                    if redirect_count > MAX_REDIRECTS:
                        raise SSRFValidationError(
                            f"Exceeded maximum allowed redirects ({MAX_REDIRECTS})"
                        )

                    location = response.headers.get("Location")
                    if not location:
                        raise SSRFValidationError("Redirect response missing Location header")

                    # Resolve relative redirect URLs
                    current_url = urljoin(current_url, location)
                    logger.info("Following safe redirect hop %d to: %s", redirect_count, current_url)
                    continue

                # Stream and check response size limit
                content_chunks: list[bytes] = []
                total_bytes = 0
                for chunk in response.iter_bytes():
                    total_bytes += len(chunk)
                    if total_bytes > MAX_RESPONSE_SIZE_BYTES:
                        raise SSRFValidationError(
                            f"Response payload exceeds maximum allowed limit of {MAX_RESPONSE_SIZE_BYTES} bytes"
                        )
                    content_chunks.append(chunk)

                raw_bytes = b"".join(content_chunks)
                text = raw_bytes.decode(response.encoding or "utf-8", errors="replace")

                return SafeFetchResponse(
                    status_code=response.status_code,
                    content=raw_bytes,
                    text=text,
                    headers=dict(response.headers),
                    final_url=str(response.url),
                )
