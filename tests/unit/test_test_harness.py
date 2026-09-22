"""Unit tests verifying test harness fixtures and isolation."""

import json
from pathlib import Path
import unittest

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


class TestTestingHarness(unittest.TestCase):
    def test_sources_fixtures_valid_json(self) -> None:
        sources_file = FIXTURES_DIR / "sources.json"
        self.assertTrue(sources_file.exists())
        with open(sources_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        first = data[0]
        self.assertIn("domain", first)
        self.assertIn("rss_url", first)
        self.assertIn("priority", first)

    def test_articles_fixtures_valid_json(self) -> None:
        articles_file = FIXTURES_DIR / "articles.json"
        self.assertTrue(articles_file.exists())
        with open(articles_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        first = data[0]
        self.assertIn("canonical_url", first)
        self.assertIn("content_hash", first)
        self.assertIn("title", first)

    def test_events_fixtures_valid_json(self) -> None:
        events_file = FIXTURES_DIR / "events.json"
        self.assertTrue(events_file.exists())
        with open(events_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        first = data[0]
        self.assertIn("title", first)
        self.assertIn("category", first)
        self.assertIn("location", first)
        self.assertIn("latitude", first["location"])
        self.assertIn("longitude", first["location"])


if __name__ == "__main__":
    unittest.main()
