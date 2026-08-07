"""Tests for the extractor modules."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from pdfstract.domain.models import ExtractionMethod
from pdfstract.extractors.native import NativeExtractor
from pdfstract.extractors.ocr import OCRExtractor


class TestNativeExtractor:
    def test_extracts_text_from_digital_pdf(self, sample_pdf: Path) -> None:
        extractor = NativeExtractor()
        document = extractor.extract(sample_pdf)

        assert document.source == sample_pdf
        assert len(document.pages) == 2
        assert document.pages[0].method == ExtractionMethod.NATIVE
        assert "page one" in document.pages[0].text


class TestOCRExtractor:
    def test_extract_returns_pages_with_ocr_method(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "empty.pdf"
        writer = __import__("pypdf").PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with pdf_path.open("wb") as f:
            writer.write(f)

        extractor = OCRExtractor(lang="por")
        fake_image = Image.new("RGB", (100, 100), color="white")

        with (
            patch("pdfstract.extractors.ocr.convert_from_path", return_value=[fake_image]),
            patch(
                "pdfstract.extractors.ocr.pytesseract.image_to_string",
                return_value="OCR text",
            ),
        ):
            document = extractor.extract(pdf_path)

        assert len(document.pages) == 1
        assert document.pages[0].method == ExtractionMethod.OCR
        assert document.pages[0].text == "OCR text"

    def test_extract_page_runs_ocr_on_single_page(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "single.pdf"
        writer = __import__("pypdf").PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with pdf_path.open("wb") as f:
            writer.write(f)

        extractor = OCRExtractor(lang="eng")
        fake_image = Image.new("RGB", (100, 100), color="white")

        with (
            patch("pdfstract.extractors.ocr.convert_from_path", return_value=[fake_image]),
            patch(
                "pdfstract.extractors.ocr.pytesseract.image_to_string",
                return_value="page text",
            ),
        ):
            page = extractor.extract_page(pdf_path, page_number=1)

        assert page.number == 1
        assert page.text == "page text"
        assert page.method == ExtractionMethod.OCR
