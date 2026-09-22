"""Article domain service."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.common.db.models.article import Article
from backend.app.modules.articles.repository import ArticleRepository
from backend.app.modules.articles.schemas import NormalizedArticleDTO


class ArticleService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = ArticleRepository(session)

    def get_article_by_id(self, article_id: UUID) -> Optional[Article]:
        return self.repo.get_by_id(article_id)

    def list_articles(self, limit: int = 50, offset: int = 0) -> list[Article]:
        return self.repo.list_all(limit=limit, offset=offset)

    def save_unique_articles(
        self,
        dtos: list[NormalizedArticleDTO],
    ) -> list[Article]:
        return self.repo.save_unique_articles(dtos)
