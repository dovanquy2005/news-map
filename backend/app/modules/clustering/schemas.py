"""Schemas for event clustering, candidate retrieval, and similarity scoring."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ClusteringDecision(str, Enum):
    """Decision outcomes for clustering evaluation."""

    MERGE = "MERGE"
    CREATE_NEW_EVENT = "CREATE_NEW_EVENT"
    UNCERTAIN = "UNCERTAIN"


class EventCandidateDTO(BaseModel):
    """Structured representation of an existing event candidate for clustering."""

    event_id: UUID
    title: str
    normalized_title: str
    category: str
    status: str
    latitude: float
    longitude: float
    location_label: Optional[str] = None
    location_confidence: float = 1.0
    occurred_at: datetime
    first_reported_at: datetime
    last_updated_at: datetime
    article_count: int = 1
    source_count: int = 1
    confidence_score: float = 0.5
    summary: Optional[str] = None
    distance_meters: Optional[float] = None


class ClusteringSignalBreakdown(BaseModel):
    """Breakdown of individual multi-signal similarity scores."""

    location_similarity: float = Field(..., ge=0.0, le=1.0)
    time_similarity: float = Field(..., ge=0.0, le=1.0)
    semantic_similarity: float = Field(..., ge=0.0, le=1.0)
    entity_overlap: float = Field(..., ge=0.0, le=1.0)
    fact_overlap: float = Field(..., ge=0.0, le=1.0)
    category_match: float = Field(..., ge=0.0, le=1.0)
    composite_score: float = Field(..., ge=0.0, le=1.0)


class ClusteringDecisionDTO(BaseModel):
    """Final clustering decision with provenance rationale."""

    decision: ClusteringDecision
    target_event_id: Optional[UUID] = None
    composite_score: float = Field(..., ge=0.0, le=1.0)
    breakdown: Optional[ClusteringSignalBreakdown] = None
    match_reason: str
