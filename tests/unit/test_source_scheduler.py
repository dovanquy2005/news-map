"""Unit tests for SourceScheduler logic and CircuitBreaker."""

from datetime import datetime, timezone, timedelta
import unittest
from uuid import uuid4

from workers.ingestion.health import CircuitBreaker, HealthStatus
from workers.ingestion.scheduler import SourceScheduler


class TestSourceSchedulerUnit(unittest.TestCase):
    def setUp(self) -> None:
        self.circuit_breaker = CircuitBreaker(failure_threshold=5)

    def test_circuit_breaker_healthy_under_threshold(self) -> None:
        status, backoff = self.circuit_breaker.evaluate_status(
            consecutive_failures=2,
            last_success_at=datetime.now(timezone.utc),
        )
        self.assertEqual(status, HealthStatus.HEALTHY)
        self.assertIsNone(backoff)

    def test_circuit_breaker_degraded_before_cutoff(self) -> None:
        status, backoff = self.circuit_breaker.evaluate_status(
            consecutive_failures=4,
            last_success_at=datetime.now(timezone.utc),
        )
        self.assertEqual(status, HealthStatus.DEGRADED)
        self.assertIsNone(backoff)

    def test_circuit_breaker_paused_and_exponential_backoff(self) -> None:
        now = datetime.now(timezone.utc)

        # 5 failures -> 1h backoff
        status, backoff_5 = self.circuit_breaker.evaluate_status(5, None, now=now)
        self.assertEqual(status, HealthStatus.PAUSED)
        self.assertIsNotNone(backoff_5)
        self.assertAlmostEqual(
            (backoff_5 - now).total_seconds(), 3600, delta=5
        )

        # 6 failures -> 4h backoff
        status, backoff_6 = self.circuit_breaker.evaluate_status(6, None, now=now)
        self.assertAlmostEqual(
            (backoff_6 - now).total_seconds(), 14400, delta=5
        )

        # 7+ failures -> 24h backoff
        status, backoff_7 = self.circuit_breaker.evaluate_status(7, None, now=now)
        self.assertAlmostEqual(
            (backoff_7 - now).total_seconds(), 86400, delta=5
        )

    def test_eligibility_check_respects_backoff(self) -> None:
        now = datetime.now(timezone.utc)
        future_backoff = now + timedelta(hours=1)
        past_backoff = now - timedelta(minutes=5)

        self.assertFalse(self.circuit_breaker.is_eligible_to_poll(5, future_backoff, now=now))
        self.assertTrue(self.circuit_breaker.is_eligible_to_poll(5, past_backoff, now=now))
        self.assertTrue(self.circuit_breaker.is_eligible_to_poll(0, None, now=now))


if __name__ == "__main__":
    unittest.main()
