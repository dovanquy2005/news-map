"""LLM response caching layer backed by Redis."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from backend.app.common.cache.redis import get_redis_client

logger = logging.getLogger(__name__)

LLM_CACHE_TTL_SECONDS = 7 * 86400  # 7 days


class LLMCache:
    """Caches LLM structured JSON responses keyed by model, prompt version, and content hash."""

    def __init__(self) -> None:
        self.client = get_redis_client()

    def _build_key(self, model_name: str, prompt_version: str, content_hash: str) -> str:
        return f"vnm:cache:llm:{model_name}:{prompt_version}:{content_hash}"

    def get(
        self,
        model_name: str,
        prompt_version: str,
        content_hash: str,
    ) -> Optional[dict[str, Any]]:
        """Retrieve previously cached response if present."""
        key = self._build_key(model_name, prompt_version, content_hash)
        try:
            cached_val = self.client.get(key)
            if cached_val:
                logger.info("LLM cache HIT for key %s", key)
                return json.loads(cached_val)
        except Exception as err:
            logger.warning("Error reading from LLM cache: %s", err)
        return None

    def set(
        self,
        model_name: str,
        prompt_version: str,
        content_hash: str,
        response_data: dict[str, Any],
        ttl_seconds: int = LLM_CACHE_TTL_SECONDS,
    ) -> None:
        """Store LLM structured output with expiration."""
        key = self._build_key(model_name, prompt_version, content_hash)
        try:
            self.client.set(key, json.dumps(response_data), ex=ttl_seconds)
            logger.debug("LLM cache SET for key %s", key)
        except Exception as err:
            logger.warning("Error writing to LLM cache: %s", err)
