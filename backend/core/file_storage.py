"""Private local upload storage with conservative validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
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


def is_generated_name(filename: str) -> bool:
    """True only for names this system generated (uuid4 hex + supported extension)."""
    if not isinstance(filename, str) or "/" in filename or "\\" in filename:
        return False
    extension = next(
        (ext for ext in sorted(SUPPORTED_UPLOAD_EXTENSIONS, key=len, reverse=True) if filename.endswith(ext)),
        None,
    )
    if extension is None:
        return False
    file_id = filename[: -len(extension)]
    return bool(re.fullmatch(r"[0-9a-f]{32}", file_id))


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

    def delete_generated(self, filename: str) -> bool:
        """Delete a file only when its name matches this store's generated-ID format."""
        if not is_generated_name(filename):
            return False
        target = (self.root / filename).resolve()
        if target.parent != self.root:
            return False
        try:
            target.unlink()
        except FileNotFoundError:
            return False
        return True


@dataclass(frozen=True)
class StoredUploadRef:
    """Reference to an upload kept in the database (serverless storage mode)."""

    name: str
    extension: str
    size: int


class DatabaseFileStore:
    """Store upload bytes in the relational database instead of the filesystem.

    Serverless/container filesystems are ephemeral; this store keeps the same
    generated-name contract as LocalFileStore while persisting bytes in the
    ``upload_blobs`` table so uploads survive redeploys. Names are random
    uuid4 hex values, never user-controlled.
    """

    def __init__(self, *, max_bytes: int = 100 * 1024 * 1024) -> None:
        self.max_bytes = int(max_bytes)
        if self.max_bytes <= 0:
            raise ValueError("max_bytes must be positive")

    def new_name(self, filename: str, content: bytes) -> StoredUploadRef:
        if len(content) > self.max_bytes:
            raise UploadValidationError("Upload exceeds the configured size limit")
        extension = _extension(filename)
        return StoredUploadRef(name=f"{uuid4().hex}{extension}", extension=extension, size=len(content))

    async def save(self, db, filename: str, content: bytes, *, content_type: str = "application/octet-stream") -> StoredUploadRef:
        from models.medical import UploadBlob

        ref = self.new_name(filename, content)
        db.add(UploadBlob(name=ref.name, content=content, size=ref.size, content_type=(content_type or "application/octet-stream")[:120]))
        await db.flush()
        return ref

    async def read(self, db, name: str) -> bytes | None:
        from models.medical import UploadBlob
        from sqlalchemy import select

        if not is_generated_name(name):
            return None
        row = (await db.execute(select(UploadBlob.content).where(UploadBlob.name == name))).scalar_one_or_none()
        return row

    async def delete_generated(self, db, filename: str) -> bool:
        from models.medical import UploadBlob
        from sqlalchemy import delete

        if not is_generated_name(filename):
            return False
        result = await db.execute(delete(UploadBlob).where(UploadBlob.name == filename))
        return bool(result.rowcount)
