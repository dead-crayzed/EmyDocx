"""Чистые функции из emydocx.utils."""
import pytest

from emydocx.utils import (
    read_number,
    suggested_docx_name,
    suggested_md_name,
    valid_hex,
)


class TestValidHex:
    @pytest.mark.parametrize("raw,expected", [
        ("#aabbcc", "#AABBCC"),
        ("aabbcc",  "#AABBCC"),
        ("  #FF00FF  ", "#FF00FF"),
        ("123456",  "#123456"),
    ])
    def test_normalizes(self, raw, expected):
        assert valid_hex(raw, "#000000") == expected

    @pytest.mark.parametrize("raw", [
        None, "", "#xyz", "12345", "1234567", "not-a-color", "#GGGGGG",
    ])
    def test_fallback_on_invalid(self, raw):
        assert valid_hex(raw, "#ABCDEF") == "#ABCDEF"


class TestReadNumber:
    @pytest.mark.parametrize("raw,expected", [
        ("12",   12.0),
        ("2.5",  2.5),
        (3,      3.0),
        (1.15,   1.15),
    ])
    def test_parses(self, raw, expected):
        assert read_number(raw, 0, 0, 100) == expected

    @pytest.mark.parametrize("raw", ["", None, "abc", [], {}])
    def test_default_on_error(self, raw):
        assert read_number(raw, 7.0, 0, 100) == 7.0

    def test_clamps_low(self):
        assert read_number("-5", 12, 6, 72) == 6

    def test_clamps_high(self):
        assert read_number("1000", 12, 6, 72) == 72

    def test_passthrough_within_range(self):
        assert read_number("20", 12, 6, 72) == 20


class TestSuggestedNames:
    def test_md_from_path(self):
        assert suggested_md_name("/tmp/report.md") == "report.md"

    def test_md_default(self):
        assert suggested_md_name(None) == "document.md"

    def test_docx_from_path(self):
        assert suggested_docx_name("/tmp/report.md") == "report.docx"

    def test_docx_default(self):
        assert suggested_docx_name(None) == "emydocx-document.docx"