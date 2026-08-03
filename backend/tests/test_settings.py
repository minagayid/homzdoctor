"""Configuration safety contracts."""

import unittest

from core.config import Settings


class SettingsTests(unittest.TestCase):
    def test_production_rejects_the_default_secret(self):
        with self.assertRaises(ValueError):
            Settings(
                _env_file=None,
                ENVIRONMENT="production",
                SECRET_KEY="homzdoctor-local-development-key-change-me",
            )

    def test_local_allowed_origins_are_parsed_without_wildcard_credentials(self):
        settings = Settings(
            _env_file=None,
            ENVIRONMENT="local",
            ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8000",
        )
        self.assertEqual(settings.allowed_origins, ["http://localhost:3000", "http://localhost:8000"])


if __name__ == "__main__":
    unittest.main()
