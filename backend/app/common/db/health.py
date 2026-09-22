"""Database health check and diagnostic probes.

Strictly complies with:
- docs/04-data-architecture.md (Geospatial PostGIS requirement)
- docs/11-performance-scalability.md (Health check latency < 50ms)
- tasks/TASK-003-database-foundation.md
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Engine, text

from backend.app.common.db.connection import get_db_engine


@dataclass(frozen=True)
class DatabaseHealthReport:
    """Diagnostic outcome for database liveness and readiness probes."""

    is_healthy: bool
    latency_ms: float
    postgis_version: Optional[str] = None
    pgvector_version: Optional[str] = None
    error_message: Optional[str] = None


def check_db_health(engine: Engine | None = None) -> DatabaseHealthReport:
    """Execute diagnostic queries to verify database connectivity, responsiveness, and extension presence."""
    target_engine = engine or get_db_engine()
    start_time = time.perf_counter()
    try:
        with target_engine.connect() as conn:
            query_start = time.perf_counter()

            # 1. Liveness ping (SELECT 1)
            conn.execute(text("SELECT 1"))

            # 2. PostGIS presence check
            postgis_ver = None
            try:
                result = conn.execute(text("SELECT PostGIS_Version()")).scalar()
                if result:
                    postgis_ver = str(result).strip()
            except Exception:
                postgis_ver = None

            # 3. pgvector presence check
            pgvector_ver = None
            try:
                v_res = conn.execute(
                    text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
                ).scalar()
                if v_res:
                    pgvector_ver = str(v_res).strip()
            except Exception:
                pgvector_ver = None

            latency_ms = (time.perf_counter() - query_start) * 1000.0

        # Health is considered true if basic connection works and PostGIS is present
        is_healthy = postgis_ver is not None

        return DatabaseHealthReport(
            is_healthy=is_healthy,
            latency_ms=round(latency_ms, 2),
            postgis_version=postgis_ver,
            pgvector_version=pgvector_ver,
            error_message=None if is_healthy else "PostGIS extension not found or inactive",
        )

    except Exception as exc:
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        # Sanitize error message to avoid credential leakage
        raw_msg = str(exc)
        safe_msg = raw_msg.split("@")[-1] if "@" in raw_msg else raw_msg
        return DatabaseHealthReport(
            is_healthy=False,
            latency_ms=round(latency_ms, 2),
            postgis_version=None,
            pgvector_version=None,
            error_message=f"Database connection failed: {safe_msg[:120]}",
        )
