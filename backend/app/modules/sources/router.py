"""Router for sources module according to API contract."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.common.db.connection import get_db
from backend.app.modules.sources.schemas import (
    SourceCreateRequest,
    SourceListResponse,
    SourceResponse,
    SourceToggleRequest,
    SourceUpdateRequest,
)
from backend.app.modules.sources.service import SourceService

router = APIRouter(prefix="/api/v1/sources", tags=["sources"])


def get_source_service(session: Session = Depends(get_db)) -> SourceService:
    return SourceService(session)


@router.get("", response_model=SourceListResponse)
def list_sources(
    active_only: bool = Query(default=True, description="Filter only active sources"),
    service: SourceService = Depends(get_source_service),
) -> SourceListResponse:
    """Retrieve news publisher sources."""
    if active_only:
        sources = service.get_active_sources()
    else:
        sources = service.get_all_sources()

    items = [SourceResponse.model_validate(s) for s in sources]
    return SourceListResponse(data=items, count=len(items))


@router.get("/{source_id}", response_model=SourceResponse)
def get_source_detail(
    source_id: UUID,
    service: SourceService = Depends(get_source_service),
) -> SourceResponse:
    """Retrieve a single source by UUID."""
    source = service.get_source_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with id '{source_id}' was not found.",
        )
    return SourceResponse.model_validate(source)


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(
    payload: SourceCreateRequest,
    service: SourceService = Depends(get_source_service),
) -> SourceResponse:
    """Register a new news publisher source."""
    try:
        source = service.register_source(payload)
        return SourceResponse.model_validate(source)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err),
        )


@router.patch("/{source_id}", response_model=SourceResponse)
def update_source(
    source_id: UUID,
    payload: SourceUpdateRequest,
    service: SourceService = Depends(get_source_service),
) -> SourceResponse:
    """Update news source configuration."""
    try:
        source = service.update_source(source_id, payload)
        return SourceResponse.model_validate(source)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        )


@router.patch("/{source_id}/toggle", response_model=SourceResponse)
def toggle_source(
    source_id: UUID,
    payload: SourceToggleRequest,
    service: SourceService = Depends(get_source_service),
) -> SourceResponse:
    """Toggle source active status (immediately pauses/resumes crawls)."""
    try:
        source = service.toggle_source_status(source_id, payload.active)
        return SourceResponse.model_validate(source)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        )
