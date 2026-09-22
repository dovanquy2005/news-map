"""Centralized configuration and secret management.

Strictly complies with:
- AGENTS.md (Security by default, Logging)
- docs/10-security.md (Secrets management)
- docs/15-dev-conventions.md (Configuration conventions)
- docs/17-deployment.md (Environment strategy)
- tasks/TASK-002-environment-configuration.md
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

AppEnv = Literal["local", "staging", "production"]


class SecretStr:
    """A wrapper for secret values that prevents accidental exposure in logs and representations."""

    def __init__(self, value: str):
        self._value = str(value) if value is not None else ""

    def get_secret_value(self) -> str:
        """Return the raw secret value."""
        return self._value

    def __repr__(self) -> str:
        return "******"

    def __str__(self) -> str:
        return "******"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SecretStr):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False

    def __bool__(self) -> bool:
        return bool(self._value.strip())


def _load_env_file(filepath: Path) -> dict[str, str]:
    """Parse a simple key-value .env file without external dependencies."""
    env_vars: dict[str, str] = {}
    if not filepath.is_file():
        return env_vars

    content = filepath.read_text(encoding="utf-8")
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        # Remove surrounding quotes if present
        if len(val) >= 2 and (
            (val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'")
        ):
            val = val[1:-1]
        env_vars[key] = val
    return env_vars


@dataclass(frozen=True)
class Settings:
    """Application configuration schema with typed validation and secret masking."""

    # Server / Runtime Environment
    app_env: AppEnv = "local"
    port: int = 8000
    log_level: str = "INFO"
    cors_allowed_origins: list[str] = field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"]
    )

    # Database (PostgreSQL + PostGIS)
    database_url: SecretStr = field(
        default_factory=lambda: SecretStr("postgresql://news_map:NewsMapDev_2026!@localhost:5432/news_map")
    )
    db_pool_min: int = 5
    db_pool_max: int = 20
    db_timeout_ms: int = 5000

    # Redis Cache & Queue
    redis_url: SecretStr = field(default_factory=lambda: SecretStr("redis://localhost:6379/0"))
    redis_max_connections: int = 20

    # Maps API
    maps_browser_key: str = ""
    maps_server_key: SecretStr = field(default_factory=lambda: SecretStr(""))

    # LLM / AI Extraction
    llm_api_key: SecretStr = field(default_factory=lambda: SecretStr(""))
    llm_model_name: str = "gemini-1.5-flash"
    llm_timeout_ms: int = 30000
    llm_max_tokens: int = 2048

    # Rate Limiting
    rate_limit_anonymous_rps: int = 10
    rate_limit_search_rps: int = 5
    rate_limit_admin_rps: int = 20

    # Admin Authentication
    admin_jwt_secret: SecretStr = field(
        default_factory=lambda: SecretStr("dev-insecure-admin-jwt-secret-change-in-production")
    )
    admin_session_ttl_hours: int = 12

    def to_dict(self, mask_secrets: bool = True) -> dict[str, Any]:
        """Serialize configuration into a dictionary, optionally masking sensitive fields."""
        res: dict[str, Any] = {}
        for key, val in self.__dict__.items():
            if isinstance(val, SecretStr):
                res[key] = "******" if mask_secrets else val.get_secret_value()
            else:
                res[key] = val
        return res

    def validate_security(self) -> None:
        """Enforce strict fail-fast validation for production environments."""
        if self.app_env != "production":
            return

        insecure_patterns = [
            "dev-insecure",
            "change-in-production",
            "NewsMapDev_2026!",
            "example",
            "changeme",
        ]

        # 1. Admin JWT Secret validation
        jwt_val = self.admin_jwt_secret.get_secret_value()
        if not jwt_val or len(jwt_val) < 32:
            raise ValueError(
                "CRITICAL SECURITY FAILURE: ADMIN_JWT_SECRET must be at least 32 characters long in production."
            )
        for pattern in insecure_patterns:
            if pattern in jwt_val.lower():
                raise ValueError(
                    f"CRITICAL SECURITY FAILURE: ADMIN_JWT_SECRET contains insecure default keyword '{pattern}'."
                )

        # 2. Database credentials validation
        db_val = self.database_url.get_secret_value()
        if not db_val:
            raise ValueError("CRITICAL CONFIGURATION FAILURE: DATABASE_URL must not be empty in production.")
        db_val_lower = db_val.lower()
        for pattern in ["newsmapdev", ":password@", ":root@", ":admin@", "@localhost", "@127.0.0.1"]:
            if pattern in db_val_lower:
                raise ValueError(
                    f"CRITICAL SECURITY FAILURE: DATABASE_URL uses insecure or default credentials '{pattern}' in production."
                )

        # 3. Redis URL validation
        if not self.redis_url.get_secret_value():
            raise ValueError("CRITICAL CONFIGURATION FAILURE: REDIS_URL must not be empty in production.")

        # 4. Server-side Maps Key validation
        if not self.maps_server_key.get_secret_value():
            raise ValueError("CRITICAL CONFIGURATION FAILURE: MAPS_SERVER_KEY must not be empty in production.")

        # 5. LLM API Key validation
        if not self.llm_api_key.get_secret_value():
            raise ValueError("CRITICAL CONFIGURATION FAILURE: LLM_API_KEY must not be empty in production.")


def load_settings(env_file: Path | str | None = None, override_env: dict[str, str] | None = None) -> Settings:
    """Load, parse, and validate application settings from environment variables."""
    raw_env: dict[str, str] = {}

    # 1. Read from .env file if specified or default root/backend location exists
    search_paths = []
    if env_file:
        search_paths.append(Path(env_file))
    else:
        search_paths.extend(
            [
                Path(".env"),
                Path("backend/.env"),
                Path(__file__).resolve().parent.parent.parent / ".env",
            ]
        )

    for p in search_paths:
        if p.is_file():
            raw_env.update(_load_env_file(p))
            break

    # 2. Layer with os.environ
    raw_env.update(os.environ)

    # 3. Layer with direct overrides (e.g. for unit testing)
    if override_env:
        raw_env.update(override_env)

    # Helper converters
    def get_str(key: str, default: str) -> str:
        return raw_env.get(key, default).strip()

    def get_int(key: str, default: int) -> int:
        val = raw_env.get(key)
        if val is None or not val.strip():
            return default
        try:
            return int(val.strip())
        except ValueError:
            raise ValueError(f"Invalid integer configuration for '{key}': received '{val}'")

    def get_list(key: str, default: list[str]) -> list[str]:
        val = raw_env.get(key)
        if not val or not val.strip():
            return default
        return [item.strip() for item in val.split(",") if item.strip()]

    app_env_raw = get_str("APP_ENV", "local").lower()
    if app_env_raw not in ("local", "staging", "production"):
        raise ValueError(
            f"Invalid APP_ENV: '{app_env_raw}'. Must be one of: 'local', 'staging', 'production'."
        )
    app_env: AppEnv = app_env_raw  # type: ignore

    settings = Settings(
        app_env=app_env,
        port=get_int("PORT", 8000),
        log_level=get_str("LOG_LEVEL", "INFO").upper(),
        cors_allowed_origins=get_list(
            "CORS_ALLOWED_ORIGINS", ["http://localhost:3000", "http://localhost:5173"]
        ),
        database_url=SecretStr(
            get_str(
                "DATABASE_URL",
                "postgresql://news_map:NewsMapDev_2026!@localhost:5432/news_map",
            )
        ),
        db_pool_min=get_int("DB_POOL_MIN", 5),
        db_pool_max=get_int("DB_POOL_MAX", 20),
        db_timeout_ms=get_int("DB_TIMEOUT_MS", 5000),
        redis_url=SecretStr(get_str("REDIS_URL", "redis://localhost:6379/0")),
        redis_max_connections=get_int("REDIS_MAX_CONNECTIONS", 20),
        maps_browser_key=get_str("MAPS_BROWSER_KEY", ""),
        maps_server_key=SecretStr(get_str("MAPS_SERVER_KEY", "")),
        llm_api_key=SecretStr(get_str("LLM_API_KEY", "")),
        llm_model_name=get_str("LLM_MODEL_NAME", "gemini-1.5-flash"),
        llm_timeout_ms=get_int("LLM_TIMEOUT_MS", 30000),
        llm_max_tokens=get_int("LLM_MAX_TOKENS", 2048),
        rate_limit_anonymous_rps=get_int("RATE_LIMIT_ANONYMOUS_RPS", 10),
        rate_limit_search_rps=get_int("RATE_LIMIT_SEARCH_RPS", 5),
        rate_limit_admin_rps=get_int("RATE_LIMIT_ADMIN_RPS", 20),
        admin_jwt_secret=SecretStr(
            get_str(
                "ADMIN_JWT_SECRET",
                "dev-insecure-admin-jwt-secret-change-in-production",
            )
        ),
        admin_session_ttl_hours=get_int("ADMIN_SESSION_TTL_HOURS", 12),
    )

    settings.validate_security()
    return settings


_CACHED_SETTINGS: Settings | None = None


def get_settings() -> Settings:
    """Retrieve application settings singleton."""
    global _CACHED_SETTINGS
    if _CACHED_SETTINGS is None:
        _CACHED_SETTINGS = load_settings()
    return _CACHED_SETTINGS


def reset_settings() -> None:
    """Reset cached singleton (primarily used for unit testing)."""
    global _CACHED_SETTINGS
    _CACHED_SETTINGS = None
