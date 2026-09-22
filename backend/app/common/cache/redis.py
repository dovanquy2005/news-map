"""Redis client connection pool, health diagnostics, and caching abstractions.

Strictly complies with:
- docs/02-system-architecture.md (Redis Cache + Queue)
- docs/10-security.md (Key namespacing, No secret serialization)
- tasks/TASK-005-redis-queue-foundation.md
"""

from __future__ import annotations

import json
import time
from typing import Any, Optional, Tuple

import redis
from redis.connection import ConnectionPool

from backend.app.common.config import get_settings

_REDIS_POOL: Optional[ConnectionPool] = None
_REDIS_CLIENT: Optional[redis.Redis] = None

CACHE_PREFIX = "vnm:cache:"


def get_redis_client() -> redis.Redis:
    """Create or return cached Redis client instance with connection pooling."""
    global _REDIS_POOL, _REDIS_CLIENT
    if _REDIS_CLIENT is not None:
        return _REDIS_CLIENT

    settings = get_settings()
    redis_url = settings.redis_url.get_secret_value()

    _REDIS_POOL = ConnectionPool.from_url(
        redis_url,
        max_connections=settings.redis_max_connections,
        decode_responses=True,
        socket_timeout=5.0,
        socket_connect_timeout=5.0,
        health_check_interval=30,
    )
    _REDIS_CLIENT = redis.Redis(connection_pool=_REDIS_POOL)
    return _REDIS_CLIENT


def check_redis_health() -> Tuple[bool, float, Optional[str]]:
    """Probe Redis responsiveness using PING.

    Returns:
        (is_healthy, latency_ms, error_message)
    """
    client = get_redis_client()
    start = time.perf_counter()
    try:
        pong = client.ping()
        latency_ms = (time.perf_counter() - start) * 1000.0
        return (bool(pong), round(latency_ms, 2), None)
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000.0
        return (False, round(latency_ms, 2), f"Redis connection failed: {str(exc)[:100]}")


def reset_redis_client() -> None:
    """Reset and close the cached Redis client and pool (useful for testing)."""
    global _REDIS_POOL, _REDIS_CLIENT
    if _REDIS_CLIENT is not None:
        _REDIS_CLIENT.close()
        _REDIS_CLIENT = None
    if _REDIS_POOL is not None:
        _REDIS_POOL.disconnect()
        _REDIS_POOL = None


class CacheService:
    """Namespaced caching operations with automatic serialization."""

    def __init__(self, client: Optional[redis.Redis] = None, prefix: str = CACHE_PREFIX):
        self.client = client or get_redis_client()
        self.prefix = prefix

    def _format_key(self, key: str) -> str:
        return f"{self.prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Fetch value from cache, automatically parsing JSON objects/arrays."""
        raw_val = self.client.get(self._format_key(key))
        if raw_val is None:
            return None
        trimmed = str(raw_val).strip()
        if (trimmed.startswith("{") and trimmed.endswith("}")) or (
            trimmed.startswith("[") and trimmed.endswith("]")
        ):
            try:
                return json.loads(trimmed)
            except Exception:
                return raw_val
        return raw_val

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Store value in cache with optional TTL. Serializes non-strings to JSON."""
        serialized = value if isinstance(value, str) else json.dumps(value)
        formatted_key = self._format_key(key)
        if ttl_seconds and ttl_seconds > 0:
            return bool(self.client.set(formatted_key, serialized, ex=ttl_seconds))
        return bool(self.client.set(formatted_key, serialized))

    def delete(self, key: str) -> bool:
        """Remove a key from cache."""
        return bool(self.client.delete(self._format_key(key)))

    def delete_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a wildcard pattern."""
        full_pattern = f"{self.prefix}{pattern}"
        matched_keys = self.client.keys(full_pattern)
        if not matched_keys:
            return 0
        return int(self.client.delete(*matched_keys))

    def exists(self, key: str) -> bool:
        """Check if a cache key exists."""
        return bool(self.client.exists(self._format_key(key)))
