"""Router scaffold for search module."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("")
def search_events(q: str = ""):
    return {"query": q, "results": [], "total": 0}
