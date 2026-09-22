"""Router scaffold for clustering module."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/clustering", tags=["clustering"])


@router.get("/status")
def clustering_status():
    return {"status": "idle", "active_jobs": 0}
