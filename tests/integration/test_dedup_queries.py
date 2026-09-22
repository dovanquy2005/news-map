"""Integration tests for ArticleDeduplicator tiered hierarchy."""

from datetime import datetime, timezone
import unittest
from uuid import uuid4

from backend.app.common.db.connection import get_db_session
from backend.app.common.db.models.article import Article
from backend.app.common.db.models.source import Source
from backend.app.modules.articles.deduplicator import ArticleDeduplicator, DedupLevel
from backend.app.modules.articles.schemas import NormalizedArticleDTO


class TestDeduplicationIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.session_cm = get_db_session()
        self.db = self.session_cm.__enter__()
        self.deduplicator = ArticleDeduplicator(self.db)

        # Create source
        self.source = Source(
            name=f"Dedup Source {uuid4().hex[:6]}",
            domain=f"dedup-{uuid4().hex[:6]}.vn",
            source_type="RSS",
            active=True,
            priority=50,
        )
        self.db.add(self.source)
        self.db.commit()

    def tearDown(self) -> None:
        self.db.rollback()
        self.session_cm.__exit__(None, None, None)

    def test_level_1_exact_canonical_url(self) -> None:
        canonical_url = f"https://{self.source.domain}/article-1.html"
        content_hash = "1111111111111111111111111111111111111111111111111111111111111111"

        existing = Article(
            source_id=self.source.id,
            url=canonical_url + "?utm_source=rss",
            canonical_url=canonical_url,
            title="Dự án giao thông trọng điểm",
            content_excerpt="Nội dung bài viết",
            content_hash=content_hash,
            published_at=datetime.now(timezone.utc),
        )
        self.db.add(existing)
        self.db.commit()

        incoming = NormalizedArticleDTO(
            source_id=self.source.id,
            url=canonical_url + "?ref=share",
            canonical_url=canonical_url,
            title="Dự án giao thông trọng điểm",
            content_excerpt="Nội dung bài viết",
            published_at=datetime.now(timezone.utc),
            content_hash="2222222222222222222222222222222222222222222222222222222222222222",
        )

        decision = self.deduplicator.evaluate_article(incoming)
        self.assertTrue(decision.is_duplicate)
        self.assertEqual(decision.dedup_level, DedupLevel.EXACT_URL)
        self.assertEqual(decision.matched_article_id, existing.id)

    def test_level_2_content_hash(self) -> None:
        content_hash = f"{uuid4().hex}{uuid4().hex}"
        url1 = f"https://{self.source.domain}/article-a-{uuid4().hex[:6]}.html"
        url2 = f"https://{self.source.domain}/article-b-{uuid4().hex[:6]}.html"

        existing = Article(
            source_id=self.source.id,
            url=url1,
            canonical_url=url1,
            title="Bài viết nội dung gốc",
            content_excerpt="Đoạn trích tin tức quan trọng",
            content_hash=content_hash,
            published_at=datetime.now(timezone.utc),
        )
        self.db.add(existing)
        self.db.commit()

        incoming = NormalizedArticleDTO(
            source_id=self.source.id,
            url=url2,
            canonical_url=url2,  # Different canonical URL
            title="Bài viết nội dung gốc",
            content_excerpt="Đoạn trích tin tức quan trọng",
            published_at=datetime.now(timezone.utc),
            content_hash=content_hash,  # Identical content hash
        )

        decision = self.deduplicator.evaluate_article(incoming)
        self.assertTrue(decision.is_duplicate)
        self.assertEqual(decision.dedup_level, DedupLevel.CONTENT_HASH)
        self.assertEqual(decision.matched_article_id, existing.id)


if __name__ == "__main__":
    unittest.main()
