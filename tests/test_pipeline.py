"""Tests for the extraction pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from pdfstract.domain.models import ExtractionMethod
from pdfstract.domain.pipeline import ExtractionPipeline


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
        fake_image = MagicMock()

        with (
            patch("pdfstract.extractors.ocr.convert_from_path", return_value=[fake_image]),
            patch(
                "pdfstract.extractors.ocr.pytesseract.image_to_string",
                return_value="OCR fallback text",
            ),
        ):
            document = pipeline.extract(scanned_like_pdf, force_ocr=False)

        assert document is not None
        assert all(page.method == ExtractionMethod.OCR for page in document.pages)
        assert "OCR fallback text" in document.pages[0].text

    def test_force_ocr_ignores_native_extraction(self, sample_pdf: Path) -> None:
        pipeline = ExtractionPipeline()
        fake_image = MagicMock()

        with (
            patch("pdfstract.extractors.ocr.convert_from_path", return_value=[fake_image, fake_image]),
            patch(
                "pdfstract.extractors.ocr.pytesseract.image_to_string",
                return_value="forced OCR",
            ),
        ):
            document = pipeline.extract(sample_pdf, force_ocr=True)

        assert document is not None
        assert all(page.method == ExtractionMethod.OCR for page in document.pages)
