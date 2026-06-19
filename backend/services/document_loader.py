"""Document loader for HomzDoctor medical inputs.

Turns an uploaded medical file (X-ray / CT / MRI image or a lab-report PDF) into
the two things a vision-language model needs:

    1. A list of base64-encoded PNG images (one per page / per file).
    2. Any embedded text the file already contains (e.g. a typed lab PDF).

Supported inputs: .jpg .jpeg .png .webp .bmp .tif/.tiff and .pdf

Optional dependencies (degrade gracefully if missing):
    - Pillow   -> image normalisation / format conversion
    - PyMuPDF  -> render PDF pages to images AND pull embedded text

If a dependency is missing we raise ``DocumentLoadError`` with a clear hint so
the caller can fall back instead of crashing.
"""

from __future__ import annotations

import base64
import io
import os
from dataclasses import dataclass, field
from typing import List, Optional

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
PDF_EXTS = {".pdf"}

# Cap how many PDF pages we render, to bound model cost/latency.
MAX_PDF_PAGES = int(os.getenv("LVLM_MAX_PDF_PAGES", "8"))
# DPI used when rasterising PDF pages.
PDF_RENDER_DPI = int(os.getenv("LVLM_PDF_DPI", "150"))


class DocumentLoadError(Exception):
    """Raised when a file cannot be turned into images/text."""


@dataclass
class LoadedDocument:
    """Result of loading a medical file."""

    images_b64: List[str] = field(default_factory=list)  # PNG, base64 (no data: prefix)
    text: str = ""                                        # embedded/extracted text
    page_count: int = 0
    source_name: str = ""

    def as_data_urls(self) -> List[str]:
        """Return images as ``data:image/png;base64,...`` URLs for chat APIs."""
        return [f"data:image/png;base64,{b}" for b in self.images_b64]


def _encode_png(raw: bytes) -> str:
    """Best-effort: normalise any image bytes to base64 PNG.

    Uses Pillow when available (handles odd formats / colour spaces); otherwise
    falls back to passing the original bytes through unchanged.
    """
    try:
        from PIL import Image  # type: ignore
    except Exception:
        # No Pillow: assume the bytes are already a web-friendly image.
        return base64.b64encode(raw).decode("ascii")

    with Image.open(io.BytesIO(raw)) as img:
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("ascii")


def _load_pdf(raw: bytes, source_name: str) -> LoadedDocument:
    try:
        import fitz  # PyMuPDF  # type: ignore
    except Exception as exc:  # pragma: no cover - import guard
        raise DocumentLoadError(
            "PyMuPDF is required to read PDF files. Install it with "
            "`pip install pymupdf`."
        ) from exc

    doc = LoadedDocument(source_name=source_name)
    text_chunks: List[str] = []
    zoom = PDF_RENDER_DPI / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(stream=raw, filetype="pdf") as pdf:
        doc.page_count = pdf.page_count
        for index, page in enumerate(pdf):
            if index >= MAX_PDF_PAGES:
                break
            text_chunks.append(page.get_text("text") or "")
            pixmap = page.get_pixmap(matrix=matrix)
            doc.images_b64.append(base64.b64encode(pixmap.tobytes("png")).decode("ascii"))

    doc.text = "\n".join(c.strip() for c in text_chunks if c.strip())
    return doc


def _load_image(raw: bytes, source_name: str) -> LoadedDocument:
    return LoadedDocument(
        images_b64=[_encode_png(raw)],
        page_count=1,
        source_name=source_name,
    )


def load_document(raw: bytes, filename: str) -> LoadedDocument:
    """Load raw file bytes into images + text based on the file extension."""
    ext = os.path.splitext(filename or "")[1].lower()
    if ext in PDF_EXTS:
        return _load_pdf(raw, filename)
    if ext in IMAGE_EXTS:
        return _load_image(raw, filename)
    raise DocumentLoadError(
        f"Unsupported file type '{ext or '?'}'. Supported: "
        f"{', '.join(sorted(IMAGE_EXTS | PDF_EXTS))}"
    )


def load_path(path: str) -> LoadedDocument:
    """Convenience: load a file from disk."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except OSError as exc:
        raise DocumentLoadError(f"Cannot read file '{path}': {exc}") from exc
    return load_document(raw, os.path.basename(path))
