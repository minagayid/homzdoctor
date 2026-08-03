"""Small liveness tests; authenticated workflow tests live in test_api_contracts."""

import unittest

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
