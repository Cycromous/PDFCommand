import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "PDFCommand")))


def test_import_theme():
    import theme
    assert hasattr(theme, "BG_GRAY")
    assert hasattr(theme, "MINT_GREEN")


def test_import_ui_helpers():
    import ui_helpers
    assert hasattr(ui_helpers, "create_rounded_button")
    assert hasattr(ui_helpers, "create_hover_card")


def test_import_modules_and_classes():
    import Home
    assert hasattr(Home, "HomeFrame")
    assert hasattr(Home, "ModernPDFHome")

    import PDFEditor
    assert hasattr(PDFEditor, "EditorFrame")
    assert hasattr(PDFEditor, "ModernPDFEditor")

    import PDFMerger
    assert hasattr(PDFMerger, "MergerFrame")
    assert hasattr(PDFMerger, "ModernPDFMerger")

    import PDFSplitter
    assert hasattr(PDFSplitter, "SplitterFrame")
    assert hasattr(PDFSplitter, "ModernPDFSplitter")

    import PDFConverter
    assert hasattr(PDFConverter, "ConverterFrame")
    assert hasattr(PDFConverter, "ModernPDFConverter")

    import PDFViewer
    assert hasattr(PDFViewer, "ViewerFrame")
    assert hasattr(PDFViewer, "ModernPDFViewer")


def test_import_app_controller():
    import app_controller
    assert hasattr(app_controller, "PDFCommanderApp")
    assert hasattr(app_controller, "PDFCommandApp")
    assert "home" in app_controller.PDFCommanderApp.FRAME_CLASSES
    assert "editor" in app_controller.PDFCommanderApp.FRAME_CLASSES
    assert "merger" in app_controller.PDFCommanderApp.FRAME_CLASSES
    assert "splitter" in app_controller.PDFCommanderApp.FRAME_CLASSES
    assert "converter" in app_controller.PDFCommanderApp.FRAME_CLASSES
    assert "viewer" in app_controller.PDFCommanderApp.FRAME_CLASSES

