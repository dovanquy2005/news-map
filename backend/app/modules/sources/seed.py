"""Database seed script for official Vietnamese news sources."""

from __future__ import annotations

import logging
from sqlalchemy.orm import Session

from backend.app.common.db.connection import get_db_session
from backend.app.modules.sources.schemas import SourceCreateRequest
from backend.app.modules.sources.service import SourceService

logger = logging.getLogger(__name__)

INITIAL_SOURCES = [
    SourceCreateRequest(
        name="VnExpress",
        domain="vnexpress.net",
        source_type="RSS",
        rss_url="https://vnexpress.net/rss/thoi-su.rss",
        parser_type="RSS",
        priority=95,
        rate_limit_rpm=60,
        terms_url="https://vnexpress.net/dieu-khoan-su-dung",
        active=True,
    ),
    SourceCreateRequest(
        name="Tuổi Trẻ",
        domain="tuoitre.vn",
        source_type="RSS",
        rss_url="https://tuoitre.vn/rss/thoi-su.rss",
        parser_type="RSS",
        priority=90,
        rate_limit_rpm=60,
        terms_url="https://tuoitre.vn/dieu-khoan-su-dung.htm",
        active=True,
    ),
    SourceCreateRequest(
        name="Thanh Niên",
        domain="thanhnien.vn",
        source_type="RSS",
        rss_url="https://thanhnien.vn/rss/thoi-su.rss",
        parser_type="RSS",
        priority=85,
        rate_limit_rpm=60,
        terms_url="https://thanhnien.vn/dieu-khoan-su-dung.htm",
        active=True,
    ),
    SourceCreateRequest(
        name="Dân Trí",
        domain="dantri.com.vn",
        source_type="RSS",
        rss_url="https://dantri.com.vn/rss/xa-hoi.rss",
        parser_type="RSS",
        priority=80,
        rate_limit_rpm=60,
        terms_url="https://dantri.com.vn/dieu-khoan-su-dung.htm",
        active=True,
    ),
    SourceCreateRequest(
        name="VTV News",
        domain="vtv.vn",
        source_type="RSS",
        rss_url="https://vtv.vn/rss/trong-nuoc.rss",
        parser_type="RSS",
        priority=80,
        rate_limit_rpm=60,
        terms_url="https://vtv.vn/dieu-khoan-su-dung.htm",
        active=True,
    ),
]


def seed_sources(session: Session) -> int:
    """Seeds default Vietnamese news sources if not already present."""
    service = SourceService(session)
    seeded = 0
    for item in INITIAL_SOURCES:
        existing = service.repo.get_by_domain(item.domain)
        if not existing:
            service.register_source(item)
            seeded += 1
            logger.info("Seeded news source: %s (%s)", item.name, item.domain)
    return seeded


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with get_db_session() as db:
        count = seed_sources(db)
        print(f"Successfully seeded {count} sources.")
