"""Named entity overlap calculation."""

from __future__ import annotations

from typing import List


def compute_entity_overlap(art_entities: List[str], cand_entities: List[str]) -> float:
    """Compute Jaccard similarity of extracted named entities."""
    if not art_entities and not cand_entities:
        return 0.5  # Neutral when neither has entities

    set1 = {e.strip().lower() for e in art_entities if e.strip()}
    set2 = {e.strip().lower() for e in cand_entities if e.strip()}

    if not set1 or not set2:
        return 0.3  # Mild penalty if one side missing entities

    intersect = len(set1.intersection(set2))
    union = len(set1.union(set2))

    return intersect / union if union > 0 else 0.0
