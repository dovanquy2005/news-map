"""Text and title semantic similarity calculation."""

from __future__ import annotations

import re

VIETNAMESE_STOPWORDS = {
    "tại", "ở", "lúc", "vào", "ngày", "vụ", "các", "nhiều", "bị", "được", "do", "và", "cho", "với", "là", "của", "ra", "đang"
}


def _tokenize(text: str) -> set[str]:
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    words = [w for w in clean.split() if len(w) > 0 and w not in VIETNAMESE_STOPWORDS]
    return set(words)


def _char_ngrams(text: str, n: int = 3) -> set[str]:
    clean = re.sub(r"\s+", " ", text.lower()).strip()
    if len(clean) < n:
        return {clean}
    return {clean[i : i + n] for i in range(len(clean) - n + 1)}


def compute_text_similarity(art_title: str, cand_title: str) -> float:
    """Compute lexical and n-gram overlap similarity with containment bonus."""
    if not art_title or not cand_title:
        return 0.0

    # 1. Content word tokens
    words1 = _tokenize(art_title)
    words2 = _tokenize(cand_title)
    if not words1 or not words2:
        return 0.0

    word_intersect = len(words1.intersection(words2))
    word_union = len(words1.union(words2))
    word_jaccard = word_intersect / word_union if word_union > 0 else 0.0

    # Containment (overlap relative to shorter title)
    min_len = min(len(words1), len(words2))
    containment = word_intersect / min_len if min_len > 0 else 0.0

    # 2. Tri-gram Jaccard
    ngrams1 = _char_ngrams(art_title, 3)
    ngrams2 = _char_ngrams(cand_title, 3)
    ngram_intersect = len(ngrams1.intersection(ngrams2))
    ngram_union = len(ngrams1.union(ngrams2))
    ngram_jaccard = ngram_intersect / ngram_union if ngram_union > 0 else 0.0

    # Weighted blend: 30% Jaccard, 40% Containment, 30% Tri-grams
    return 0.3 * word_jaccard + 0.4 * containment + 0.3 * ngram_jaccard
