"""Pytest fixtures for Vietnam News Map test suite.

Provides isolated database transactions, Redis test isolation, API test clients,
and standardized entity fixtures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient

from backend.app.common.cache.redis import get_redis_client
from backend.app.common.db.connection import get_db_session
from backend.app.main import create_app

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_sources_data() -> list[dict[str, Any]]:
    """Loads standardized source fixtures."""
    with open(FIXTURES_DIR / "sources.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def sample_articles_data() -> list[dict[str, Any]]:
    """Loads standardized article fixtures."""
    with open(FIXTURES_DIR / "articles.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def sample_events_data() -> list[dict[str, Any]]:
    """Loads standardized event fixtures."""
    with open(FIXTURES_DIR / "events.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def api_client() -> Generator[TestClient, None, None]:
    """Provides a FastAPI test client instance with clean dependency scope."""
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture
def isolated_db_session() -> Generator[Any, None, None]:
    """Provides a database session wrapped in a transaction that is rolled back on exit."""
    with get_db_session() as session:
        yield session
        session.rollback()


@pytest.fixture
def isolated_redis() -> Generator[Any, None, None]:
    """Provides an isolated Redis client ensuring test-specific keys are flushed."""
    client = get_redis_client()
    yield client
    # Clean up test keys if any were created with test prefix
    for key in client.scan_iter("vnm:test:*"):
        client.delete(key)
