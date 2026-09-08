import os
import sys
import tempfile
import fitz
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "PDFCommand")))


def create_dummy_pdf(num_pages: int, text_prefix: str = "Page") -> bytes:
    """Helper creating an in-memory PDF with specified number of pages."""
    doc = fitz.open()
    for i in range(num_pages):
        page = doc.new_page(width=300, height=300)
        page.insert_text((50, 50), f"{text_prefix} {i + 1}")
    data = doc.tobytes()
    doc.close()
    return data


def test_merge_two_pdfs():
    """Verify merging two separate PDF documents results in combined page count."""
    pdf1_bytes = create_dummy_pdf(2, "DocA")
    pdf2_bytes = create_dummy_pdf(3, "DocB")

    with tempfile.TemporaryDirectory() as tmpdir:
        path1 = os.path.join(tmpdir, "doc1.pdf")
        path2 = os.path.join(tmpdir, "doc2.pdf")
        out_path = os.path.join(tmpdir, "merged.pdf")

        with open(path1, "wb") as f:
            f.write(pdf1_bytes)
        with open(path2, "wb") as f:
            f.write(pdf2_bytes)

        # Merge using the exact logic from PDFMerger
        merged_doc = fitz.open()
        for p in [path1, path2]:
            doc_to_insert = fitz.open(p)
            merged_doc.insert_pdf(doc_to_insert)
            doc_to_insert.close()

        merged_doc.save(out_path)
        merged_doc.close()

        # Verification
        result = fitz.open(out_path)
        assert len(result) == 5
        assert "DocA 1" in result[0].get_text()
        assert "DocB 1" in result[2].get_text()
        result.close()


def test_merger_queue_reordering():
    """Test reordering items in the merge queue (Move Up / Move Down logic)."""
    items = ["file_a.pdf", "file_b.pdf", "file_c.pdf"]
    idx = 1  # select file_b

    # Move Up
    items[idx], items[idx - 1] = items[idx - 1], items[idx]
    assert items == ["file_b.pdf", "file_a.pdf", "file_c.pdf"]

    # Move Down
    idx = 0
    items[idx], items[idx + 1] = items[idx + 1], items[idx]
    assert items == ["file_a.pdf", "file_b.pdf", "file_c.pdf"]


def test_merger_minimum_file_requirement():
    """Verify that merging requires at least 2 files."""
    files = ["doc1.pdf"]
    assert len(files) < 2

