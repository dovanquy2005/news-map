"""Unit tests for sources schemas and domain validation."""

import unittest
from pydantic import ValidationError

from backend.app.modules.sources.schemas import SourceCreateRequest, SourceUpdateRequest


class TestSourcesDomainValidation(unittest.TestCase):
    def test_valid_source_creation(self) -> None:
        source = SourceCreateRequest(
            name="VnExpress",
            domain="vnexpress.net",
            rss_url="https://vnexpress.net/rss/thoi-su.rss",
            priority=90,
            rate_limit_rpm=60,
        )
        self.assertEqual(source.domain, "vnexpress.net")
        self.assertEqual(source.priority, 90)
        self.assertTrue(source.active)

    def test_reject_invalid_domain_formats(self) -> None:
        invalid_domains = [
            "localhost",
            "127.0.0.1",
            "http://vnexpress.net",
            "not a domain",
            "-vnexpress.net",
        ]
        for bad_domain in invalid_domains:
            with self.assertRaises(ValidationError, msg=f"Should reject: {bad_domain}"):
                SourceCreateRequest(
                    name="Bad Source",
                    domain=bad_domain,
                    rss_url="https://example.com/rss.xml",
                )

    def test_reject_insecure_rss_url(self) -> None:
        with self.assertRaises(ValidationError):
            SourceCreateRequest(
                name="Insecure",
                domain="insecure.com",
                rss_url="http://insecure.com/rss.xml",  # http instead of https
            )

    def test_priority_boundary_validation(self) -> None:
        # Valid bounds
        s1 = SourceCreateRequest(name="S1", domain="s1.com", priority=1)
        s2 = SourceCreateRequest(name="S2", domain="s2.com", priority=100)
        self.assertEqual(s1.priority, 1)
        self.assertEqual(s2.priority, 100)

        # Invalid bounds
        with self.assertRaises(ValidationError):
            SourceCreateRequest(name="Low", domain="s.com", priority=0)

        with self.assertRaises(ValidationError):
            SourceCreateRequest(name="High", domain="s.com", priority=101)


if __name__ == "__main__":
    unittest.main()
