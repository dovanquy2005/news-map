"""String similarity metrics for title comparison and deduplication heuristic."""

from __future__ import annotations

import difflib
import re

TOKEN_REGEX = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> set[str]:
    """Tokenize lowercased text into set of word tokens."""
    if not text:
        return set()
    return set(TOKEN_REGEX.findall(text.lower()))


def jaccard_similarity(text1: str, text2: str) -> float:
    """Computes Jaccard index between two token sets."""
    set1 = tokenize(text1)
    set2 = tokenize(text2)
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0


def sequence_matcher_similarity(text1: str, text2: str) -> float:
    """Computes Ratcliff/Obershelp string similarity ratio bounded to 500 chars."""
    t1 = text1[:500].lower().strip()
    t2 = text2[:500].lower().strip()
    return difflib.SequenceMatcher(None, t1, t2).ratio()


def compute_title_similarity(title1: str, title2: str) -> float:
    """Blends sequence similarity and token Jaccard similarity for Vietnamese titles."""
    if title1.strip().lower() == title2.strip().lower():
        return 1.0

    seq_sim = sequence_matcher_similarity(title1, title2)
    jaccard_sim = jaccard_similarity(title1, title2)

    # 60% token overlap + 40% character sequence alignment
    return (0.6 * jaccard_sim) + (0.4 * seq_sim)
