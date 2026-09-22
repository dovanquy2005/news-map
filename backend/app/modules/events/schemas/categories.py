"""Standardized event category enumerations according to PRD 7.1."""

from __future__ import annotations

from enum import Enum


class EventCategory(str, Enum):
    ACCIDENT = "ACCIDENT"
    FIRE = "FIRE"
    CRIME = "CRIME"
    PUBLIC_SAFETY = "PUBLIC_SAFETY"
    WEATHER = "WEATHER"
    FLOOD = "FLOOD"
    TRAFFIC = "TRAFFIC"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    PUBLIC_EVENT = "PUBLIC_EVENT"
    POLITICS = "POLITICS"
    BUSINESS = "BUSINESS"
    HEALTH = "HEALTH"
    EDUCATION = "EDUCATION"
    ENTERTAINMENT = "ENTERTAINMENT"
    SPORTS = "SPORTS"
    OTHER = "OTHER"

    @classmethod
    def from_string(cls, val: str) -> EventCategory:
        """Safe parsing with fallback to OTHER."""
        if not val:
            return cls.OTHER
        clean = val.strip().upper()
        try:
            return cls(clean)
        except ValueError:
            return cls.OTHER
