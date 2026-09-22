"""Standardized asynchronous job envelope and queue specifications.

Strictly complies with:
- docs/03-backend-architecture.md (Workers, Idempotency)
- docs/05-ingestion-pipeline.md (Queue semantics)
- tasks/TASK-005-redis-queue-foundation.md
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class QueueName(str, Enum):
    """Dedicated Redis queue keys corresponding to distinct pipeline stages."""

    INGESTION = "vnm:queue:ingestion"
    EXTRACTION = "vnm:queue:extraction"
    GEOCODING = "vnm:queue:geocoding"
    CLUSTERING = "vnm:queue:clustering"
    SUMMARY = "vnm:queue:summary"
    DEAD_LETTER = "vnm:queue:dlq"


class JobType(str, Enum):
    """Pipeline processing job types."""

    INGESTION = "ingestion"
    EXTRACTION = "extraction"
    GEOCODING = "geocoding"
    CLUSTERING = "clustering"
    SUMMARY = "summary"


def _iso_utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class JobPayload:
    """Standardized asynchronous job envelope passed through Redis queues."""

    job_type: str
    entity_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attempt: int = 0
    max_attempts: int = 3
    created_at: str = field(default_factory=_iso_utcnow)
    scheduled_at: str = field(default_factory=_iso_utcnow)
    idempotency_key: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert job payload to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize job payload to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> JobPayload:
        """Construct a validated JobPayload from a dictionary."""
        return cls(
            job_type=str(data["job_type"]),
            entity_id=str(data["entity_id"]) if data.get("entity_id") is not None else None,
            payload=data.get("payload", {}),
            job_id=str(data.get("job_id", str(uuid.uuid4()))),
            attempt=int(data.get("attempt", 0)),
            max_attempts=int(data.get("max_attempts", 3)),
            created_at=str(data.get("created_at", _iso_utcnow())),
            scheduled_at=str(data.get("scheduled_at", _iso_utcnow())),
            idempotency_key=str(data["idempotency_key"]) if data.get("idempotency_key") else None,
            error_message=str(data["error_message"]) if data.get("error_message") else None,
        )

    @classmethod
    def from_json(cls, json_str: str) -> JobPayload:
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
