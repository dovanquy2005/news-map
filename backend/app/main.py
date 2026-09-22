"""FastAPI Backend Application Factory and Modular Monolith Runtime.

Strictly complies with:
- docs/02-system-architecture.md (Trust boundaries, Modular monolith)
- docs/03-backend-architecture.md (Style, Layering, Error handling)
- docs/09-api-contracts.md (Base /api/v1, Standard error envelope)
- docs/10-security.md (CORS, Request validation, Security headers)
- tasks/TASK-006-backend-modular-monolith-foundation.md
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse

from backend.app.common.cache import check_redis_health
from backend.app.common.config import get_settings
from backend.app.common.db import check_db_health
from backend.app.common.logging import setup_structured_logging
from backend.app.common.metrics import get_metrics
from backend.app.modules.admin.router import router as admin_router
from backend.app.modules.analytics.router import router as analytics_router
from backend.app.modules.articles.router import router as articles_router
from backend.app.modules.clustering.router import router as clustering_router
from backend.app.modules.events.router import router as events_router
from backend.app.modules.locations.router import router as locations_router
from backend.app.modules.search.router import router as search_router
from backend.app.modules.sources.router import router as sources_router

logger = logging.getLogger("news_map.api")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Assigns or propagates X-Request-ID across the request context and response."""

    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response


def create_error_response(
    status_code: int,
    code: str,
    message: str,
    details: Dict[str, Any] | None = None,
    headers: Dict[str, str] | None = None,
) -> JSONResponse:
    """Build standardized JSON error response adhering to docs/09-api-contracts.md."""
    envelope = {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }
    return JSONResponse(status_code=status_code, content=envelope, headers=headers)


def create_app() -> FastAPI:
    """Application factory for Vietnam News Map backend."""
    settings = get_settings()

    app = FastAPI(
        title="Vietnam News Map API",
        version="0.1.0",
        description="Public and operational backend API for the Vietnam News Map platform.",
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url="/redoc" if settings.app_env != "production" else None,
    )

    # 1. Register Middlewares
    app.add_middleware(CorrelationIdMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Register Exception Handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message="Invalid request parameters or payload",
            details={"errors": [str(err) for err in exc.errors()]},
        )

    from starlette.exceptions import HTTPException as StarletteHTTPException

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            429: "RATE_LIMIT_EXCEEDED",
        }
        err_code = code_map.get(exc.status_code, "HTTP_ERROR")
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            err_dict = exc.detail["error"]
            return create_error_response(
                status_code=exc.status_code,
                code=err_dict.get("code", err_code),
                message=err_dict.get("message", "HTTP Error"),
                details=err_dict.get("details", {}),
                headers=exc.headers,
            )
        elif isinstance(exc.detail, dict) and "code" in exc.detail:
            return create_error_response(
                status_code=exc.status_code,
                code=exc.detail.get("code", err_code),
                message=exc.detail.get("message", "HTTP Error"),
                details=exc.detail.get("details", {}),
                headers=exc.headers,
            )
        return create_error_response(
            status_code=exc.status_code,
            code=err_code,
            message=str(exc.detail),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def global_unhandled_exception_handler(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", "unknown")
        logger.error("Unhandled exception [req_id=%s]: %s", req_id, exc, exc_info=True)

        if settings.app_env == "production":
            safe_message = "An internal server error occurred. Please contact support with your Request ID."
            details = {"request_id": req_id}
        else:
            safe_message = str(exc)
            details = {"request_id": req_id, "exception_type": type(exc).__name__}

        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
            message=safe_message,
            details=details,
        )

    # 3. Healthcheck Endpoints
    @app.get("/healthz", tags=["health"])
    def liveness_check():
        """Liveness check probe returning 200 OK if API server process is responding."""
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.get("/readyz", tags=["health"])
    def readiness_check():
        """Readiness check probe validating database and Redis connectivity."""
        db_report = check_db_health()
        redis_healthy, redis_latency, redis_err = check_redis_health()

        is_ready = db_report.is_healthy and redis_healthy
        status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

        response_data = {
            "status": "ready" if is_ready else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "database": {
                    "healthy": db_report.is_healthy,
                    "latency_ms": db_report.latency_ms,
                    "postgis_version": db_report.postgis_version,
                    "error": db_report.error_message,
                },
                "redis": {
                    "healthy": redis_healthy,
                    "latency_ms": redis_latency,
                    "error": redis_err,
                },
            },
        }
        return JSONResponse(status_code=status_code, content=response_data)

    @app.get("/metrics", tags=["observability"])
    def metrics_scrape():
        """Prometheus metrics scrape endpoint."""
        return PlainTextResponse(
            get_metrics().export_prometheus_text(),
            media_type="text/plain; version=0.0.4",
        )

    # 4. Mount Modular Routers
    app.include_router(events_router)
    app.include_router(articles_router)
    app.include_router(sources_router)
    app.include_router(locations_router)
    app.include_router(clustering_router)
    app.include_router(search_router)
    app.include_router(analytics_router)
    app.include_router(admin_router)

    return app


# Default ASGI application instance for Uvicorn
app = create_app()
