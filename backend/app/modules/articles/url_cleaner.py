"""URL canonicalization and tracking parameter cleaner."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

# Query parameters commonly used for marketing, analytics, and click tracking
TRACKING_QUERY_PARAMS = frozenset(
    {
        "ref",
        "fbclid",
        "gclid",
        "dclid",
        "msclkid",
        "source",
        "campaign",
        "medium",
        "term",
        "content",
        "src",
        "spref",
        "mc_cid",
        "mc_eid",
        "_ga",
        "_gl",
        "igshid",
        "ns_mchannel",
        "ns_source",
    }
)


def canonicalize_url(url: str, base_url: str = "") -> str:
    """Cleans, strips tracking parameters, and canonicalizes article URLs."""
    if not url:
        return ""

    raw_url = url.strip()
    if base_url:
        raw_url = urljoin(base_url, raw_url)

    parsed = urlparse(raw_url)

    # Force lowercase https scheme and lowercase domain
    scheme = "https" if parsed.scheme in ("http", "https") else parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Normalize port (remove 80 for http, 443 for https)
    if netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]
    elif netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]

    # Filter query parameters: remove utm_* and tracking params
    filtered_query: list[tuple[str, str]] = []
    if parsed.query:
        for k, v in parse_qsl(parsed.query, keep_blank_values=False):
            k_lower = k.lower()
            if k_lower.startswith("utm_"):
                continue
            if k_lower in TRACKING_QUERY_PARAMS:
                continue
            filtered_query.append((k, v))

    # Sort query parameters for canonical determinism
    filtered_query.sort(key=lambda x: x[0])
    query_str = urlencode(filtered_query)

    # Path normalization: strip trailing slash unless root path
    path = parsed.path
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    # Discard fragment entirely (#...)
    clean_parts = (scheme, netloc, path, parsed.params, query_str, "")
    return urlunparse(clean_parts)
