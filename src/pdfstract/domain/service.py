"""Reusable text extraction service shared by the CLI and the API."""

from __future__ import annotations

from pathlib import Path

from pdfstract.domain.config import DEFAULT_FORMAT, DEFAULT_OCR_LANGUAGE, DEFAULT_UI_LANGUAGE
from pdfstract.domain.pipeline import ExtractionPipeline
from pdfstract.formatters.base import Formatter
from pdfstract.formatters.markdown import MarkdownFormatter
from pdfstract.formatters.plain_text import PlainTextFormatter


def formatter_for(format_name: str) -> Formatter:
    """Return a formatter instance for the requested output format."""
    if format_name == "txt":
        return PlainTextFormatter()
    return MarkdownFormatter()


def extract_text(
    pdf_path: Path,
    format_name: str = DEFAULT_FORMAT,
    ocr_lang: str = DEFAULT_OCR_LANGUAGE,
    ui_lang: str = DEFAULT_UI_LANGUAGE,
    force_ocr: bool = False,
    pages: set[int] | None = None,
) -> str | None:
    """Extract text from *pdf_path* and return it formatted, or ``None`` on failure."""
    pipeline = ExtractionPipeline(
        ocr_lang=ocr_lang,
        ui_lang=ui_lang,
    )

    document = pipeline.extract(pdf_path, force_ocr=force_ocr, pages=pages)
    if document is None:
        return None

    formatter = formatter_for(format_name)
    return formatter.format(document)
