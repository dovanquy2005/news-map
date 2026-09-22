"""Router scaffold for analytics module."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/overview")
def analytics_overview():
    return {"events_count": 0, "articles_count": 0, "active_sources": 0}
