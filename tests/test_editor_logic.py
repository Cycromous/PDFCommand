import os
import sys
import tempfile
import fitz
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "PDFCommand")))

from PDFEditor import EditorFrame


def test_hex_to_rgb():
    """Verify hex to normalized RGB tuple (0.0 - 1.0) conversion."""
    rgb_white = EditorFrame.hex_to_rgb(None, "#FFFFFF")
    assert rgb_white == (1.0, 1.0, 1.0)

    rgb_black = EditorFrame.hex_to_rgb(None, "#000000")
    assert rgb_black == (0.0, 0.0, 0.0)

    rgb_custom = EditorFrame.hex_to_rgb(None, "#93E9BE")
    assert len(rgb_custom) == 3
    assert all(0.0 <= c <= 1.0 for c in rgb_custom)


def test_editor_text_insertion():
    """Verify text is correctly inserted into the PDF document."""
    doc = fitz.open()
    page = doc.new_page(width=400, height=400)

    test_text = "Automated Test Text"
    font_size = 14
    point = fitz.Point(100, 150)

    page.insert_text(point, test_text, fontname="tiro", fontsize=font_size, color=(0, 0, 0))
    pdf_bytes = doc.tobytes()
    doc.close()

    # Reopen and check text was extracted
    reopened = fitz.open("pdf", pdf_bytes)
    page_text = reopened[0].get_text()
    assert test_text in page_text
    reopened.close()


def test_editor_shape_drawing():
    """Verify rectangle and oval shapes are drawn into PDF without document corruption."""
    doc = fitz.open()
    page = doc.new_page(width=500, height=500)

    rgb = EditorFrame.hex_to_rgb(None, "#93E9BE")

    rect = fitz.Rect(50, 50, 200, 100)
    page.draw_rect(rect, color=rgb, fill=rgb)

    oval = fitz.Rect(250, 50, 350, 150)
    page.draw_oval(oval, color=rgb, fill=rgb)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_name = tmp.name

    try:
        doc.save(tmp_name)
        doc.close()

        # Validate that the document is intact
        reopened = fitz.open(tmp_name)
        assert len(reopened) == 1
        reopened.close()
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


def test_coordinate_scaling_roundtrip():
    """Test canvas coordinate to PDF true_coords and back."""
    scale_factor = 1.5
    x_offset = 50.0
    y_offset = 10.0

    canvas_x = 200.0
    canvas_y = 310.0

    # Convert to PDF coordinates
    true_x = (canvas_x - x_offset) / scale_factor
    true_y = (canvas_y - y_offset) / scale_factor

    # Convert back to canvas coordinates
    reconstructed_x = (true_x * scale_factor) + x_offset
    reconstructed_y = (true_y * scale_factor) + y_offset

    assert pytest.approx(canvas_x) == reconstructed_x
    assert pytest.approx(canvas_y) == reconstructed_y


def test_autosave_snapshot_isolation():
    """Verify that modifying the master dictionary does not mutate the snapshot."""
    master = {0: {1: {"text": "Original"}}}
    snapshot = {p: dict(items) for p, items in master.items()}

    # Mutate master
    master[0][2] = {"text": "New"}

    # Snapshot should remain unaffected
    assert len(snapshot[0]) == 1
    assert 2 not in snapshot[0]

