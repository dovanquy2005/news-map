"""Article repository providing persistence and query operations."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.app.common.db.models.article import Article
from backend.app.common.db.repositories.base import BaseRepository
from backend.app.modules.articles.schemas import NormalizedArticleDTO


class ArticleRepository(BaseRepository[Article]):
    def __init__(self, session: Session) -> None:
        super().__init__(Article, session)

    def get_by_canonical_url(self, canonical_url: str) -> Optional[Article]:
        stmt = select(Article).where(Article.canonical_url == canonical_url)
        return self.session.scalars(stmt).first()

    def get_by_content_hash(self, content_hash: str) -> Optional[Article]:
        stmt = select(Article).where(Article.content_hash == content_hash)
        return self.session.scalars(stmt).first()

    def save_unique_articles(
        self,
        dtos: list[NormalizedArticleDTO],
    ) -> list[Article]:
        """Saves unique articles and returns the list of newly created Article entities."""
        if not dtos:
            return []

        created_articles: list[Article] = []
        for dto in dtos:
            # Check if canonical_url already exists
            existing = self.get_by_canonical_url(dto.canonical_url)
            if existing:
                continue

            article = Article(
                source_id=dto.source_id,
                url=dto.url,
                canonical_url=dto.canonical_url,
                title=dto.title,
                content_excerpt=dto.content_excerpt,
                content_hash=dto.content_hash,
                published_at=dto.published_at,
            )
            self.session.add(article)
            created_articles.append(article)

        if created_articles:
            self.session.commit()
            for art in created_articles:
                self.session.refresh(art)

        return created_articles
