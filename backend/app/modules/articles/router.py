"""Router scaffold for articles module."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/articles", tags=["articles"])


@router.get("")
def list_articles():
    return {"data": [], "pagination": {"limit": 50, "offset": 0, "total": 0}}
