"""Shared fixtures for pdfstract tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfWriter


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a simple digital PDF with two pages of text."""
    pdf_path = tmp_path / "sample.pdf"
    writer = PdfWriter()

    page_1 = writer.add_blank_page(width=612, height=792)
    page_1.extract_text = lambda: "This is page one with enough text."

    page_2 = writer.add_blank_page(width=612, height=792)
    page_2.extract_text = lambda: "Página dois com texto suficiente."

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
