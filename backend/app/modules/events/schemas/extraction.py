"""Pydantic extraction schema and validated extraction DTO."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.modules.events.schemas.categories import EventCategory


class EntityType(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    VEHICLE = "VEHICLE"
    OTHER = "OTHER"


class EntityItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    type: EntityType = EntityType.OTHER

    @field_validator("type", mode="before")
    @classmethod
    def parse_type(cls, v: str) -> EntityType:
        if isinstance(v, EntityType):
            return v
        try:
            return EntityType(str(v).strip().upper())
        except ValueError:
            return EntityType.OTHER


class EventExtractionSchema(BaseModel):
    """Raw extraction schema expected from LLM output."""

    event_title: str = Field(..., min_length=10, max_length=300)
    event_type: EventCategory = Field(default=EventCategory.OTHER)
    is_event: bool = True
    location_text: Optional[str] = Field(None, max_length=500)
    province: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    ward: Optional[str] = Field(None, max_length=100)
    occurred_at: Optional[datetime] = None
    facts: list[str] = Field(default_factory=list)
    entities: list[EntityItem] = Field(default_factory=list)
    uncertainty_notes: Optional[str] = Field(None, max_length=1000)
    extraction_confidence: float = Field(default=0.5, ge=0.0, le=1.0)

    @field_validator("event_type", mode="before")
    @classmethod
    def parse_event_type(cls, v: str) -> EventCategory:
        return EventCategory.from_string(str(v))

    @field_validator("facts")
    @classmethod
    def limit_facts(cls, v: list[str]) -> list[str]:
        # Limit to max 10 facts per PRD
        return [f.strip() for f in v if f and f.strip()][:10]

    model_config = ConfigDict(extra="ignore")


class ValidatedExtractionDTO(BaseModel):
    """Sanitized, domain-checked extraction ready for downstream geocoding & clustering."""

    event_title: str
    event_type: EventCategory
    is_event: bool
    location_text: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None
    occurred_at: Optional[datetime] = None
    facts: list[str] = Field(default_factory=list)
    entities: list[EntityItem] = Field(default_factory=list)
    uncertainty_notes: Optional[str] = None
    extraction_confidence: float

    model_config = ConfigDict(from_attributes=True)
