"""Unit tests for RSSFeedAdapter and XML safety."""

from pathlib import Path
import unittest
from uuid import uuid4

from backend.app.modules.sources.adapters.rss import RSSFeedAdapter

FEEDS_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "feeds"


class TestRSSAdapterUnit(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = RSSFeedAdapter()
        self.dummy_source_id = uuid4()

    def test_parse_valid_rss2(self) -> None:
        file_path = FEEDS_DIR / "sample_rss2.xml"
        self.assertTrue(file_path.exists())
        with open(file_path, "r", encoding="utf-8") as f:
            xml_data = f.read()

        items = self.adapter.parse_xml_content(xml_data, self.dummy_source_id)
        self.assertEqual(len(items), 2)

        first = items[0]
        self.assertEqual(first.title, "Hà Nội khánh thành hầm chui nút giao Kim Đồng")
        self.assertIn("4812345.html", first.source_url)
        self.assertIn("Kim Đồng", first.summary_raw or "")
        self.assertIsNotNone(first.published_at_raw)
        self.assertIsNotNone(first.image_url)

    def test_parse_valid_atom(self) -> None:
        file_path = FEEDS_DIR / "sample_atom.xml"
        self.assertTrue(file_path.exists())
        with open(file_path, "r", encoding="utf-8") as f:
            xml_data = f.read()

        items = self.adapter.parse_xml_content(xml_data, self.dummy_source_id)
        self.assertEqual(len(items), 1)

        entry = items[0]
        self.assertIn("Cảnh báo mưa lớn", entry.title)
        self.assertEqual(entry.author_raw, "Đức Tuyên")
        self.assertIn("tuoitre.vn", entry.source_url)

    def test_xxe_exploit_is_neutralized(self) -> None:
        file_path = FEEDS_DIR / "xxe_exploit.xml"
        self.assertTrue(file_path.exists())
        with open(file_path, "r", encoding="utf-8") as f:
            xml_data = f.read()

        items = self.adapter.parse_xml_content(xml_data, self.dummy_source_id)
        # Verify no external file contents leaked
        for item in items:
            self.assertNotIn("root:x:0:0", item.title)
            self.assertNotIn("root:x:0:0", item.summary_raw or "")

    def test_malformed_xml_graceful_handling(self) -> None:
        broken_xml = "<rss><channel><item><title>Broken without closing"
        items = self.adapter.parse_xml_content(broken_xml, self.dummy_source_id)
        self.assertIsInstance(items, list)


if __name__ == "__main__":
    unittest.main()
