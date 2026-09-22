"""Unit tests for LLM abstraction client, token tracking, and response caching."""

import unittest
from uuid import uuid4

from backend.app.common.ai.client import LLMClient, MockLLMClient
from backend.app.common.ai.cost_tracker import calculate_cost, estimate_tokens
from backend.app.common.ai.prompts import build_user_prompt


class InMemoryCache:
    def __init__(self) -> None:
        self.store = {}

    def get(self, model_name: str, prompt_version: str, content_hash: str):
        return self.store.get((model_name, prompt_version, content_hash))

    def set(self, model_name: str, prompt_version: str, content_hash: str, response_data, ttl_seconds: int = 0):
        self.store[(model_name, prompt_version, content_hash)] = response_data


class TestLLMClientUnit(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_client = MockLLMClient()
        self.mock_cache = InMemoryCache()
        self.client = LLMClient(provider=self.mock_client, model_name="mock", cache=self.mock_cache)
        self.content_hash = f"test_hash_{uuid4().hex}"

    def test_structured_event_extraction(self) -> None:
        result = self.client.extract_event_structured(
            title="Khởi công dự án cầu Thủ Thiêm",
            content="Dự án cầu Thủ Thiêm nối Quận 7 và Thủ Đức được khởi công sáng nay.",
            content_hash=self.content_hash,
        )
        self.assertFalse(result.cached)
        self.assertTrue(result.data["is_event"])
        self.assertEqual(result.data["category"], "INFRASTRUCTURE")
        self.assertGreater(result.token_usage.total_tokens, 0)

    def test_response_caching_on_second_call(self) -> None:
        # First call: populates cache
        res1 = self.client.extract_event_structured("Title", "Content", self.content_hash)
        self.assertFalse(res1.cached)

        # Second call with same hash: hits cache
        res2 = self.client.extract_event_structured("Title", "Content", self.content_hash)
        self.assertTrue(res2.cached)
        self.assertEqual(res2.token_usage.total_tokens, 0)
        self.assertEqual(res2.token_usage.estimated_cost_usd, 0.0)

    def test_token_and_cost_estimation(self) -> None:
        text = "Một hai ba bốn năm sáu bảy tám chín mười"
        tokens = estimate_tokens(text)
        self.assertGreater(tokens, 0)

        usage = calculate_cost("gemini-1.5-flash", prompt_tokens=1000, completion_tokens=200)
        self.assertEqual(usage.total_tokens, 1200)
        self.assertGreater(usage.estimated_cost_usd, 0.0)

    def test_content_truncation_boundary(self) -> None:
        long_content = "A" * 5000
        prompt = build_user_prompt("Short Title", long_content)
        # Verify content was bounded to max 2000 chars
        self.assertLess(len(prompt), 3000)


if __name__ == "__main__":
    unittest.main()
