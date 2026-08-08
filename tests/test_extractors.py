"""Tests for the extractor modules."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from pdfstract.domain.models import ExtractionMethod, Page
from pdfstract.extractors.native import NativeExtractor
from pdfstract.extractors.ocr import OCRExtractor


def _mock_pdf_document(page_count: int) -> MagicMock:
    document = MagicMock()
    document.__len__.return_value = page_count
    page = MagicMock()
    page.render.return_value.to_pil.return_value = Image.new("RGB", (100, 100), color="white")
    document.__getitem__.return_value = page
    return document


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

        with (
            patch(
                "pdfstract.extractors.ocr.pdfium.PdfDocument",
                return_value=_mock_pdf_document(1),
            ),
            patch("pdfstract.extractors.ocr.RapidOCR") as engine_mock,
        ):
            engine_mock.return_value.return_value.txts = ("OCR text",)
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

        with (
            patch(
                "pdfstract.extractors.ocr.pdfium.PdfDocument",
                return_value=_mock_pdf_document(1),
            ),
            patch("pdfstract.extractors.ocr.RapidOCR", return_value=MagicMock()),
        ):
            engine = extractor.engine
            engine.return_value.txts = ("page text",)

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

        with (
            patch.object(OCRExtractor, "extract_page") as extract_page_mock,
        ):
            extract_page_mock.side_effect = [
                Page(number=1, text="page 1", method=ExtractionMethod.OCR),
                Page(number=3, text="page 3", method=ExtractionMethod.OCR),
            ]
            document = extractor.extract(pdf_path, pages={1, 3})

        assert [page.number for page in document.pages] == [1, 3]
        assert [page.text for page in document.pages] == ["page 1", "page 3"]
        assert all(page.method == ExtractionMethod.OCR for page in document.pages)
        # extract_page is called once per selected page
        assert [call.args[1] for call in extract_page_mock.call_args_list] == [1, 3]
