"""Centralized LLM abstraction client for structured news event extraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import logging
from typing import Any, Optional

from backend.app.common.ai.cache import LLMCache
from backend.app.common.ai.cost_tracker import TokenUsage, calculate_cost, estimate_tokens
from backend.app.common.ai.prompts import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


@dataclass
class RawExtractionResult:
    data: dict[str, Any]
    token_usage: TokenUsage
    cached: bool = False
    model_name: str = "mock"


class BaseLLMClient(ABC):
    @abstractmethod
    def generate_json(self, system_prompt: str, user_prompt: str) -> str:
        """Call underlying provider and return raw JSON string."""
        pass


class MockLLMClient(BaseLLMClient):
    """Deterministic mock client for testing and local development."""

    def __init__(self, mock_response: Optional[dict[str, Any]] = None) -> None:
        self.mock_response = mock_response or {
            "is_event": True,
            "title": "Sự kiện thời sự trích xuất",
            "summary": "Tóm tắt sự kiện có cấu trúc",
            "category": "INFRASTRUCTURE",
            "location_name": "Hà Nội",
            "admin_level_1": "Hà Nội",
            "admin_level_2": "Ba Đình",
            "confidence_score": 0.95,
            "key_facts": ["Khởi công công trình", "Dự kiến hoàn thành 2028"],
        }

    def generate_json(self, system_prompt: str, user_prompt: str) -> str:
        return json.dumps(self.mock_response)


class LLMClient:
    """Production LLM wrapper handling caching, token tracking, and structured parsing."""

    def __init__(
        self,
        provider: Optional[BaseLLMClient] = None,
        model_name: str = "mock",
        cache: Optional[LLMCache] = None,
    ) -> None:
        self.provider = provider or MockLLMClient()
        self.model_name = model_name
        self.cache = cache or LLMCache()

    def extract_event_structured(
        self,
        title: str,
        content: str,
        content_hash: str,
    ) -> RawExtractionResult:
        """Extracts structured event representation with cache lookups and token accounting."""

        # 1. Check cache first
        cached_result = self.cache.get(self.model_name, PROMPT_VERSION, content_hash)
        if cached_result:
            usage = TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                estimated_cost_usd=0.0,
            )
            return RawExtractionResult(
                data=cached_result,
                token_usage=usage,
                cached=True,
                model_name=self.model_name,
            )

        # 2. Build safe fenced user prompt
        user_prompt = build_user_prompt(title, content)

        # 3. Call LLM provider
        raw_output = self.provider.generate_json(SYSTEM_PROMPT, user_prompt)

        # 4. Parse JSON
        try:
            parsed_data = json.loads(raw_output)
        except json.JSONDecodeError as err:
            logger.error("LLM failed to output valid JSON: %s", err)
            parsed_data = {"is_event": False, "error": "Invalid JSON response"}

        # 5. Token and cost estimation
        prompt_tokens = estimate_tokens(SYSTEM_PROMPT + user_prompt)
        completion_tokens = estimate_tokens(raw_output)
        token_usage = calculate_cost(self.model_name, prompt_tokens, completion_tokens)

        # 6. Store in cache
        if parsed_data.get("is_event"):
            self.cache.set(self.model_name, PROMPT_VERSION, content_hash, parsed_data)

        return RawExtractionResult(
            data=parsed_data,
            token_usage=token_usage,
            cached=False,
            model_name=self.model_name,
        )
