"""Integration tests for the local safety and ownership boundaries."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from io import BytesIO

from PIL import Image

# Configure an isolated SQLite file before importing the application settings.
_db_path = Path(tempfile.gettempdir()) / "homzdoctor-contract-tests.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_db_path.as_posix()}"
os.environ["DEBUG"] = "false"
os.environ["ENVIRONMENT"] = "test"

from fastapi.testclient import TestClient

from main import app


class APIContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)
        try:
            _db_path.unlink()
        except FileNotFoundError:
            pass

    def _register_and_login(self, email: str) -> dict[str, str]:
        registered = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "fullName": "Local Patient",
                "password": "patient-password",
            },
        )
        self.assertEqual(registered.status_code, 201, registered.text)
        login = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "patient-password"},
        )
        self.assertEqual(login.status_code, 200, login.text)
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    def test_registration_cannot_create_a_doctor_account(self):
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": "self-appointed@example.test",
                "fullName": "Untrusted User",
                "password": "patient-password",
                "role": "doctor",
            },
        )
        self.assertIn(response.status_code, (400, 403, 422))

    def test_medical_upload_requires_authentication_and_persists_bytes(self):
        unauthenticated = self.client.post(
            "/api/v1/medical/records/1/upload",
            files={"file": ("scan.png", b"not-a-real-image", "image/png")},
        )
        self.assertEqual(unauthenticated.status_code, 401)

        headers = self._register_and_login("upload-owner@example.test")
        record = self.client.post(
            "/api/v1/medical/records",
            headers=headers,
            json={"recordType": "lab_report", "filePath": ""},
        )
        self.assertEqual(record.status_code, 201, record.text)
        record_id = record.json()["id"]

        uploaded = self.client.post(
            f"/api/v1/medical/records/{record_id}/upload",
            headers=headers,
            files={"file": ("report.pdf", b"local report bytes", "application/pdf")},
        )
        self.assertEqual(uploaded.status_code, 200, uploaded.text)
        payload = uploaded.json()
        self.assertEqual(payload["size"], len(b"local report bytes"))
        self.assertTrue(payload["filePath"].endswith(".pdf"))

    def test_patient_cannot_create_or_approve_prescriptions(self):
        headers = self._register_and_login("prescription-patient@example.test")
        created = self.client.post(
            "/api/v1/prescriptions",
            headers=headers,
            json={"patientId": 1, "recordId": 1, "medications": []},
        )
        self.assertEqual(created.status_code, 403)

        approved = self.client.put("/api/v1/prescriptions/1/approve", headers=headers)
        self.assertEqual(approved.status_code, 403)

    def test_private_adherence_and_escalation_endpoints_require_authentication(self):
        adherence = self.client.get("/api/v1/adherence/patient/1")
        escalation = self.client.post("/api/v1/escalation/check", json={"symptoms": []})
        self.assertEqual(adherence.status_code, 401)
        self.assertEqual(escalation.status_code, 401)

    def test_ai_upload_creates_a_reviewable_persistent_analysis(self):
        headers = self._register_and_login("analysis-owner@example.test")
        image = BytesIO()
        Image.new("RGB", (4, 4), color=(20, 30, 40)).save(image, format="PNG")
        response = self.client.post(
            "/api/v1/ai/diagnose",
            headers=headers,
            files={"file": ("scan.png", image.getvalue(), "image/png")},
            data={"modality": "xray"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertIsInstance(payload["analysisId"], str)
        self.assertTrue(payload["doctorReviewRequired"])

        stored = self.client.get(
            f"/api/v1/ai/results/{payload['analysisId']}", headers=headers
        )
        self.assertEqual(stored.status_code, 200, stored.text)
        self.assertEqual(stored.json()["analysisId"], payload["analysisId"])

    def test_patient_record_intake_cannot_write_clinical_conclusions(self):
        headers = self._register_and_login("intake-owner@example.test")
        response = self.client.post(
            "/api/v1/medical/records",
            headers=headers,
            json={
                "recordType": "lab_report",
                "filePath": "",
                "findings": "patient supplied conclusion",
                "diagnosis": "patient supplied diagnosis",
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        self.assertIsNone(response.json()["findings"])
        self.assertIsNone(response.json()["diagnosis"])

    def test_record_path_cannot_escape_private_upload_storage(self):
        headers = self._register_and_login("path-owner@example.test")
        response = self.client.post(
            "/api/v1/medical/records",
            headers=headers,
            json={"recordType": "lab_report", "filePath": "../../outside.pdf"},
        )
        self.assertEqual(response.status_code, 400)

    def test_doctor_review_is_required_before_prescription_creation(self):
        patient_headers = self._register_and_login("review-patient@example.test")
        patient = self.client.get("/api/v1/auth/me", headers=patient_headers).json()
        record = self.client.post(
            "/api/v1/medical/records",
            headers=patient_headers,
            json={"recordType": "xray", "filePath": ""},
        ).json()
        before_review = self.client.post(
            "/api/v1/prescriptions",
            headers={
                "Authorization": f"Bearer {self.client.post('/api/v1/auth/login', json={'email': 'dr.demo@homzdoctor.app', 'password': 'demodoctor'}).json()['access_token']}"
            },
            json={"patientId": patient["id"], "recordId": record["id"], "medications": []},
        )
        self.assertEqual(before_review.status_code, 409)

        doctor_login = self.client.post(
            "/api/v1/auth/login",
            json={"email": "dr.demo@homzdoctor.app", "password": "demodoctor"},
        )
        doctor_headers = {"Authorization": f"Bearer {doctor_login.json()['access_token']}"}
        reviewed = self.client.post(
            f"/api/v1/doctors/review/{record['id']}",
            headers=doctor_headers,
            json={"action": "approve", "findings": "Clinician review pending final care plan."},
        )
        self.assertEqual(reviewed.status_code, 200, reviewed.text)

        created = self.client.post(
            "/api/v1/prescriptions",
            headers=doctor_headers,
            json={
                "patientId": patient["id"],
                "recordId": record["id"],
                "medications": [{"name": "Example medication", "dose": "as prescribed"}],
            },
        )
        self.assertEqual(created.status_code, 201, created.text)
        approved = self.client.put(
            f"/api/v1/prescriptions/{created.json()['id']}/approve",
            headers=doctor_headers,
        )
        self.assertEqual(approved.status_code, 200, approved.text)
        self.assertTrue(approved.json()["approved"])


if __name__ == "__main__":
    unittest.main()
