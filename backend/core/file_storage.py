"""Private local upload storage with conservative validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from core.policy_types import SUPPORTED_UPLOAD_EXTENSIONS


class UploadValidationError(ValueError):
    """Raised when a local upload cannot be safely stored."""


@dataclass(frozen=True)
class SavedUpload:
    path: Path
    extension: str
    size: int


def _extension(filename: str) -> str:
    name = (filename or "").strip()
    if not name or name in {".", ".."} or "/" in name or "\\" in name:
        raise UploadValidationError("Upload filename must be a plain filename")
    lowered = name.lower()
    extension = ".nii.gz" if lowered.endswith(".nii.gz") else "." + lowered.rsplit(".", 1)[-1]
    if "." not in name or extension not in SUPPORTED_UPLOAD_EXTENSIONS:
        raise UploadValidationError("Unsupported medical file type")
    return extension


class LocalFileStore:
    """Store uploads using generated names inside one private directory."""

    def __init__(self, root: Path, *, max_bytes: int = 100 * 1024 * 1024) -> None:
        self.root = Path(root).resolve()
        self.max_bytes = int(max_bytes)
        if self.max_bytes <= 0:
            raise ValueError("max_bytes must be positive")
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> SavedUpload:
        if len(content) > self.max_bytes:
            raise UploadValidationError("Upload exceeds the configured size limit")
        extension = _extension(filename)
        target = self.root / f"{uuid4().hex}{extension}"
        target.write_bytes(content)
        return SavedUpload(path=target, extension=extension, size=len(content))
