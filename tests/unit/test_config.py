"""Unit tests for configuration management and secret security gates.

Verifies acceptance criteria of TASK-002:
- Local startup succeeds with defaults
- Fail-fast on malformed parameters
- Secret masking in repr, str, and logging dictionaries
- Production security gates block insecure defaults
- Frontend configuration template does not contain server-side secrets
"""

import unittest
from pathlib import Path

from backend.app.common.config import SecretStr, Settings, load_settings


class TestConfigManagement(unittest.TestCase):
    def test_secret_str_masking(self):
        """SecretStr must never expose raw plaintext via str() or repr()."""
        raw_secret = "super-secret-password-123"
        secret = SecretStr(raw_secret)

        self.assertEqual(str(secret), "******")
        self.assertEqual(repr(secret), "******")
        self.assertEqual(secret.get_secret_value(), raw_secret)
        self.assertNotIn(raw_secret, str(secret))
        self.assertNotIn(raw_secret, repr(secret))

    def test_local_settings_defaults(self):
        """Local settings load cleanly with safe defaults."""
        settings = load_settings(override_env={"APP_ENV": "local"})
        self.assertEqual(settings.app_env, "local")
        self.assertEqual(settings.port, 8000)
        self.assertEqual(settings.log_level, "INFO")
        self.assertIn("http://localhost:3000", settings.cors_allowed_origins)

        # Ensure secrets are masked in to_dict()
        masked_dict = settings.to_dict(mask_secrets=True)
        self.assertEqual(masked_dict["database_url"], "******")
        self.assertEqual(masked_dict["redis_url"], "******")
        self.assertEqual(masked_dict["admin_jwt_secret"], "******")

    def test_fail_fast_on_invalid_int(self):
        """Loading settings with non-numeric PORT must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            load_settings(override_env={"PORT": "not-a-number"})
        self.assertIn("Invalid integer configuration for 'PORT'", str(ctx.exception))

    def test_fail_fast_on_invalid_app_env(self):
        """Loading settings with unknown APP_ENV must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            load_settings(override_env={"APP_ENV": "invalid_environment"})
        self.assertIn("Invalid APP_ENV", str(ctx.exception))

    def test_production_blocks_default_admin_jwt_secret(self):
        """Production mode must reject default or insecure ADMIN_JWT_SECRET."""
        with self.assertRaises(ValueError) as ctx:
            load_settings(
                override_env={
                    "APP_ENV": "production",
                    "ADMIN_JWT_SECRET": "dev-insecure-admin-jwt-secret-change-in-production",
                    "DATABASE_URL": "postgresql://prod_user:StrongProdPass123!@db.prod:5432/news_map",
                    "REDIS_URL": "redis://redis.prod:6379/0",
                    "MAPS_SERVER_KEY": "AIzaSyProdServerKey1234567890",
                    "LLM_API_KEY": "AIzaSyProdLLMKey1234567890",
                }
            )
        self.assertIn("ADMIN_JWT_SECRET", str(ctx.exception))

    def test_production_blocks_default_database_password(self):
        """Production mode must reject default database credentials."""
        with self.assertRaises(ValueError) as ctx:
            load_settings(
                override_env={
                    "APP_ENV": "production",
                    "ADMIN_JWT_SECRET": "a-very-long-secure-random-production-secret-token-12345",
                    "DATABASE_URL": "postgresql://news_map:NewsMapDev_2026!@localhost:5432/news_map",
                    "REDIS_URL": "redis://redis.prod:6379/0",
                    "MAPS_SERVER_KEY": "AIzaSyProdServerKey1234567890",
                    "LLM_API_KEY": "AIzaSyProdLLMKey1234567890",
                }
            )
        self.assertIn("DATABASE_URL uses insecure or default credentials", str(ctx.exception))

    def test_production_succeeds_with_strong_secrets(self):
        """Production mode succeeds when all required secrets are strong and non-empty."""
        settings = load_settings(
            override_env={
                "APP_ENV": "production",
                "ADMIN_JWT_SECRET": "strong-production-admin-jwt-secret-with-high-entropy-67890",
                "DATABASE_URL": "postgresql://prod_user:VeryComplexPass999!@db.prod.internal:5432/news_map",
                "REDIS_URL": "rediss://:ComplexRedisPass999!@redis.prod.internal:6379/0",
                "MAPS_SERVER_KEY": "AIzaSyRealProductionServerKey123456",
                "LLM_API_KEY": "AIzaSyRealProductionLLMKey1234567890",
            }
        )
        self.assertEqual(settings.app_env, "production")

    def test_frontend_env_excludes_server_secrets(self):
        """frontend/.env.example must not expose server-side secrets."""
        frontend_env = Path(__file__).resolve().parent.parent.parent / "frontend" / ".env.example"
        self.assertTrue(frontend_env.is_file(), "frontend/.env.example must exist")
        content = frontend_env.read_text(encoding="utf-8")

        forbidden_keys = [
            "DATABASE_URL",
            "REDIS_URL",
            "MAPS_SERVER_KEY",
            "LLM_API_KEY",
            "ADMIN_JWT_SECRET",
        ]
        for key in forbidden_keys:
            # Must not have an active assignment e.g. KEY=...
            for line in content.splitlines():
                clean = line.strip()
                if not clean.startswith("#") and clean.startswith(f"{key}="):
                    self.fail(f"frontend/.env.example exposes forbidden server secret key: {key}")


if __name__ == "__main__":
    unittest.main()
