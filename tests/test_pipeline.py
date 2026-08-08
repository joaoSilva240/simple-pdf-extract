"""Tests for the extraction pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from pdfstract.domain.models import ExtractionMethod
from pdfstract.domain.pipeline import ExtractionPipeline


def _mock_pdf_document(page_count: int) -> MagicMock:
    document = MagicMock()
    document.__len__.return_value = page_count
    page = MagicMock()
    page.render.return_value.to_pil.return_value = MagicMock()
    document.__getitem__.return_value = page
    return document


class TestExtractionPipeline:
    def test_sufficient_native_text_skips_ocr(self, sample_pdf: Path) -> None:
        pipeline = ExtractionPipeline()
        document = pipeline.extract(sample_pdf, force_ocr=False)

        assert document is not None
        assert all(page.method == ExtractionMethod.NATIVE for page in document.pages)

    def test_insufficient_native_text_falls_back_to_ocr(
        self,
        scanned_like_pdf: Path,
    ) -> None:
        pipeline = ExtractionPipeline()

        with (
            patch(
                "pdfstract.extractors.ocr.pdfium.PdfDocument",
                return_value=_mock_pdf_document(1),
            ),
            patch("pdfstract.extractors.ocr.RapidOCR") as engine_mock,
        ):
            engine_mock.return_value.return_value.txts = ("OCR fallback text",)
            document = pipeline.extract(scanned_like_pdf, force_ocr=False)

        assert document is not None
        assert all(page.method == ExtractionMethod.OCR for page in document.pages)
        assert "OCR fallback text" in document.pages[0].text

    def test_force_ocr_ignores_native_extraction(self, sample_pdf: Path) -> None:
        pipeline = ExtractionPipeline()

        with (
            patch(
                "pdfstract.extractors.ocr.pdfium.PdfDocument",
                return_value=_mock_pdf_document(2),
            ),
            patch("pdfstract.extractors.ocr.RapidOCR") as engine_mock,
        ):
            engine_mock.return_value.return_value.txts = ("forced OCR",)
            document = pipeline.extract(sample_pdf, force_ocr=True)

        assert document is not None
        assert all(page.method == ExtractionMethod.OCR for page in document.pages)

    def test_extract_with_selected_pages_returns_only_those_pages(self, sample_pdf: Path) -> None:
        pipeline = ExtractionPipeline()
        document = pipeline.extract(sample_pdf, pages={2})

        assert document is not None
        assert [page.number for page in document.pages] == [2]
        assert document.pages[0].method == ExtractionMethod.NATIVE

    def test_extract_with_selected_pages_falls_back_to_ocr_per_page(
        self,
        scanned_like_pdf: Path,
    ) -> None:
        pipeline = ExtractionPipeline()

        with (
            patch(
                "pdfstract.extractors.ocr.pdfium.PdfDocument",
                return_value=_mock_pdf_document(1),
            ),
            patch("pdfstract.extractors.ocr.RapidOCR") as engine_mock,
        ):
            engine_mock.return_value.return_value.txts = ("OCR fallback text",)
            document = pipeline.extract(scanned_like_pdf, pages={1})

        assert document is not None
        assert [page.number for page in document.pages] == [1]
        assert document.pages[0].method == ExtractionMethod.OCR
