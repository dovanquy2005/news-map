"""Extraction service coordinating article retrieval, LLM prompt, and validation."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.common.ai.client import LLMClient
from backend.app.common.db.models.article import Article
from backend.app.modules.articles.repository import ArticleRepository
from backend.app.modules.events.schemas.extraction import ValidatedExtractionDTO
from backend.app.modules.events.validators.extraction_validator import ExtractionValidator

logger = logging.getLogger(__name__)


class ExtractionService:
    def __init__(
        self,
        session: Session,
        llm_client: Optional[LLMClient] = None,
        validator: Optional[ExtractionValidator] = None,
    ) -> None:
        self.session = session
        self.article_repo = ArticleRepository(session)
        self.llm_client = llm_client or LLMClient()
        self.validator = validator or ExtractionValidator()

    def process_article(self, article_id: UUID) -> Optional[ValidatedExtractionDTO]:
        """Retrieves article, extracts structured event via LLM, and validates output."""
        article = self.article_repo.get_by_id(article_id)
        if not article:
            raise ValueError(f"Article '{article_id}' not found in database")

        content = article.content_excerpt or article.summary_raw or ""

        # 1. Call LLM extraction
        raw_res = self.llm_client.extract_event_structured(
            title=article.title,
            content=content,
            content_hash=article.content_hash,
        )

        # 2. Validate extracted JSON against schema & domain rules
        validated_dto = self.validator.validate_extraction(
            raw_res.data,
            reference_time=article.published_at,
        )

        # 3. Store intermediate extraction in article metadata
        metadata = dict(article.raw_metadata or {})
        metadata["extraction"] = validated_dto.model_dump(mode="json")
        article.raw_metadata = metadata
        self.session.commit()
        self.session.refresh(article)

        logger.info(
            "Extracted and validated event for article %s: '%s' (category=%s, confidence=%.2f)",
            article_id,
            validated_dto.event_title,
            validated_dto.event_type.value,
            validated_dto.extraction_confidence,
        )

        return validated_dto
