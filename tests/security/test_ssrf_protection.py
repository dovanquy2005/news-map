"""Security regression test suite verifying SSRF and network isolation defenses."""

import unittest

from backend.app.common.security.http_client import SafeHttpClient
from backend.app.common.security.ip_validator import (
    SSRFValidationError,
    is_ip_allowed,
    resolve_and_validate_hostname,
)


class TestSSRFProtection(unittest.TestCase):
    def setUp(self) -> None:
        self.client = SafeHttpClient(allow_http_for_dev=False)

    def test_block_loopback_ips(self) -> None:
        loopback_targets = [
            "127.0.0.1",
            "127.0.1.1",
            "localhost",
            "::1",
        ]
        for target in loopback_targets:
            self.assertFalse(is_ip_allowed(target), f"Should reject loopback IP: {target}")
            with self.assertRaises(SSRFValidationError, msg=f"Should raise SSRF error for {target}"):
                resolve_and_validate_hostname(target)

    def test_block_cloud_metadata_ips(self) -> None:
        metadata_ip = "169.254.169.254"
        self.assertFalse(is_ip_allowed(metadata_ip))
        with self.assertRaises(SSRFValidationError):
            resolve_and_validate_hostname(metadata_ip)

        with self.assertRaises(SSRFValidationError):
            self.client.fetch(f"https://{metadata_ip}/latest/meta-data/")

    def test_block_rfc1918_private_ranges(self) -> None:
        private_ips = [
            "10.0.0.1",
            "10.255.255.255",
            "172.16.0.1",
            "172.31.255.255",
            "192.168.1.1",
            "192.168.0.100",
        ]
        for ip in private_ips:
            self.assertFalse(is_ip_allowed(ip), f"Should reject private IP {ip}")
            with self.assertRaises(SSRFValidationError):
                resolve_and_validate_hostname(ip)

    def test_reject_insecure_http_scheme(self) -> None:
        with self.assertRaises(SSRFValidationError):
            self.client.fetch("http://vnexpress.net/rss.xml")

    def test_reject_domain_mismatch(self) -> None:
        with self.assertRaises(SSRFValidationError):
            # Attempt to fetch attacker.com claiming to be vnexpress.net
            self.client.fetch(
                "https://attacker.com/rss.xml",
                expected_domain="vnexpress.net",
            )

    def test_allow_valid_subdomain(self) -> None:
        # Check domain validator logic: thoisu.vnexpress.net matches vnexpress.net
        scheme, host = self.client._validate_url_and_domain(
            "https://vnexpress.net/thoi-su",
            expected_domain="vnexpress.net",
        )
        self.assertEqual(host, "vnexpress.net")


if __name__ == "__main__":
    unittest.main()
