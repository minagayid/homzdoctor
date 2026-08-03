"""Tests for the local-first safety and storage contracts."""

import tempfile
import unittest
from pathlib import Path

from core.file_storage import LocalFileStore, UploadValidationError
from core.policy import (
    registration_role,
    validate_record_update,
    validate_upload_name,
)


class LocalPolicyTests(unittest.TestCase):
    def test_public_registration_cannot_self_assign_a_privileged_role(self):
        with self.assertRaises(ValueError):
            registration_role("doctor")
        with self.assertRaises(ValueError):
            registration_role("admin")
        self.assertEqual(registration_role(None), "patient")

    def test_upload_names_allow_supported_medical_inputs_without_paths(self):
        self.assertEqual(validate_upload_name("scan.nii.gz"), ".nii.gz")
        self.assertEqual(validate_upload_name("report.PDF"), ".pdf")
        with self.assertRaises(UploadValidationError):
            validate_upload_name("..\\private\\patient.pdf")
        with self.assertRaises(UploadValidationError):
            validate_upload_name("patient.exe")

    def test_patient_cannot_edit_clinician_findings_or_diagnosis(self):
        with self.assertRaises(ValueError):
            validate_record_update({"diagnosis": "new conclusion"}, doctor_reviewed=True)
        with self.assertRaises(ValueError):
            validate_record_update({"findings": "new findings"}, doctor_reviewed=True)
        self.assertEqual(
            validate_record_update({"file_path": "new-file.pdf"}, doctor_reviewed=False),
            {"file_path": "new-file.pdf"},
        )


class LocalFileStoreTests(unittest.TestCase):
    def test_upload_is_saved_under_a_generated_name_and_can_be_read_back(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalFileStore(Path(temp_dir), max_bytes=32)
            saved = store.save("patient.pdf", b"safe local content")

            self.assertTrue(saved.path.exists())
            self.assertNotEqual(saved.path.name, "patient.pdf")
            self.assertEqual(saved.path.read_bytes(), b"safe local content")
            self.assertEqual(saved.extension, ".pdf")

    def test_upload_size_limit_is_enforced_before_writing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalFileStore(Path(temp_dir), max_bytes=4)
            with self.assertRaises(UploadValidationError):
                store.save("scan.png", b"too large")
            self.assertEqual(list(Path(temp_dir).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
