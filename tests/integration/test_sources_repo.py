"""Integration tests for Source repository, seed, and service lifecycle."""

import unittest
from uuid import uuid4

from backend.app.common.db.connection import get_db_session
from backend.app.modules.sources.schemas import SourceCreateRequest, SourceUpdateRequest
from backend.app.modules.sources.seed import seed_sources
from backend.app.modules.sources.service import SourceService


class TestSourcesIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.session_cm = get_db_session()
        self.db = self.session_cm.__enter__()
        self.service = SourceService(self.db)

    def tearDown(self) -> None:
        self.db.rollback()
        self.session_cm.__exit__(None, None, None)

    def test_source_seed_and_priority_ordering(self) -> None:
        seeded_count = seed_sources(self.db)
        self.assertGreaterEqual(seeded_count, 0)

        active = self.service.get_active_sources()
        self.assertGreater(len(active), 0)

        # Verify priority descending order
        priorities = [s.priority for s in active]
        self.assertEqual(priorities, sorted(priorities, reverse=True))

    def test_source_registration_and_toggle_status(self) -> None:
        unique_domain = f"test-publisher-{uuid4().hex[:8]}.vn"
        data = SourceCreateRequest(
            name="Test Publisher",
            domain=unique_domain,
            rss_url=f"https://{unique_domain}/rss.xml",
            priority=77,
            active=True,
        )
        created = self.service.register_source(data)
        self.assertEqual(created.domain, unique_domain)
        self.assertTrue(created.active)

        # Toggle to inactive
        updated = self.service.toggle_source_status(created.id, active=False)
        self.assertFalse(updated.active)

        # Verify excluded from get_active_sources
        active_domains = [s.domain for s in self.service.get_active_sources()]
        self.assertNotIn(unique_domain, active_domains)

    def test_record_source_crawl_result(self) -> None:
        unique_domain = f"test-crawl-{uuid4().hex[:8]}.vn"
        data = SourceCreateRequest(
            name="Crawl Source",
            domain=unique_domain,
            rss_url=f"https://{unique_domain}/rss.xml",
        )
        created = self.service.register_source(data)
        self.assertIsNone(created.last_success_at)
        self.assertIsNone(created.last_error_at)

        # Record success
        self.service.record_source_crawl_result(created.id, success=True)
        self.assertIsNotNone(created.last_success_at)

        # Record error
        self.service.record_source_crawl_result(created.id, success=False, error_msg="Timeout")
        self.assertIsNotNone(created.last_error_at)


if __name__ == "__main__":
    unittest.main()
