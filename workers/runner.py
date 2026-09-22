"""Asynchronous worker process runner and supervisor.

Strictly complies with:
- docs/02-system-architecture.md (Async Workers, Scaling strategy)
- docs/03-backend-architecture.md (Worker modular boundaries)
- tasks/TASK-007-worker-runtime-foundation.md
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from typing import Callable, Dict, List, Optional

from backend.app.common.db import get_db_session
from backend.app.common.queue import JobPayload, QueueManager, QueueName
from workers.clustering.handler import handle_clustering_job
from workers.extraction.handler import handle_extraction_job
from workers.geocoding.handler import handle_geocoding_job
from workers.ingestion.handler import handle_ingestion_job
from workers.summarization.handler import handle_summarization_job

logger = logging.getLogger("news_map.worker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s")


class WorkerRunner:
    """Manages consumer loops, graceful shutdowns, and job transaction lifecycles."""

    def __init__(self, queue_manager: Optional[QueueManager] = None):
        self.queue_manager = queue_manager or QueueManager()
        self.handlers: Dict[QueueName, Callable[[JobPayload], bool]] = {}
        self._running = False

        # Register default handlers for named queues
        self.register_handler(QueueName.INGESTION, handle_ingestion_job)
        self.register_handler(QueueName.EXTRACTION, handle_extraction_job)
        self.register_handler(QueueName.GEOCODING, handle_geocoding_job)
        self.register_handler(QueueName.CLUSTERING, handle_clustering_job)
        self.register_handler(QueueName.SUMMARY, handle_summarization_job)

    def register_handler(
        self, queue_name: QueueName, handler: Callable[[JobPayload], bool]
    ) -> None:
        """Associate a queue with its designated execution handler."""
        self.handlers[queue_name] = handler

    def stop(self) -> None:
        """Signal the runner to cease polling and initiate graceful termination."""
        logger.info("Graceful shutdown initiated. Completing in-flight jobs...")
        self._running = False

    def process_one(self, queue_name: QueueName, timeout_seconds: int = 0) -> bool:
        """Fetch and execute a single job from the specified queue.

        Returns True if a job was dequeued and processed, False otherwise.
        """
        handler = self.handlers.get(queue_name)
        if not handler:
            logger.error("No handler registered for queue %s", queue_name.value)
            return False

        job = self.queue_manager.dequeue(queue_name, timeout_seconds=timeout_seconds)
        if not job:
            return False

        logger.info("Executing job %s from %s", job.job_id, queue_name.value)
        try:
            # Execute within transaction lifecycle guard
            with get_db_session() as session:
                success = handler(job)
                if not success:
                    raise RuntimeError("Handler returned failure status")
            logger.info("Job %s completed successfully", job.job_id)
            return True
        except Exception as exc:
            logger.warning("Job %s failed execution: %s", job.job_id, exc)
            self.queue_manager.retry(queue_name, job, error=exc)
            return False

    def run_loop(self, queues: List[QueueName], poll_interval: float = 0.5) -> None:
        """Continuously poll registered queues until stopped."""
        self._running = True

        def _sig_handler(signum, frame):
            logger.info("Received termination signal (%s)", signum)
            self.stop()

        # Attach signal handlers if supported on host OS
        try:
            signal.signal(signal.SIGINT, _sig_handler)
            signal.signal(signal.SIGTERM, _sig_handler)
        except (ValueError, AttributeError):
            pass

        logger.info(
            "Worker runner started. Monitoring queues: %s",
            [q.value for q in queues],
        )

        while self._running:
            processed_any = False
            for q in queues:
                if not self._running:
                    break
                if self.process_one(q, timeout_seconds=0):
                    processed_any = True

            if not processed_any and self._running:
                time.sleep(poll_interval)

        logger.info("Worker runner stopped cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Vietnam News Map Worker Runner CLI")
    parser.add_argument(
        "--queue",
        choices=["ingestion", "extraction", "geocoding", "clustering", "summary"],
        help="Run worker for a specific named queue",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run combined worker for all pipeline queues",
    )

    args = parser.parse_args()
    runner = WorkerRunner()

    name_mapping = {
        "ingestion": QueueName.INGESTION,
        "extraction": QueueName.EXTRACTION,
        "geocoding": QueueName.GEOCODING,
        "clustering": QueueName.CLUSTERING,
        "summary": QueueName.SUMMARY,
    }

    if args.queue:
        target_queues = [name_mapping[args.queue]]
    elif args.all:
        target_queues = list(name_mapping.values())
    else:
        parser.print_help()
        sys.exit(1)

    runner.run_loop(target_queues)


if __name__ == "__main__":
    main()
