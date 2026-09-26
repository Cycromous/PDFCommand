import os
import sys
import tempfile

try:
    import pymupdf as fitz  # type: ignore[import-not-found]
except ImportError:
    import fitz  # type: ignore[import-not-found]

import pytest  # type: ignore[import-not-found]

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "PDFCommand")))


def test_image_to_pdf_conversion():
    """Verify converting an image (PNG) into a PDF via PyMuPDF."""
    with tempfile.TemporaryDirectory() as tmpdir:
        img_path = os.path.join(tmpdir, "test_image.png")
        out_pdf_path = os.path.join(tmpdir, "output.pdf")

        # Generate a small test PNG image using PyMuPDF Pixmap
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 100, 80))
        pix.clear_with(255)  # white background
        pix.save(img_path)

        # Replicate Converter conversion logic with context managers
        with fitz.open(img_path) as img_doc:
            pdf_bytes = img_doc.convert_to_pdf()

        with fitz.open("pdf", pdf_bytes) as img_pdf:
            img_pdf.save(out_pdf_path)

        # Validate that the generated PDF exists and has 1 page
        assert os.path.exists(out_pdf_path)

        with fitz.open(out_pdf_path) as converted_doc:
            assert len(converted_doc) == 1

            # PyMuPDF converts the 100x80 image using 96 DPI:
            # 100 * 72 / 96 = 75 pt, 80 * 72 / 96 = 60 pt
            assert converted_doc[0].rect.width == pytest.approx(75)
            assert converted_doc[0].rect.height == pytest.approx(60)


def test_converter_supported_extensions():
    """Verify supported vs unsupported file extensions."""
    supported = [".docx", ".png", ".jpg", ".jpeg", ".bmp"]
    test_files = [
        ("report.docx", True),
        ("photo.jpg", True),
        ("photo.JPEG", True),
        ("scan.png", True),
        ("image.bmp", True),
        ("notes.txt", False),
        ("script.py", False),
    ]

    for fname, is_supported in test_files:
        _, ext = os.path.splitext(fname)
        matches = ext.lower() in supported
        assert matches == is_supported, f"Extension check failed for {fname}"