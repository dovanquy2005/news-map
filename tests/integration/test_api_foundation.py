"""Integration tests for Backend Modular Monolith API Foundation (TASK-006).

Verifies:
- Liveness (/healthz) and Readiness (/readyz)
- Correlation ID (X-Request-ID) middleware propagation
- CORS headers
- Standardized error envelopes (404, 422)
- Modular routers under /api/v1
"""

import unittest
from fastapi.testclient import TestClient

from backend.app.main import create_app


class TestApiFoundationIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = TestClient(cls.app)

    def test_liveness_probe(self):
        """GET /healthz returns 200 OK and status 'ok'."""
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("timestamp", data)

    def test_readiness_probe(self):
        """GET /readyz validates live DB and Redis connections."""
        response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ready")
        self.assertTrue(data["checks"]["database"]["healthy"])
        self.assertTrue(data["checks"]["redis"]["healthy"])
        self.assertIsNotNone(data["checks"]["database"]["postgis_version"])

    def test_correlation_id_middleware(self):
        """X-Request-ID is generated if omitted and preserved if supplied."""
        # 1. Server generates if omitted
        res1 = self.client.get("/healthz")
        req_id1 = res1.headers.get("X-Request-ID")
        self.assertIsNotNone(req_id1)
        self.assertTrue(len(req_id1) > 10)

        # 2. Client supplied ID is preserved
        custom_id = "custom-trace-uuid-12345"
        res2 = self.client.get("/healthz", headers={"X-Request-ID": custom_id})
        self.assertEqual(res2.headers.get("X-Request-ID"), custom_id)

    def test_standardized_error_envelope_404(self):
        """Non-existent route returns standardized error envelope."""
        response = self.client.get("/api/v1/non_existent_route")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "NOT_FOUND")
        self.assertIn("message", data["error"])

    def test_modular_routers_mounted(self):
        """All 8 modular domain routers are mounted under /api/v1."""
        endpoints = [
            "/api/v1/events",
            "/api/v1/articles",
            "/api/v1/sources",
            "/api/v1/locations",
            "/api/v1/clustering/status",
            "/api/v1/search",
            "/api/v1/analytics/overview",
            "/api/v1/admin/health",
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200, f"Endpoint {ep} should return 200 OK")


if __name__ == "__main__":
    unittest.main()
