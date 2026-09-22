"""Integration tests for Database Foundation (TASK-003).

Verifies against active PostgreSQL container:
- Extensions: postgis, uuid-ossp, and vector
- Database health check latency (< 50ms) and diagnosis
- Connection pool concurrent acquisition and cleanup
- Session context manager commit and rollback mechanics
"""

import concurrent.futures
import unittest
from sqlalchemy import create_engine, text

from backend.app.common.db.connection import (
    get_db_engine,
    get_db_session,
    reset_db_engine,
)
from backend.app.common.db.health import check_db_health


class TestDatabaseFoundationIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reset_db_engine()
        cls.engine = get_db_engine()

    @classmethod
    def tearDownClass(cls):
        reset_db_engine()

    def test_postgis_extension_active(self):
        """PostGIS extension must be active and report valid version."""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT PostGIS_Version();")).scalar()
            self.assertIsNotNone(result)
            self.assertTrue(str(result).startswith("3."), f"Expected PostGIS 3.x, got: {result}")

    def test_uuid_and_vector_extensions_active(self):
        """uuid-ossp and vector extensions must be registered in pg_extension."""
        with self.engine.connect() as conn:
            extensions = conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'vector', 'postgis');")
            ).scalars().all()

            self.assertIn("postgis", extensions)
            self.assertIn("uuid-ossp", extensions)
            self.assertIn("vector", extensions)

    def test_database_health_check_performance(self):
        """Database health probe must return healthy and respond under 50ms budget."""
        report = check_db_health(self.engine)
        self.assertTrue(report.is_healthy, f"DB Health failed: {report.error_message}")
        self.assertIsNotNone(report.postgis_version)
        self.assertIsNotNone(report.pgvector_version)
        self.assertLess(report.latency_ms, 50.0, f"Health check took {report.latency_ms}ms, exceeded 50ms")

    def test_connection_pool_concurrency(self):
        """Simulate concurrent worker connection checkouts without pool exhaustion."""
        def worker_task(idx: int) -> int:
            with get_db_session() as session:
                val = session.execute(text(f"SELECT {idx} AS id;")).scalar()
                return int(val)

        # Run 10 parallel queries
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker_task, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        self.assertEqual(sorted(results), list(range(10)))

    def test_session_context_manager_rollback_on_error(self):
        """Context manager must cleanly rollback transaction on error and release connection."""
        class CustomTestException(Exception):
            pass

        with self.assertRaises(CustomTestException):
            with get_db_session() as session:
                session.execute(text("SELECT 1;"))
                raise CustomTestException("Simulated error inside transaction")

        # Ensure subsequent session checkout succeeds immediately without hanging
        with get_db_session() as session:
            val = session.execute(text("SELECT 100;")).scalar()
            self.assertEqual(val, 100)

    def test_unhealthy_db_handling(self):
        """Invalid connection settings should report is_healthy=False without leaking credentials."""
        bad_engine = create_engine(
            "postgresql+psycopg://news_map:dummy@127.0.0.1:59999/invalid_db?connect_timeout=1"
        )
        report = check_db_health(bad_engine)
        self.assertFalse(report.is_healthy)
        self.assertIn("Database connection failed", str(report.error_message))
        self.assertNotIn("dummy", str(report.error_message))
        bad_engine.dispose()


if __name__ == "__main__":
    unittest.main()
