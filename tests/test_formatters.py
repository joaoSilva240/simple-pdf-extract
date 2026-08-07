"""Tests for the formatter modules."""

from __future__ import annotations

from pathlib import Path

from pdfstract.domain.models import ExtractionMethod, ExtractedDocument, Page
from pdfstract.formatters.markdown import MarkdownFormatter
from pdfstract.formatters.plain_text import PlainTextFormatter


def make_document(tmp_path: Path) -> ExtractedDocument:
    return ExtractedDocument(
        source=tmp_path / "report.pdf",
        pages=[
            Page(number=1, text="First page.", method=ExtractionMethod.NATIVE),
            Page(number=2, text="Second page.", method=ExtractionMethod.OCR),
        ],
    )


class TestMarkdownFormatter:
    def test_format_includes_filename_and_page_headers(self, tmp_path: Path) -> None:
        document = make_document(tmp_path)
        formatter = MarkdownFormatter()
        output = formatter.format(document)

        assert "# report.pdf" in output
        assert "## Página 1" in output
        assert "## Página 2" in output
        assert "First page." in output
        assert "Second page." in output

    def test_extension_is_md(self) -> None:
        assert MarkdownFormatter().extension() == "md"


class TestPlainTextFormatter:
    def test_format_separates_pages_with_blank_lines(self, tmp_path: Path) -> None:
        document = make_document(tmp_path)
        formatter = PlainTextFormatter()
        output = formatter.format(document)

        assert "First page." in output
        assert "Second page." in output
        assert output == "First page.\n\nSecond page."

    def test_extension_is_txt(self) -> None:
        assert PlainTextFormatter().extension() == "txt"
