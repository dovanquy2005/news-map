"""Event facts aggregation and conflict detection service."""

from __future__ import annotations

from collections import defaultdict
import logging
import re
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.common.db.models.article import Article
from backend.app.common.db.models.event import Event
from backend.app.common.db.models.event_article import EventArticle
from backend.app.common.db.models.event_fact import EventFact

logger = logging.getLogger(__name__)


def _normalize_key(key: str) -> str:
    clean = re.sub(r"[^\w\s]", "", key.lower().strip())
    return re.sub(r"\s+", "_", clean)[:100]


class EventFactsService:
    """Aggregates factual claims and flags cross-source conflicts."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def aggregate_facts(self, event_id: UUID) -> List[EventFact]:
        """Collect facts from all attached articles, resolve consensus, and detect conflicts."""
        stmt = (
            select(Article)
            .join(EventArticle, EventArticle.article_id == Article.id)
            .where(EventArticle.event_id == event_id)
        )
        articles = self._session.scalars(stmt).all()
        if not articles:
            return []

        # Key -> list of (value, article_id)
        raw_facts_by_key: Dict[str, List[str]] = defaultdict(list)

        for art in articles:
            extraction = art.raw_metadata.get("extraction", {})
            key_facts = extraction.get("key_facts", [])
            for fact_text in key_facts:
                if ":" in fact_text:
                    k, v = fact_text.split(":", 1)
                elif "-" in fact_text:
                    k, v = fact_text.split("-", 1)
                else:
                    k, v = "thông_tin_chính", fact_text
                norm_k = _normalize_key(k)
                clean_v = v.strip()
                if clean_v:
                    raw_facts_by_key[norm_k].append(clean_v)

        # Clear existing facts for clean re-aggregation
        self._session.execute(delete(EventFact).where(EventFact.event_id == event_id))

        persisted_facts: List[EventFact] = []
        for norm_k, values in raw_facts_by_key.items():
            unique_values = list(set(values))
            supporting_count = len(values)

            if len(unique_values) == 1:
                # High consensus
                fact = EventFact(
                    event_id=event_id,
                    fact_key=norm_k,
                    fact_value=unique_values[0],
                    fact_confidence=0.95,
                    supporting_article_count=supporting_count,
                )
            else:
                # Conflicting claims across sources
                divergent_text = " / ".join(unique_values[:3])
                fact = EventFact(
                    event_id=event_id,
                    fact_key=norm_k,
                    fact_value=f"{divergent_text} [CẦN XÁC MINH - CHƯA THỐNG NHẤT]",
                    fact_confidence=0.40,
                    supporting_article_count=supporting_count,
                )

            self._session.add(fact)
            persisted_facts.append(fact)

        self._session.flush()
        return persisted_facts
