"""Public API response schemas for events conforming to docs/09-api-contracts.md."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class EventListItemDTO(BaseModel):
    """Event card item in public map list and viewport responses."""

    id: UUID
    title: str
    category: str
    status: str
    latitude: float
    longitude: float
    location_label: Optional[str] = None
    location_confidence: float = 1.0
    occurred_at: datetime
    first_reported_at: datetime
    last_updated_at: datetime
    article_count: int
    source_count: int
    confidence_score: float
    summary: Optional[str] = None


class LocationPublicDTO(BaseModel):
    latitude: float
    longitude: float
    label: Optional[str] = None
    confidence: float
    is_approximate: bool = False


class ConfidencePublicDTO(BaseModel):
    score: int
    level: str
    factors: Dict[str, float] = Field(default_factory=dict)
    positive_indicators: List[str] = Field(default_factory=list)
    warning_indicators: List[str] = Field(default_factory=list)


class SourcePublicDTO(BaseModel):
    source_name: str
    article_title: str
    original_url: str
    published_at: datetime
    source_type: str = "MAJOR_NEWS"


class TimelinePublicDTO(BaseModel):
    timestamp: datetime
    type: str
    text: str
    source_article_id: Optional[UUID] = None


class FactPublicDTO(BaseModel):
    key: str
    value: str
    confidence: float
    supporting_articles: int = 1


class RelatedEventPublicDTO(BaseModel):
    id: UUID
    title: str
    category: str
    occurred_at: datetime
    distance_meters: Optional[float] = None


class EventDetailDTO(BaseModel):
    """Complete detail view schema for a single event."""

    id: UUID
    title: str
    category: str
    status: str
    summary: Optional[str] = None
    location: LocationPublicDTO
    occurred_at: datetime
    first_reported_at: datetime
    last_updated_at: datetime
    article_count: int
    source_count: int
    confidence: ConfidencePublicDTO
    sources: List[SourcePublicDTO] = Field(default_factory=list)
    timeline: List[TimelinePublicDTO] = Field(default_factory=list)
    facts: List[FactPublicDTO] = Field(default_factory=list)
    related_events: List[RelatedEventPublicDTO] = Field(default_factory=list)


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class PaginatedEventsResponse(BaseModel):
    data: List[EventListItemDTO]
    pagination: PaginationMeta
