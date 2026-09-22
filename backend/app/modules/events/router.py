"""Public Events API routes conforming to docs/09-api-contracts.md."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.common.db.connection import get_db
from backend.app.modules.events.repository import EventRepository
from backend.app.modules.events.schemas.public import (
    EventDetailDTO,
    PaginatedEventsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/events", tags=["events"])


def get_event_repo(session: Session = Depends(get_db)) -> EventRepository:
    return EventRepository(session)


@router.get("", response_model=PaginatedEventsResponse)
def list_events(
    from_time: Optional[datetime] = Query(None, alias="from"),
    to_time: Optional[datetime] = Query(None, alias="to"),
    province: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    event_status: Optional[str] = Query(None, alias="status"),
    min_sources: int = Query(1, alias="minSources", ge=1),
    min_articles: int = Query(1, alias="minArticles", ge=1),
    bbox: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    repo: EventRepository = Depends(get_event_repo),
) -> PaginatedEventsResponse:
    """List events within spatial bounding box and temporal filters."""
    now = datetime.now(timezone.utc)
    from_dt = from_time or (now - timedelta(hours=24))
    to_dt = to_time or now

    # Server-side security guard: Max 30-day temporal window for public queries
    if (to_dt - from_dt).total_seconds() > 30 * 86400:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "WINDOW_TOO_LARGE",
                    "message": "Maximum date range for events query is 30 days",
                }
            },
        )

    items, meta = repo.list_events(
        bbox=bbox,
        from_time=from_dt,
        to_time=to_dt,
        province=province,
        category=category,
        status=event_status,
        min_sources=min_sources,
        min_articles=min_articles,
        page=page,
        limit=limit,
    )

    return PaginatedEventsResponse(data=items, pagination=meta)


@router.get("/search", response_model=PaginatedEventsResponse)
def search_events(
    q: str = Query(..., min_length=2, max_length=100),
    province: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    from_time: Optional[datetime] = Query(None, alias="from"),
    to_time: Optional[datetime] = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    repo: EventRepository = Depends(get_event_repo),
) -> PaginatedEventsResponse:
    """Full-text search across event titles, summaries, and locations."""
    clean_q = q.strip()
    if len(clean_q) < 2 or len(clean_q) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_QUERY_LENGTH",
                    "message": "Search query must be between 2 and 100 characters",
                }
            },
        )

    items, meta = repo.search_events(
        q=clean_q,
        province=province,
        category=category,
        from_time=from_time,
        to_time=to_time,
        page=page,
        limit=limit,
    )
    return PaginatedEventsResponse(data=items, pagination=meta)


@router.get("/{eventId}", response_model=EventDetailDTO)
def get_event_detail(
    eventId: UUID,
    repo: EventRepository = Depends(get_event_repo),
) -> EventDetailDTO:
    """Retrieve full event detail representation."""
    detail = repo.get_event_detail(eventId)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "EVENT_NOT_FOUND",
                    "message": f"Event with id {eventId} was not found",
                }
            },
        )
    return detail
