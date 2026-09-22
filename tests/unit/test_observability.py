"""Unit tests for Observability Foundation (TASK-010).

Verifies:
- Secret redaction filter masks passwords, tokens, and database credentials
- JSON log formatter outputs structured JSON lines
- MetricsRegistry collects counters and gauges and exports Prometheus format
- GET /metrics endpoint responds cleanly
"""

import json
import logging
import unittest
from fastapi.testclient import TestClient

from backend.app.common.logging.logger import JSONLogFormatter, SecretMaskingFilter
from backend.app.common.metrics.registry import MetricsRegistry
from backend.app.main import create_app


class TestObservability(unittest.TestCase):
    def test_secret_masking_filter(self):
        """Sensitive credentials must be masked before log output."""
        sensitive_samples = [
            ("Connecting with password=SuperSecretPass123! to server", "password=******"),
            ("Auth token is Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "Bearer [REDACTED]"),
            ("Postgres URI postgresql://user:SecretDbPass999@localhost:5432/db", "postgresql://user:******@localhost:5432/db"),
            ("Using api_key: AIzaSySecretKey1234567890", "api_key=******"),
        ]

        for raw_text, expected_mask in sensitive_samples:
            masked = SecretMaskingFilter.mask_secrets(raw_text)
            self.assertIn(expected_mask, masked, f"Failed masking for: {raw_text}")
            self.assertNotIn("SuperSecretPass123!", masked)
            self.assertNotIn("SecretDbPass999", masked)

    def test_json_log_formatter(self):
        """Log records must serialize to valid JSON with required metadata."""
        formatter = JSONLogFormatter(service_name="test-service")
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="User login successful",
            args=(),
            exc_info=None,
        )
        record.request_id = "trace-uuid-12345"

        formatted_line = formatter.format(record)
        data = json.loads(formatted_line)

        self.assertEqual(data["level"], "INFO")
        self.assertEqual(data["service"], "test-service")
        self.assertEqual(data["message"], "User login successful")
        self.assertEqual(data["request_id"], "trace-uuid-12345")
        self.assertIn("timestamp", data)

    def test_metrics_registry_prometheus_format(self):
        """MetricsRegistry correctly records counters, gauges, and formats text."""
        metrics = MetricsRegistry()
        metrics.inc_counter("http_requests_total", 5.0, labels={"status": "200", "method": "GET"})
        metrics.set_gauge("queue_depth", 42.0, labels={"queue": "ingestion"})

        self.assertEqual(
            metrics.get_counter("http_requests_total", labels={"status": "200", "method": "GET"}),
            5.0,
        )
        self.assertEqual(
            metrics.get_gauge("queue_depth", labels={"queue": "ingestion"}),
            42.0,
        )

        output = metrics.export_prometheus_text()
        self.assertIn('http_requests_total{method="GET",status="200"} 5.0', output)
        self.assertIn('queue_depth{queue="ingestion"} 42.0', output)

    def test_metrics_http_endpoint(self):
        """GET /metrics returns 200 with Prometheus media type."""
        app = create_app()
        client = TestClient(app)
        res = client.get("/metrics")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/plain", res.headers.get("content-type", ""))


if __name__ == "__main__":
    unittest.main()
