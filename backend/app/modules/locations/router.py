"""Router scaffold for locations module."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/locations", tags=["locations"])


@router.get("")
def list_locations():
    return {"data": [], "pagination": {"limit": 50, "offset": 0, "total": 0}}
