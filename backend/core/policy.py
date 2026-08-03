"""Small, dependency-free policy checks shared by the API and tests."""

from __future__ import annotations

from typing import Any, Mapping

from core.file_storage import UploadValidationError

_SUPPORTED_UPLOAD_EXTENSIONS = {
    ".dcm",
    ".dicom",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".pdf",
    ".nii",
    ".nii.gz",
}
_PATIENT_EDITABLE_FIELDS = {"record_type", "file_path"}
_CLINICAL_FIELDS = {
    "findings",
    "diagnosis",
    "confidence_score",
    "doctor_reviewed",
    "doctor_notes",
    "status",
    "file_metadata",
}


def registration_role(requested_role: Any) -> str:
    """Return the only role that public self-registration may create."""
    role = str(requested_role or "patient").strip().lower()
    if role != "patient":
        raise ValueError("Public registration can only create patient accounts")
    return role


def validate_upload_name(filename: str) -> str:
    """Validate an upload's extension and reject path-like names."""
    name = (filename or "").strip()
    if not name or name in {".", ".."} or "/" in name or "\\" in name:
        raise UploadValidationError("Upload filename must be a plain filename")

    lowered = name.lower()
    extension = ".nii.gz" if lowered.endswith(".nii.gz") else "." + lowered.rsplit(".", 1)[-1]
    if "." not in name or extension not in _SUPPORTED_UPLOAD_EXTENSIONS:
        raise UploadValidationError("Unsupported medical file type")
    return extension


def validate_record_update(
    updates: Mapping[str, Any], *, doctor_reviewed: bool
) -> dict[str, Any]:
    """Allow patients to edit intake metadata, never clinician conclusions."""
    clean = dict(updates)
    unknown = set(clean) - (_PATIENT_EDITABLE_FIELDS | _CLINICAL_FIELDS)
    if unknown:
        raise ValueError(f"Unsupported medical record fields: {sorted(unknown)}")
    if doctor_reviewed and set(clean) & _CLINICAL_FIELDS:
        raise ValueError("Clinician-reviewed findings can only be changed by a doctor")
    if not doctor_reviewed and set(clean) & _CLINICAL_FIELDS:
        raise ValueError("Clinical findings are written by the analysis/review workflow")
    if clean.get("file_path"):
        validate_upload_name(str(clean["file_path"]))
    return {key: clean[key] for key in clean if key in _PATIENT_EDITABLE_FIELDS}
