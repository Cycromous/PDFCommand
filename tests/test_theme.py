import os
import sys
import pytest

# Ensure PDFCommand package directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "PDFCommand")))

import theme


def test_theme_constants_exist():
    required_constants = [
        "MINT_GREEN",
        "TEXT_COLOR",
        "BG_GRAY",
        "WHITE",
        "SIDEBAR_BG",
        "GENTLE_GRAY_BORDER",
        "TOOLBAR_COLOR",
        "TOOLBAR_DIVIDER",
        "NAV_BG",
        "DARK",
        "DISABLED_GRAY",
        "ACTIVE_TEXT",
    ]
    for const in required_constants:
        assert hasattr(theme, const), f"Missing theme constant: {const}"
        val = getattr(theme, const)
        assert isinstance(val, str), f"{const} should be a string"
        assert val.startswith("#"), f"{const} should start with '#'"
        assert len(val) == 7, f"{const} should be a 6-digit hex code"


def test_theme_values():
    assert theme.MINT_GREEN == "#93E9BE"
    assert theme.TEXT_COLOR == "#1F2937"
    assert theme.WHITE == "#FFFFFF"
    assert theme.DARK == "#111827"

