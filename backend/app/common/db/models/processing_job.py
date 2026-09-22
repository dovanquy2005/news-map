"""ProcessingJob entity model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.common.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ProcessingJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Background processing queue and task execution audit ledger."""

    __tablename__ = "processing_jobs"

    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), nullable=True)

    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_processing_jobs_type_status_sched", "job_type", "status", "scheduled_at"),
    )
