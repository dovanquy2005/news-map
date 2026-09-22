"""Token counting and AI invocation cost estimator."""

from __future__ import annotations

from dataclasses import dataclass
import math

# Pricing per million tokens (USD)
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gemini-1.5-flash": {"input_per_million": 0.075, "output_per_million": 0.30},
    "gpt-4o-mini": {"input_per_million": 0.15, "output_per_million": 0.60},
    "claude-3-haiku": {"input_per_million": 0.25, "output_per_million": 1.25},
    "mock": {"input_per_million": 0.0, "output_per_million": 0.0},
}


@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float


def estimate_tokens(text: str) -> int:
    """Fast conservative heuristic: ~3-4 characters per token for Vietnamese/English."""
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 3.5))


def calculate_cost(
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> TokenUsage:
    """Computes dollar cost based on model token usage."""
    pricing = MODEL_PRICING.get(model_name.lower(), MODEL_PRICING["gemini-1.5-flash"])
    input_cost = (prompt_tokens / 1_000_000.0) * pricing["input_per_million"]
    output_cost = (completion_tokens / 1_000_000.0) * pricing["output_per_million"]
    total_cost = round(input_cost + output_cost, 6)

    return TokenUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        estimated_cost_usd=total_cost,
    )
