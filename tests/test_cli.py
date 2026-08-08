"""Tests for CLI helpers (page parsing and filename suffixes)."""

from __future__ import annotations

import pytest

from pdfstract.cli import _pages_suffix, _parse_pages


class TestParsePages:
    def test_single_page(self) -> None:
        assert _parse_pages("3") == {3}

    def test_comma_separated_pages(self) -> None:
        assert _parse_pages("1,3,5") == {1, 3, 5}

    def test_page_range(self) -> None:
        assert _parse_pages("5-8") == {5, 6, 7, 8}

    def test_mixed_pages_and_ranges(self) -> None:
        assert _parse_pages("1,3,5-8") == {1, 3, 5, 6, 7, 8}

    def test_whitespace_is_tolerated(self) -> None:
        assert _parse_pages(" 1 , 3-5 ") == {1, 3, 4, 5}

    def test_invalid_page_raises(self) -> None:
        with pytest.raises(ValueError):
            _parse_pages("abc")

    def test_invalid_range_raises(self) -> None:
        with pytest.raises(ValueError):
            _parse_pages("8-5")

    def test_zero_page_raises(self) -> None:
        with pytest.raises(ValueError):
            _parse_pages("0")

    def test_empty_spec_raises(self) -> None:
        with pytest.raises(ValueError):
            _parse_pages("")


class TestPagesSuffix:
    def test_no_pages_returns_empty(self) -> None:
        assert _pages_suffix(set()) == ""

    def test_single_page(self) -> None:
        assert _pages_suffix({3}) == "_p3"

    def test_compresses_consecutive_ranges(self) -> None:
        assert _pages_suffix({1, 3, 5, 6, 7, 8}) == "_p1,3,5-8"

    def test_orders_pages(self) -> None:
        assert _pages_suffix({8, 1, 3}) == "_p1,3,8"
