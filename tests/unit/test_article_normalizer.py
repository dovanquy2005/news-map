"""Unit tests for ArticleNormalizer and URL cleaner."""

from datetime import datetime, timezone
import unittest
from uuid import uuid4

from backend.app.modules.articles.normalizer import ArticleNormalizer
from backend.app.modules.articles.url_cleaner import canonicalize_url
from backend.app.modules.sources.adapters.base import RawArticleDTO


class TestArticleNormalizerUnit(unittest.TestCase):
    def setUp(self) -> None:
        self.normalizer = ArticleNormalizer()

    def test_canonicalize_url_strips_tracking(self) -> None:
        dirty_url = (
            "https://vnexpress.net/thoi-su/du-an-metro-48000.html?"
            "utm_source=rss&utm_medium=feed&utm_campaign=daily&fbclid=IwAR123&ref=home#comments"
        )
        clean = canonicalize_url(dirty_url)
        self.assertEqual(clean, "https://vnexpress.net/thoi-su/du-an-metro-48000.html")
        self.assertNotIn("utm_", clean)
        self.assertNotIn("fbclid", clean)
        self.assertNotIn("#comments", clean)

    def test_strip_html_and_scripts(self) -> None:
        dirty_html = (
            "<p>Tin nóng: <script>alert('xss')</script>"
            "<b>Hà Nội</b> khánh thành dự án <a href='https://example.com'>tại đây</a>.</p>"
        )
        clean = self.normalizer.strip_html_tags(dirty_html)
        self.assertNotIn("<script>", clean)
        self.assertNotIn("alert", clean)
        self.assertNotIn("<p>", clean)
        self.assertNotIn("<b>", clean)
        self.assertIn("Hà Nội khánh thành dự án tại đây", clean)

    def test_vietnamese_unicode_normalization(self) -> None:
        # Check NFC normalization on Vietnamese diacritics
        raw_text = "Thành   phố   Hồ   Chí   Minh   \n\n   khởi   công"
        clean = self.normalizer.normalize_text(raw_text)
        self.assertEqual(clean, "Thành phố Hồ Chí Minh khởi công")

    def test_parse_datetime_variants(self) -> None:
        # RFC 822 with +0700 timezone offset (ICT)
        rfc_date = "Mon, 16 Mar 2026 14:00:00 +0700"
        dt1 = self.normalizer.parse_datetime(rfc_date)
        self.assertEqual(dt1.tzinfo, timezone.utc)
        self.assertEqual(dt1.hour, 7)  # 14:00 +07:00 == 07:00 UTC

        # ISO 8601
        iso_date = "2026-03-16T10:30:00Z"
        dt2 = self.normalizer.parse_datetime(iso_date)
        self.assertEqual(dt2.hour, 10)
        self.assertEqual(dt2.minute, 30)

    def test_content_hash_determinism(self) -> None:
        h1 = self.normalizer.compute_content_hash("Tiêu đề bài viết", "Đoạn trích nội dung")
        h2 = self.normalizer.compute_content_hash("Tiêu đề bài viết", "Đoạn trích nội dung")
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_normalize_full_dto(self) -> None:
        source_id = uuid4()
        raw = RawArticleDTO(
            source_id=source_id,
            source_url="https://tuoitre.vn/bai-viet.htm?utm_source=fb",
            title="<b>Tin tức mới</b>",
            summary_raw="<p>Mô tả chi tiết <i>sự kiện</i>.</p>",
            published_at_raw="2026-03-16T08:00:00Z",
        )
        normalized = self.normalizer.normalize(raw)
        self.assertEqual(normalized.title, "Tin tức mới")
        self.assertEqual(normalized.content_excerpt, "Mô tả chi tiết sự kiện.")
        self.assertEqual(normalized.canonical_url, "https://tuoitre.vn/bai-viet.htm")
        self.assertEqual(len(normalized.content_hash), 64)


if __name__ == "__main__":
    unittest.main()
