"""Event summary generator invoking LLM with strict fact-groundedness."""

from __future__ import annotations

import logging
from typing import List, Optional

from backend.app.common.ai.client import BaseLLMClient, MockLLMClient
from backend.app.common.ai.prompts import (
    EVENT_SUMMARY_SYSTEM_INSTRUCTION,
    build_summary_prompt,
)
from backend.app.common.config import load_settings

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """Generates fact-grounded summaries preserving uncertainties."""

    def __init__(self, llm_client: Optional[BaseLLMClient] = None) -> None:
        self._client = llm_client or MockLLMClient()

    def generate(
        self,
        event_title: str,
        category: str,
        location_label: str,
        facts: List[str],
        timeline_items: List[str],
        source_names: List[str],
    ) -> str:
        """Generate concise summary using LLM or structured template fallback."""
        prompt = build_summary_prompt(
            event_title=event_title,
            category=category,
            location_label=location_label,
            facts=facts,
            timeline_items=timeline_items,
            source_names=source_names,
        )

        try:
            # If using mock client in tests, format template
            if isinstance(self._client, MockLLMClient):
                return self._fallback_summary(
                    event_title, category, location_label, facts, source_names
                )

            res = self._client.generate(
                prompt=prompt,
                system_instruction=EVENT_SUMMARY_SYSTEM_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=300,
            )
            cleaned = res.text.strip()
            # Simple word count sanity check (between 20 and 200 words)
            word_count = len(cleaned.split())
            if 20 <= word_count <= 250:
                return cleaned

        except Exception as e:
            logger.warning("LLM summary generation failed: %s. Using template fallback.", e)

        return self._fallback_summary(
            event_title, category, location_label, facts, source_names
        )

    def _fallback_summary(
        self,
        event_title: str,
        category: str,
        location_label: str,
        facts: List[str],
        source_names: List[str],
    ) -> str:
        sources_text = (
            f"Theo ghi nhận từ {len(source_names)} nguồn báo chí ({', '.join(source_names[:3])})"
            if source_names
            else "Theo các nguồn tin ban đầu"
        )
        facts_summary = f". Một số thông tin chính: {'; '.join(facts[:3])}" if facts else ""
        return (
            f"{sources_text}, sự việc '{event_title}' xảy ra tại khu vực {location_label}{facts_summary}. "
            f"Các lực lượng chức năng đang tiếp tục cập nhật tình hình."
        )
