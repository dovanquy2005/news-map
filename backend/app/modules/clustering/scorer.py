"""Multi-signal event clustering scorer and decision policy engine."""

from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple

from backend.app.modules.clustering.candidate_retriever import COMPATIBLE_CATEGORIES
from backend.app.modules.clustering.schemas import (
    ClusteringDecision,
    ClusteringDecisionDTO,
    ClusteringSignalBreakdown,
    EventCandidateDTO,
)
from backend.app.modules.clustering.signals.entity import compute_entity_overlap
from backend.app.modules.clustering.signals.fact import compute_fact_overlap
from backend.app.modules.clustering.signals.location import compute_location_similarity
from backend.app.modules.clustering.signals.text import compute_text_similarity
from backend.app.modules.clustering.signals.time import compute_time_similarity

logger = logging.getLogger(__name__)

DEFAULT_WEIGHTS: Dict[str, float] = {
    "location": 0.25,
    "time": 0.20,
    "semantic": 0.25,
    "entity": 0.15,
    "fact": 0.10,
    "category": 0.05,
}

MERGE_THRESHOLD = 0.68
NEW_EVENT_THRESHOLD = 0.40


class ClusteringScorer:
    """Computes weighted multi-signal similarity scores and makes merge decisions."""

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        merge_threshold: float = MERGE_THRESHOLD,
        new_event_threshold: float = NEW_EVENT_THRESHOLD,
    ) -> None:
        self._weights = weights or DEFAULT_WEIGHTS
        self._merge_threshold = merge_threshold
        self._new_event_threshold = new_event_threshold

    def evaluate_candidate(
        self,
        # Article data
        art_title: str,
        art_category: str,
        art_time: datetime,
        art_lat: Optional[float] = None,
        art_lng: Optional[float] = None,
        art_province: Optional[str] = None,
        art_entities: Optional[List[str]] = None,
        art_facts: Optional[List[str]] = None,
        # Candidate data
        candidate: Optional[EventCandidateDTO] = None,
    ) -> Tuple[ClusteringDecision, float, ClusteringSignalBreakdown, str]:
        """Evaluate match between an article and an event candidate."""
        if not candidate:
            breakdown = ClusteringSignalBreakdown(
                location_similarity=0.0,
                time_similarity=0.0,
                semantic_similarity=0.0,
                entity_overlap=0.0,
                fact_overlap=0.0,
                category_match=0.0,
                composite_score=0.0,
            )
            return ClusteringDecision.CREATE_NEW_EVENT, 0.0, breakdown, "No candidates found"

        # 1. Category match
        art_cat_upper = art_category.upper()
        cand_cat_upper = candidate.category.upper()
        if art_cat_upper == cand_cat_upper:
            cat_score = 1.0
        elif cand_cat_upper in COMPATIBLE_CATEGORIES.get(art_cat_upper, []):
            cat_score = 0.6
        else:
            cat_score = 0.0

        # Safety Guard 1: Incompatible categories can NEVER be merged
        if cat_score == 0.0:
            breakdown = ClusteringSignalBreakdown(
                location_similarity=0.0,
                time_similarity=0.0,
                semantic_similarity=0.0,
                entity_overlap=0.0,
                fact_overlap=0.0,
                category_match=0.0,
                composite_score=0.0,
            )
            return (
                ClusteringDecision.CREATE_NEW_EVENT,
                0.0,
                breakdown,
                f"Categories incompatible ({art_category} vs {candidate.category})",
            )

        # 2. Location similarity
        loc_score = compute_location_similarity(
            art_lat=art_lat,
            art_lng=art_lng,
            art_province=art_province,
            cand_lat=candidate.latitude,
            cand_lng=candidate.longitude,
            cand_label=candidate.location_label,
            distance_meters=candidate.distance_meters,
        )

        # 3. Time similarity
        time_score = compute_time_similarity(
            art_time=art_time,
            cand_occurred=candidate.occurred_at,
            cand_updated=candidate.last_updated_at,
        )

        # 4. Semantic / Text similarity
        sem_score = compute_text_similarity(art_title, candidate.title)

        # 5. Entity overlap
        cand_entities = []  # Can be augmented if candidate summary/facts store entities
        ent_score = compute_entity_overlap(art_entities or [], cand_entities)

        # 6. Fact overlap
        cand_facts = []
        fact_score = compute_fact_overlap(art_facts or [], cand_facts)

        # Safety Guard 2: High spatial proximity alone does NOT warrant merge
        # if text and time indicate distinct incidents
        if sem_score < 0.20 and time_score < 0.40:
            composite = min(
                0.35,
                (
                    self._weights["location"] * loc_score
                    + self._weights["time"] * time_score
                    + self._weights["semantic"] * sem_score
                ),
            )
            breakdown = ClusteringSignalBreakdown(
                location_similarity=loc_score,
                time_similarity=time_score,
                semantic_similarity=sem_score,
                entity_overlap=ent_score,
                fact_overlap=fact_score,
                category_match=cat_score,
                composite_score=round(composite, 4),
            )
            return (
                ClusteringDecision.CREATE_NEW_EVENT,
                round(composite, 4),
                breakdown,
                "Divergent semantic content and time despite geographic proximity",
            )

        # Compute weighted composite score
        composite = (
            self._weights["location"] * loc_score
            + self._weights["time"] * time_score
            + self._weights["semantic"] * sem_score
            + self._weights["entity"] * ent_score
            + self._weights["fact"] * fact_score
            + self._weights["category"] * cat_score
        )
        composite = round(min(1.0, max(0.0, composite)), 4)

        breakdown = ClusteringSignalBreakdown(
            location_similarity=round(loc_score, 4),
            time_similarity=round(time_score, 4),
            semantic_similarity=round(sem_score, 4),
            entity_overlap=round(ent_score, 4),
            fact_overlap=round(fact_score, 4),
            category_match=round(cat_score, 4),
            composite_score=composite,
        )

        # Decision policy
        if composite >= self._merge_threshold:
            decision = ClusteringDecision.MERGE
            reason = f"High composite match ({composite:.2f} >= {self._merge_threshold}) across location, time, and content"
        elif composite <= self._new_event_threshold:
            decision = ClusteringDecision.CREATE_NEW_EVENT
            reason = f"Low composite match ({composite:.2f} <= {self._new_event_threshold})"
        else:
            decision = ClusteringDecision.UNCERTAIN
            reason = f"Uncertain composite match ({composite:.2f}). Enforcing conservative separation."

        return decision, composite, breakdown, reason

    def select_best_match(
        self,
        art_title: str,
        art_category: str,
        art_time: datetime,
        candidates: List[EventCandidateDTO],
        art_lat: Optional[float] = None,
        art_lng: Optional[float] = None,
        art_province: Optional[str] = None,
        art_entities: Optional[List[str]] = None,
        art_facts: Optional[List[str]] = None,
    ) -> ClusteringDecisionDTO:
        """Evaluate all candidates and select the best matching event."""
        if not candidates:
            return ClusteringDecisionDTO(
                decision=ClusteringDecision.CREATE_NEW_EVENT,
                target_event_id=None,
                composite_score=0.0,
                match_reason="No candidates available in retrieval window",
            )

        best_decision = ClusteringDecision.CREATE_NEW_EVENT
        best_score = -1.0
        best_cand_id = None
        best_breakdown = None
        best_reason = ""

        for cand in candidates:
            decision, score, breakdown, reason = self.evaluate_candidate(
                art_title=art_title,
                art_category=art_category,
                art_time=art_time,
                art_lat=art_lat,
                art_lng=art_lng,
                art_province=art_province,
                art_entities=art_entities,
                art_facts=art_facts,
                candidate=cand,
            )
            if score > best_score:
                best_score = score
                best_decision = decision
                best_cand_id = cand.event_id
                best_breakdown = breakdown
                best_reason = reason

        # Conservative Safety Principle: UNCERTAIN defaults to CREATE_NEW_EVENT
        final_decision = (
            ClusteringDecision.MERGE
            if best_decision == ClusteringDecision.MERGE
            else ClusteringDecision.CREATE_NEW_EVENT
        )

        return ClusteringDecisionDTO(
            decision=final_decision,
            target_event_id=best_cand_id if final_decision == ClusteringDecision.MERGE else None,
            composite_score=best_score,
            breakdown=best_breakdown,
            match_reason=best_reason,
        )
