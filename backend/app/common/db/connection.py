"""Database engine, connection pooling, and session management.

Strictly complies with:
- ADR-002: PostgreSQL + PostGIS as Primary Data Store
- docs/04-data-architecture.md (Primary database, Connection pooling)
- docs/11-performance-scalability.md (Database performance)
- tasks/TASK-003-database-foundation.md
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from backend.app.common.config import get_settings


def _normalize_database_url(raw_url: str) -> str:
    """Ensure SQLAlchemy uses psycopg v3 driver for PostgreSQL connections."""
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    return raw_url


_ENGINE: Engine | None = None
_SESSION_FACTORY: sessionmaker[Session] | None = None


def get_db_engine(**kwargs: Any) -> Engine:
    """Create or return the cached SQLAlchemy Engine with configured connection pooling."""
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    settings = get_settings()
    db_url = _normalize_database_url(settings.database_url.get_secret_value())

    pool_size = max(1, settings.db_pool_min)
    max_overflow = max(0, settings.db_pool_max - settings.db_pool_min)
    pool_timeout = max(1.0, float(settings.db_timeout_ms) / 1000.0)

    _ENGINE = create_engine(
        db_url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=1800,  # Recycle connections after 30 minutes to prevent stale sockets
        pool_pre_ping=True,  # Guard against dropped connections
        **kwargs,
    )
    return _ENGINE


def get_session_factory() -> sessionmaker[Session]:
    """Retrieve or initialize the SQLAlchemy sessionmaker."""
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        engine = get_db_engine()
        _SESSION_FACTORY = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SESSION_FACTORY


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager providing an atomic database session.

    Commits on successful completion, rolls back on error, and ensures the
    connection is returned to the pool in all circumstances.
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database session."""
    with get_db_session() as session:
        yield session


def reset_db_engine() -> None:
    """Dispose and reset engine and session factory (primarily used in testing)."""
    global _ENGINE, _SESSION_FACTORY
    if _ENGINE is not None:
        _ENGINE.dispose()
        _ENGINE = None
    _SESSION_FACTORY = None
