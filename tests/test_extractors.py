"""Tests for the extractor modules."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

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

    def test_extract_filters_selected_pages(self, sample_pdf: Path) -> None:
        extractor = NativeExtractor()
        document = extractor.extract(sample_pdf, pages={2})

        assert [page.number for page in document.pages] == [2]
        assert "Page two" in document.pages[0].text

    def test_extract_with_empty_page_selection_returns_no_pages(self, sample_pdf: Path) -> None:
        extractor = NativeExtractor()
        document = extractor.extract(sample_pdf, pages=set())

        assert document.pages == []


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

    def test_extract_with_selected_pages_uses_extract_page_per_page(
        self,
        tmp_path: Path,
    ) -> None:
        pdf_path = tmp_path / "multi.pdf"
        writer = __import__("pypdf").PdfWriter()
        writer.add_blank_page(width=612, height=792)
        writer.add_blank_page(width=612, height=792)
        with pdf_path.open("wb") as f:
            writer.write(f)

        extractor = OCRExtractor(lang="por")
        fake_image = Image.new("RGB", (100, 100), color="white")

        with (
            patch(
                "pdfstract.extractors.ocr.convert_from_path",
                return_value=[fake_image],
            ) as convert_mock,
            patch(
                "pdfstract.extractors.ocr.pytesseract.image_to_string",
                side_effect=["page 1", "page 3"],
            ),
        ):
            document = extractor.extract(pdf_path, pages={1, 3})

        assert [page.number for page in document.pages] == [1, 3]
        assert [page.text for page in document.pages] == ["page 1", "page 3"]
        assert all(page.method == ExtractionMethod.OCR for page in document.pages)
        # extract_page is called once per selected page, passing first_page=last_page=n
        convert_calls = [
            call.kwargs for call in convert_mock.call_args_list if "first_page" in call.kwargs
        ]
        assert len(convert_calls) == 2
        assert sorted(call["first_page"] for call in convert_calls) == [1, 3]
