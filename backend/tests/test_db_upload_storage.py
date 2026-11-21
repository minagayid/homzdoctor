"""Database-backed upload storage (serverless mode) keeps the same contract."""

import os
import tempfile
import unittest
from pathlib import Path

_db_path = Path(tempfile.gettempdir()) / "homzdoctor-dbstorage-tests.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_db_path.as_posix()}"
os.environ["DEBUG"] = "false"
os.environ["ENVIRONMENT"] = "test"
os.environ["UPLOAD_STORAGE"] = "database"
_db_path.unlink(missing_ok=True)

from fastapi.testclient import TestClient

from main import app
from core.config import settings

settings.UPLOAD_STORAGE = "database"


def _png_bytes() -> bytes:
    # 1x1 transparent PNG
    import base64

    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )


class DatabaseStorageTests(unittest.TestCase):
    def test_upload_record_and_reanalyze_from_database(self):
        with TestClient(app) as client:
            email = "dbstore-patient@example.com"
            password = "Long-Test-Passphrase-123!"
            r = client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": "Db Store"})
            self.assertIn(r.status_code, (200, 201, 409), r.text)
            login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
            self.assertEqual(login.status_code, 200, login.text)
            token = login.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            record = client.post(
                "/api/v1/medical/records",
                json={"recordType": "xray"},
                headers=headers,
            )
            self.assertIn(record.status_code, (200, 201), record.text)
            record_id = record.json()["id"]

            upload = client.post(
                f"/api/v1/medical/records/{record_id}/upload",
                files={"file": ("chest.png", _png_bytes(), "image/png")},
                headers=headers,
            )
            self.assertEqual(upload.status_code, 200, upload.text)
            stored_name = upload.json()["filePath"].split("/", 1)[1]
            self.assertRegex(stored_name, r"^[0-9a-f]{32}\.png$")
            self.assertFalse(Path("uploads", stored_name).exists(), "database mode must not write to disk")

            analyze = client.post("/api/v1/ai/analyze", json={"record_id": record_id}, headers=headers)
            self.assertEqual(analyze.status_code, 200, analyze.text)
            self.assertIn("analysisId", analyze.json())

            delete = client.delete(f"/api/v1/medical/records/{record_id}", headers=headers)
            self.assertEqual(delete.status_code, 204, delete.text)

            again = client.post("/api/v1/ai/analyze", json={"record_id": record_id}, headers=headers)
            self.assertEqual(again.status_code, 404)

    def test_invalid_extension_rejected(self):
        with TestClient(app) as client:
            email = "dbstore-ext@example.com"
            password = "Long-Test-Passphrase-123!"
            client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": "Db Ext"})
            login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
            headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
            record = client.post("/api/v1/medical/records", json={"recordType": "xray"}, headers=headers)
            record_id = record.json()["id"]
            upload = client.post(
                f"/api/v1/medical/records/{record_id}/upload",
                files={"file": ("evil.sh", b"#!/bin/sh\n", "application/x-sh")},
                headers=headers,
            )
            self.assertEqual(upload.status_code, 400)


if __name__ == "__main__":
    unittest.main()
