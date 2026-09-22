"""Unit tests for Article Deduplication similarity functions."""

import unittest

from backend.app.modules.articles.similarity import (
    compute_title_similarity,
    jaccard_similarity,
    sequence_matcher_similarity,
)


class TestArticleSimilarityUnit(unittest.TestCase):
    def test_identical_titles(self) -> None:
        title = "Hà Nội chuẩn bị khánh thành tuyến metro số 2"
        self.assertEqual(compute_title_similarity(title, title), 1.0)

    def test_high_similarity_minor_edit(self) -> None:
        t1 = "Hà Nội chuẩn bị khánh thành tuyến metro số 2"
        t2 = "Hà Nội chuẩn bị khánh thành tuyến metro số 2 sáng nay"
        sim = compute_title_similarity(t1, t2)
        self.assertGreaterEqual(sim, 0.85)

    def test_distinct_topics_low_similarity(self) -> None:
        t1 = "Hà Nội chuẩn bị khánh thành tuyến metro số 2"
        t2 = "Giá vàng SJC tăng vọt lên mức kỷ lục"
        sim = compute_title_similarity(t1, t2)
        self.assertLess(sim, 0.3)


if __name__ == "__main__":
    unittest.main()
