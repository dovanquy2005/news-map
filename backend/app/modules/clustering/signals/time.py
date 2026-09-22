"""Time similarity calculation for event clustering."""

from __future__ import annotations

from datetime import datetime


def compute_time_similarity(
    art_time: datetime, cand_occurred: datetime, cand_updated: datetime
) -> float:
    """Compute temporal similarity between article and candidate event using time decay."""
    diff_occurred = abs((art_time - cand_occurred).total_seconds()) / 3600.0
    diff_updated = abs((art_time - cand_updated).total_seconds()) / 3600.0
    min_diff_hours = min(diff_occurred, diff_updated)

    if min_diff_hours <= 2.0:
        return 1.0
    elif min_diff_hours <= 6.0:
        return 0.85
    elif min_diff_hours <= 12.0:
        return 0.70
    elif min_diff_hours <= 24.0:
        return 0.50
    elif min_diff_hours <= 48.0:
        return 0.25
    elif min_diff_hours <= 72.0:
        return 0.15
    else:
        return 0.05
