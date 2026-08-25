"""Small liveness tests; authenticated workflow tests live in test_api_contracts."""

import os
import tempfile
import unittest
from pathlib import Path

# Configure the isolated test database before importing the ASGI application.
_db_path = Path(tempfile.gettempdir()) / "homzdoctor-contract-tests.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_db_path.as_posix()}"
os.environ["DEBUG"] = "false"
os.environ["ENVIRONMENT"] = "test"
_db_path.unlink(missing_ok=True)

from fastapi.testclient import TestClient

from main import app


class APILivenessTests(unittest.TestCase):
    def test_root_endpoint(self):
        with TestClient(app) as client:
            response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "homzdoctor-api")

    def test_health_endpoint(self):
        with TestClient(app) as client:
            response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")


if __name__ == "__main__":
    unittest.main()
