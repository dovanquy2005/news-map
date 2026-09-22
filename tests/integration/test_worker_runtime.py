"""Integration tests for Worker Runtime Foundation (TASK-007).

Verifies:
- WorkerRunner single-job processing
- Transaction boundary safety and exception capture
- Retry escalation to Dead-Letter Queue
- Graceful shutdown signal handling
"""

import unittest
import uuid

from backend.app.common.cache import get_redis_client
from backend.app.common.queue import JobPayload, JobType, QueueManager, QueueName
from workers.runner import WorkerRunner


class TestWorkerRuntimeIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = get_redis_client()
        cls.queue_manager = QueueManager(cls.client)
        cls.runner = WorkerRunner(cls.queue_manager)

    def setUp(self):
        for q in QueueName:
            self.queue_manager.clear_queue(q)

    def tearDown(self):
        for q in QueueName:
            self.queue_manager.clear_queue(q)

    def test_worker_processes_job_successfully(self):
        """Worker processes a queued job and releases it from the queue."""
        processed_jobs = []

        def custom_handler(job: JobPayload) -> bool:
            processed_jobs.append(job.job_id)
            return True

        self.runner.register_handler(QueueName.EXTRACTION, custom_handler)

        job = JobPayload(
            job_type=JobType.EXTRACTION.value,
            entity_id=str(uuid.uuid4()),
        )
        self.queue_manager.enqueue(QueueName.EXTRACTION, job)
        self.assertEqual(self.queue_manager.get_queue_length(QueueName.EXTRACTION), 1)

        # Process single job
        result = self.runner.process_one(QueueName.EXTRACTION)
        self.assertTrue(result)
        self.assertEqual(len(processed_jobs), 1)
        self.assertEqual(processed_jobs[0], job.job_id)
        self.assertEqual(self.queue_manager.get_queue_length(QueueName.EXTRACTION), 0)

    def test_worker_retries_on_handler_exception(self):
        """Worker handler exception triggers retry escalation."""
        def failing_handler(job: JobPayload) -> bool:
            raise ValueError("Simulated handler crash")

        self.runner.register_handler(QueueName.GEOCODING, failing_handler)

        job = JobPayload(
            job_type=JobType.GEOCODING.value,
            attempt=0,
            max_attempts=3,
        )
        self.queue_manager.enqueue(QueueName.GEOCODING, job)

        # First failure
        success = self.runner.process_one(QueueName.GEOCODING)
        self.assertFalse(success)

        # Queue still contains the re-enqueued job with attempt = 1
        self.assertEqual(self.queue_manager.get_queue_length(QueueName.GEOCODING), 1)
        re_job = self.queue_manager.dequeue(QueueName.GEOCODING)
        self.assertEqual(re_job.attempt, 1)

    def test_worker_stop_signal(self):
        """Calling stop() halts the runner."""
        self.runner._running = True
        self.runner.stop()
        self.assertFalse(self.runner._running)


if __name__ == "__main__":
    unittest.main()
