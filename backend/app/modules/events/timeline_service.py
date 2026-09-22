"""Chronological timeline construction service for events."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import re
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.common.db.models.article import Article
from backend.app.common.db.models.event import Event
from backend.app.common.db.models.event_article import EventArticle
from backend.app.common.db.models.event_timeline import EventTimeline

logger = logging.getLogger(__name__)

OFFICIAL_KEYWORDS = [
    "công an", "chính quyền", "ubnd", "bộ công an", "thông báo chính thức",
    "kết luận điều tra", "cơ quan chức năng", "bộ y tế", "thủ tướng"
]


class EventTimelineService:
    """Extracts and maintains sorted milestones for an event."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def rebuild_timeline(self, event_id: UUID) -> List[EventTimeline]:
        """Reconstruct chronological timeline from attached articles and event metadata."""
        event = self._session.get(Event, event_id)
        if not event:
            return []

        # Fetch all articles linked to this event
        stmt = (
            select(Article)
            .join(EventArticle, EventArticle.article_id == Article.id)
            .where(EventArticle.event_id == event_id)
            .order_by(Article.published_at.asc())
        )
        articles = self._session.scalars(stmt).all()
        if not articles:
            return []

        # Check existing timeline entries
        existing_stmt = select(EventTimeline).where(EventTimeline.event_id == event_id)
        existing_timelines = self._session.scalars(existing_stmt).all()
        existing_keys = {
            (t.timeline_type, t.source_article_id, t.text) for t in existing_timelines
        }

        new_entries: List[EventTimeline] = []

        # 1. Milestone: OCCURRED (if known)
        occurred_key = ("OCCURRED", None, f"Thời điểm xảy ra sự việc ({event.occurred_at.strftime('%H:%M %d/%m/%Y')})")
        if occurred_key not in existing_keys:
            t_occurred = EventTimeline(
                event_id=event_id,
                timestamp=event.occurred_at,
                timeline_type="OCCURRED",
                text=occurred_key[2],
                source_article_id=None,
            )
            self._session.add(t_occurred)
            new_entries.append(t_occurred)
            existing_keys.add(occurred_key)

        # 2. Milestone: FIRST_REPORTED (first article)
        first_art = articles[0]
        first_key = ("FIRST_REPORTED", first_art.id, f"Thông tin ban đầu: {first_art.title}")
        if first_key not in existing_keys:
            t_first = EventTimeline(
                event_id=event_id,
                timestamp=first_art.published_at,
                timeline_type="FIRST_REPORTED",
                text=first_key[2],
                source_article_id=first_art.id,
            )
            self._session.add(t_first)
            new_entries.append(t_first)
            existing_keys.add(first_key)

        # 3. Subsequent milestones: SOURCE_UPDATE or OFFICIAL_STATEMENT
        for art in articles[1:]:
            title_lower = art.title.lower()
            is_official = any(kw in title_lower for kw in OFFICIAL_KEYWORDS)
            t_type = "OFFICIAL_STATEMENT" if is_official else "SOURCE_UPDATE"
            text_desc = f"{'Thông báo chính thức' if is_official else 'Cập nhật'}: {art.title}"

            milestone_key = (t_type, art.id, text_desc)
            if milestone_key not in existing_keys:
                t_item = EventTimeline(
                    event_id=event_id,
                    timestamp=art.published_at,
                    timeline_type=t_type,
                    text=text_desc,
                    source_article_id=art.id,
                )
                self._session.add(t_item)
                new_entries.append(t_item)
                existing_keys.add(milestone_key)

        self._session.flush()

        # Return full timeline ordered by timestamp asc
        all_stmt = (
            select(EventTimeline)
            .where(EventTimeline.event_id == event_id)
            .order_by(EventTimeline.timestamp.asc())
        )
        return list(self._session.scalars(all_stmt).all())
