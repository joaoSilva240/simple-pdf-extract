"""Shared fixtures for pdfstract tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfWriter
from pypdf.generic import ContentStream, DecodedStreamObject, DictionaryObject, NameObject


def _add_text_page(writer: PdfWriter, text: str) -> None:
    """Add a page with real extractable text to *writer*."""
    page = writer.add_blank_page(width=612, height=792)

    stream = DecodedStreamObject()
    stream.set_data(f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin-1"))
    page[NameObject("/Contents")] = ContentStream(stream, page)

    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    resources = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
    page[NameObject("/Resources")] = resources


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a simple digital PDF with two pages of text."""
    pdf_path = tmp_path / "sample.pdf"
    writer = PdfWriter()

    _add_text_page(writer, "This is page one with enough text.")
    _add_text_page(writer, "Page two with enough text.")

    with pdf_path.open("wb") as f:
        writer.write(f)

    return pdf_path


@pytest.fixture
def scanned_like_pdf(tmp_path: Path) -> Path:
    """Create a PDF whose pages report almost no native text (simulates scans)."""
    pdf_path = tmp_path / "scan.pdf"
    writer = PdfWriter()

    for _ in range(2):
        page = writer.add_blank_page(width=612, height=792)
        page.extract_text = lambda: "   "

    with pdf_path.open("wb") as f:
        writer.write(f)

    return pdf_path
