"""Multi-tier article deduplication engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.common.db.models.article import Article
from backend.app.modules.articles.schemas import NormalizedArticleDTO
from backend.app.modules.articles.similarity import compute_title_similarity

TITLE_SIMILARITY_THRESHOLD = 0.90
TIME_WINDOW_HOURS = 24


class DedupLevel(str, Enum):
    EXACT_URL = "EXACT_URL"
    CONTENT_HASH = "CONTENT_HASH"
    TITLE_TIME_HEURISTIC = "TITLE_TIME_HEURISTIC"


@dataclass
class DedupDecision:
    is_duplicate: bool
    matched_article_id: Optional[UUID] = None
    dedup_level: Optional[DedupLevel] = None
    confidence: float = 0.0


class ArticleDeduplicator:
    """Evaluates incoming normalized articles against existing database entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def evaluate_article(self, article: NormalizedArticleDTO) -> DedupDecision:
        """Evaluates whether an article is a duplicate through the 3-level hierarchy."""

        # 1. Level 1 — Exact Canonical URL
        stmt_url = select(Article.id).where(Article.canonical_url == article.canonical_url)
        match_url_id = self.session.scalars(stmt_url).first()
        if match_url_id:
            return DedupDecision(
                is_duplicate=True,
                matched_article_id=match_url_id,
                dedup_level=DedupLevel.EXACT_URL,
                confidence=1.0,
            )

        # 2. Level 2 — Content Hash
        stmt_hash = select(Article.id).where(Article.content_hash == article.content_hash)
        match_hash_id = self.session.scalars(stmt_hash).first()
        if match_hash_id:
            return DedupDecision(
                is_duplicate=True,
                matched_article_id=match_hash_id,
                dedup_level=DedupLevel.CONTENT_HASH,
                confidence=1.0,
            )

        # 3. Level 3 — Title & Time Proximity Heuristic (same source within 24h)
        window_start = article.published_at - timedelta(hours=TIME_WINDOW_HOURS)
        window_end = article.published_at + timedelta(hours=TIME_WINDOW_HOURS)

        stmt_candidates = (
            select(Article.id, Article.title)
            .where(
                Article.source_id == article.source_id,
                Article.published_at >= window_start,
                Article.published_at <= window_end,
            )
            .limit(50)
        )
        candidates = self.session.execute(stmt_candidates).all()

        for cand_id, cand_title in candidates:
            sim = compute_title_similarity(cand_title, article.title)
            if sim >= TITLE_SIMILARITY_THRESHOLD:
                return DedupDecision(
                    is_duplicate=True,
                    matched_article_id=cand_id,
                    dedup_level=DedupLevel.TITLE_TIME_HEURISTIC,
                    confidence=sim,
                )

        # No duplicate detected
        return DedupDecision(
            is_duplicate=False,
            matched_article_id=None,
            dedup_level=None,
            confidence=0.0,
        )
