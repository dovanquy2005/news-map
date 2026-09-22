"""Structured JSON logging and secret redaction filter.

Strictly complies with:
- AGENTS.md (Logging, Secrets management)
- docs/10-security.md (Secrets leakage defense)
- docs/12-observability.md (Structured logging)
- tasks/TASK-010-observability-foundation.md
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict

# Patterns for sensitive values that must be redacted from logs
REDACTION_PATTERNS = [
    re.compile(r'(?i)(password|secret|token|api[_-]?key|jwt|authorization)["\s:=]+["\']?([^"\'\s,;]+)', re.IGNORECASE),
    re.compile(r'(?i)(bearer\s+)([A-Za-z0-9\-\._~\+\/]+=*)', re.IGNORECASE),
    re.compile(r'(?i)(postgres(ql)?:\/\/[^:]+:)([^@]+)(@)', re.IGNORECASE),
]


class SecretMaskingFilter(logging.Filter):
    """Intercepts and masks confidential credentials from log messages."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.mask_secrets(record.msg)
        if record.args and isinstance(record.args, tuple):
            record.args = tuple(
                self.mask_secrets(arg) if isinstance(arg, str) else arg
                for arg in record.args
            )
        return True

    @classmethod
    def mask_secrets(cls, text: str) -> str:
        """Redact sensitive keys and passwords with [REDACTED]."""
        masked = text
        for pattern in REDACTION_PATTERNS:
            if "bearer" in pattern.pattern.lower():
                masked = pattern.sub(r"\1[REDACTED]", masked)
            elif "postgres" in pattern.pattern.lower():
                masked = pattern.sub(r"\1******\4", masked)
            else:
                masked = pattern.sub(r"\1=******", masked)
        return masked


class JSONLogFormatter(logging.Formatter):
    """Serializes log records to structured single-line JSON format."""

    def __init__(self, service_name: str = "news-map-backend"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include request_id if available on record or context
        req_id = getattr(record, "request_id", None)
        if req_id:
            log_entry["request_id"] = req_id

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_structured_logging(service_name: str = "news-map-backend", log_level: str = "INFO") -> None:
    """Configure root logger with SecretMaskingFilter and JSONLogFormatter."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicate log outputs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONLogFormatter(service_name=service_name))
    console_handler.addFilter(SecretMaskingFilter())

    root_logger.addHandler(console_handler)
