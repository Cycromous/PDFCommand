import os
import sys
import tempfile
import fitz
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "PDFCommand")))


def test_image_to_pdf_conversion():
    """Verify converting an image (PNG) into a PDF via PyMuPDF."""
    with tempfile.TemporaryDirectory() as tmpdir:
        img_path = os.path.join(tmpdir, "test_image.png")
        out_pdf_path = os.path.join(tmpdir, "output.pdf")

        # Generate a small test PNG image using PyMuPDF Pixmap
        pix = fitz.Pixmap(fitz.csRGB, 100, 80, False)
        pix.clear_with(255)  # white background
        pix.save(img_path)

        # Replicate Converter conversion logic
        img_doc = fitz.open(img_path)
        pdf_bytes = img_doc.convert_to_pdf()
        img_pdf = fitz.open("pdf", pdf_bytes)
        img_pdf.save(out_pdf_path)
        img_pdf.close()
        img_doc.close()

        # Validate that the generated PDF exists and has 1 page
        assert os.path.exists(out_pdf_path)
        converted_doc = fitz.open(out_pdf_path)
        assert len(converted_doc) == 1
        assert converted_doc[0].rect.width == 100
        assert converted_doc[0].rect.height == 80
        converted_doc.close()


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

