from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from services.document_loader import (
    DocumentLoadError,
    MAX_IMAGE_PIXELS,
    MAX_PDF_RENDERED_PIXELS,
    _encode_png,
    _load_pdf,
)


class DocumentLoaderLimitTests(unittest.TestCase):
    def test_oversized_image_dimensions_are_rejected_before_conversion(self):
        image = MagicMock()
        image.__enter__.return_value = image
        image.__exit__.return_value = False
        image.width = MAX_IMAGE_PIXELS + 1
        image.height = 1
        with patch("PIL.Image.open", return_value=image):
            with self.assertRaisesRegex(DocumentLoadError, "pixel processing limit"):
                _encode_png(b"placeholder")
        image.convert.assert_not_called()

    def test_pdf_total_rendered_pixels_are_capped_before_rendering_the_next_page(self):
        pages = []
        for _ in range(2):
            page = MagicMock()
            page.rect.width = 10
            page.rect.height = 10
            page.get_text.return_value = ""
            page.get_pixmap.return_value.tobytes.return_value = b"png"
            pages.append(page)
        pdf = MagicMock()
        pdf.page_count = len(pages)
        pdf.__iter__.return_value = iter(pages)
        fitz = MagicMock()
        fitz.open.return_value.__enter__.return_value = pdf
        with patch.dict("sys.modules", {"fitz": fitz}):
            with patch("services.document_loader.PDF_RENDER_DPI", 72):
                with patch("services.document_loader.MAX_PDF_RENDERED_PIXELS", 150):
                    with self.assertRaisesRegex(DocumentLoadError, "total processing limit"):
                        _load_pdf(b"pdf", "test.pdf")
        pages[0].get_pixmap.assert_called_once()
        pages[1].get_pixmap.assert_not_called()


if __name__ == "__main__":
    unittest.main()
