import pytest


def parse_page_range(range_str: str, page_count: int):
    """Replicates the range parsing logic from PDFSplitter."""
    cleaned = range_str.replace(" ", "")
    if not cleaned:
        raise ValueError("Range string is empty")

    pages_to_keep = []
    parts = cleaned.split(",")
    for part in parts:
        if "-" in part:
            sub = part.split("-")
            if len(sub) != 2:
                raise ValueError(f"Invalid range format: '{part}'")
            start, end = int(sub[0]), int(sub[1])
            if start > end:
                raise ValueError(f"Invalid range '{part}': start page is after end page.")
            pages_to_keep.extend(range(start - 1, end))
        else:
            pages_to_keep.append(int(part) - 1)

    pages_to_keep = sorted(set(pages_to_keep))

    if any(p < 0 or p >= page_count for p in pages_to_keep):
        raise IndexError(f"Page number out of bounds for document with {page_count} pages.")

    return pages_to_keep


def test_parse_single_page():
    result = parse_page_range("1", 10)
    assert result == [0]


def test_parse_range():
    result = parse_page_range("1-4", 10)
    assert result == [0, 1, 2, 3]


def test_parse_complex_range():
    result = parse_page_range("1-3, 5, 8-10", 10)
    assert result == [0, 1, 2, 4, 7, 8, 9]


def test_parse_range_with_whitespace():
    result = parse_page_range(" 2 - 4 ,  6 ", 10)
    assert result == [1, 2, 3, 5]


def test_parse_overlapping_deduplication():
    result = parse_page_range("1-3, 2-4", 10)
    assert result == [0, 1, 2, 3]


def test_parse_inverted_range_raises_error():
    with pytest.raises(ValueError, match="start page is after end page"):
        parse_page_range("5-2", 10)


def test_parse_out_of_bounds_raises_error():
    with pytest.raises(IndexError, match="out of bounds"):
        parse_page_range("1-15", 10)


def test_parse_invalid_string_raises_error():
    with pytest.raises(ValueError):
        parse_page_range("abc", 10)

