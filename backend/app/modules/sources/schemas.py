"""Source domain Pydantic schemas and validation rules."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional
from uuid import UUID
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator

DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$"
)


class SourceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Publisher name")
    domain: str = Field(..., max_length=150, description="Publisher FQDN domain")
    source_type: str = Field(default="RSS", max_length=50, description="RSS, SITEMAP, API, CRAWLER")
    rss_url: Optional[str] = Field(None, max_length=500, description="Feed HTTPS endpoint")
    parser_type: str = Field(default="RSS", max_length=50, description="Parser adapter type")
    priority: int = Field(default=50, ge=1, le=100, description="Priority weight (1-100)")
    rate_limit_rpm: int = Field(default=60, ge=1, le=600, description="Max requests per minute")
    terms_url: Optional[str] = Field(None, max_length=500, description="Terms of service URL")

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if not DOMAIN_REGEX.match(v_clean):
            raise ValueError(f"Invalid FQDN domain: {v}")
        if v_clean in ("localhost", "127.0.0.1", "0.0.0.0"):
            raise ValueError("Localhost or IP addresses are not permitted as source domains")
        return v_clean

    @field_validator("rss_url")
    @classmethod
    def validate_rss_url(cls, v: Optional[str], info) -> Optional[str]:
        if not v:
            return None
        v_clean = v.strip()
        parsed = urlparse(v_clean)
        if parsed.scheme != "https":
            raise ValueError("RSS URL must use secure HTTPS scheme")
        if not parsed.netloc:
            raise ValueError("RSS URL must have a valid network host")
        return v_clean


class SourceCreateRequest(SourceBase):
    active: bool = Field(default=True, description="Initial active status")


class SourceUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    rss_url: Optional[str] = Field(None, max_length=500)
    parser_type: Optional[str] = Field(None, max_length=50)
    priority: Optional[int] = Field(None, ge=1, le=100)
    rate_limit_rpm: Optional[int] = Field(None, ge=1, le=600)
    terms_url: Optional[str] = Field(None, max_length=500)
    active: Optional[bool] = None


class SourceToggleRequest(BaseModel):
    active: bool = Field(..., description="Target active status")


class SourceResponse(BaseModel):
    id: UUID
    name: str
    domain: str
    source_type: str
    rss_url: Optional[str] = None
    parser_type: str = "RSS"
    active: bool
    priority: int
    rate_limit_rpm: int = 60
    terms_url: Optional[str] = None
    last_success_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SourceListResponse(BaseModel):
    data: list[SourceResponse]
    count: int
