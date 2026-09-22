"""Router scaffold for admin module."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/health")
def admin_health():
    return {"admin_service": "online"}
