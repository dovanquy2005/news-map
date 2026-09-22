"""Generic base repository providing parameterized CRUD operations.

Strictly complies with:
- AGENTS.md (Security by default, no raw SQL concatenation)
- docs/04-data-architecture.md
- tasks/TASK-004-database-entities-repositories.md
"""

from __future__ import annotations

import uuid
from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.common.db.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic repository providing baseline CRUD operations using parameterized ORM statements."""

    def __init__(self, model_class: Type[T], session: Session):
        self.model_class = model_class
        self.session = session

    def get_by_id(self, entity_id: uuid.UUID | str) -> Optional[T]:
        """Fetch a single record by its primary key ID."""
        if isinstance(entity_id, str):
            entity_id = uuid.UUID(entity_id)
        stmt = select(self.model_class).where(self.model_class.id == entity_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list(self, limit: int = 100, offset: int = 0) -> List[T]:
        """List records with explicit bounds to prevent unconstrained queries."""
        clamped_limit = max(1, min(limit, 500))
        clamped_offset = max(0, offset)
        stmt = select(self.model_class).limit(clamped_limit).offset(clamped_offset)
        return list(self.session.execute(stmt).scalars().all())

    def create(self, instance: T) -> T:
        """Persist a new entity instance."""
        self.session.add(instance)
        self.session.flush()
        return instance

    def update(self, instance: T) -> T:
        """Flush changes to an existing entity instance."""
        self.session.flush()
        return instance

    def delete(self, instance: T) -> None:
        """Remove an entity instance from the database."""
        self.session.delete(instance)
        self.session.flush()
