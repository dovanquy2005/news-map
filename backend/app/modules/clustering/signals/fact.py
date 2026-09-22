"""Fact overlap similarity calculation."""

from __future__ import annotations

from typing import List


def compute_fact_overlap(art_facts: List[str], cand_facts: List[str]) -> float:
    """Compute overlap ratio of key factual claims."""
    if not art_facts and not cand_facts:
        return 0.5  # Neutral when neither has extracted facts

    set1 = {f.strip().lower() for f in art_facts if f.strip()}
    set2 = {f.strip().lower() for f in cand_facts if f.strip()}

    if not set1 or not set2:
        return 0.4  # Mild baseline if one side has facts

    intersect = len(set1.intersection(set2))
    union = len(set1.union(set2))

    return intersect / union if union > 0 else 0.0
