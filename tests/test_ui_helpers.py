import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "PDFCommand")))

from ui_helpers import _rounded_points


def test_rounded_points_structure():
    pts = _rounded_points(width=140, height=36, radius=18, pad=2)
    assert isinstance(pts, list)
    # The polygon uses 12 coordinate pairs = 24 numbers
    assert len(pts) == 24


def test_rounded_points_bounds():
    w, h, r, pad = 200, 100, 25, 4
    pts = _rounded_points(w, h, r, pad=pad)
    xs = pts[0::2]
    ys = pts[1::2]

    # Every x must be within [pad, w - pad]
    for x in xs:
        assert pad <= x <= (w - pad), f"x coordinate {x} out of bounds [{pad}, {w - pad}]"

    # Every y must be within [pad, h - pad]
    for y in ys:
        assert pad <= y <= (h - pad), f"y coordinate {y} out of bounds [{pad}, {h - pad}]"


def test_rounded_points_zero_pad():
    pts = _rounded_points(width=100, height=40, radius=20, pad=0)
    assert min(pts[0::2]) == 0
    assert max(pts[0::2]) == 100
    assert min(pts[1::2]) == 0
    assert max(pts[1::2]) == 40

