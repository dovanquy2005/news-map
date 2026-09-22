"""Article domain Pydantic schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NormalizedArticleDTO(BaseModel):
    """Clean, sanitized, and normalized article data ready for deduplication and persistence."""

    source_id: UUID
    url: str
    canonical_url: str
    title: str = Field(..., max_length=500)
    summary_raw: Optional[str] = None
    content_excerpt: Optional[str] = Field(None, max_length=2000)
    published_at: datetime
    content_hash: str = Field(..., min_length=64, max_length=64)
    language: str = "vi"
    image_url: Optional[str] = None
    raw_metadata: dict[str, Any] = Field(default_factory=dict)


class ArticleResponse(BaseModel):
    id: UUID
    source_id: UUID
    url: str
    canonical_url: str
    title: str
    content_excerpt: Optional[str] = None
    content_hash: str
    published_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleListResponse(BaseModel):
    data: list[ArticleResponse]
    count: int
