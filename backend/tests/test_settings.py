"""Configuration safety contracts for local and production settings."""

import unittest

from core.config import Settings


class SettingsTests(unittest.TestCase):
    def _valid_production_settings(self, **overrides):
        values = {
            "ENVIRONMENT": "production",
            "DEBUG": False,
            "SECRET_KEY": "unique-production-signing-secret-" + "x" * 24,
            "DATABASE_URL": "postgresql+asyncpg://appuser:encoded-password@localhost:5432/homzdoctor",
            "ALLOWED_ORIGINS": "https://homzdoctor-web.example.run.app",
            "SEED_DEMO_DATA": False,
        }
        values.update(overrides)
        return Settings(_env_file=None, **values)

    def test_production_rejects_the_default_secret(self):
        with self.assertRaises(ValueError):
            self._valid_production_settings(
                SECRET_KEY="homzdoctor-local-development-key-change-me",
            )

    def test_production_rejects_documented_example_secret(self):
        with self.assertRaises(ValueError):
            self._valid_production_settings(
                SECRET_KEY="change-this-local-development-secret",
            )

    def test_production_rejects_demo_seeding(self):
        with self.assertRaisesRegex(ValueError, "must not seed demo"):
            self._valid_production_settings(SEED_DEMO_DATA=True)

    def test_production_rejects_sqlite(self):
        with self.assertRaisesRegex(ValueError, "PostgreSQL"):
            self._valid_production_settings(DATABASE_URL="sqlite+aiosqlite:///./homzdoctor.db")

    def test_production_rejects_debug_and_wildcard_or_http_origins(self):
        with self.assertRaisesRegex(ValueError, "DEBUG"):
            self._valid_production_settings(DEBUG=True)
        with self.assertRaisesRegex(ValueError, "ALLOWED_ORIGINS"):
            self._valid_production_settings(ALLOWED_ORIGINS="*")
        with self.assertRaisesRegex(ValueError, "HTTPS origin"):
            self._valid_production_settings(ALLOWED_ORIGINS="http://localhost:3000")

    def test_production_accepts_postgres_strong_secret_and_explicit_https_origin(self):
        configured = self._valid_production_settings()
        self.assertTrue(configured.is_production)
        self.assertFalse(configured.is_sqlite)
        self.assertEqual(configured.allowed_origins, ["https://homzdoctor-web.example.run.app"])
        self.assertFalse(configured.SEED_DEMO_DATA)

    def test_local_allowed_origins_are_parsed_for_development(self):
        settings = Settings(
            _env_file=None,
            ENVIRONMENT="local",
            ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8000",
        )
        self.assertEqual(settings.allowed_origins, ["http://localhost:3000", "http://localhost:8000"])


if __name__ == "__main__":
    unittest.main()
