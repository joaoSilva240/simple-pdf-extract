"""Extraction pipeline with native → OCR fallback."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from pdfstract.domain.config import MIN_CHARS_FOR_NATIVE
from pdfstract.domain.models import ExtractionMethod, ExtractedDocument, Page
from pdfstract.extractors.native import NativeExtractor
from pdfstract.extractors.ocr import OCRExtractor
from pdfstract.i18n import get_message


class ExtractionPipeline:
    """Orchestrates extraction using native extraction first, falling back to OCR."""

    def __init__(
        self,
        ocr_lang: str = "por",
        ui_lang: str = "pt",
        min_chars: int = MIN_CHARS_FOR_NATIVE,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        self.ocr_lang = ocr_lang
        self.ui_lang = ui_lang
        self.min_chars = min_chars
        self.progress_callback = progress_callback

    def extract(self, pdf_path: Path, force_ocr: bool = False) -> ExtractedDocument | None:
        """Extract text from *pdf_path*, optionally forcing OCR."""
        self._notify(get_message("start_extraction", self.ui_lang, path=pdf_path))

        if force_ocr:
            return self._extract_with_ocr(pdf_path)

        return self._extract_with_fallback(pdf_path)

    def _extract_with_fallback(self, pdf_path: Path) -> ExtractedDocument | None:
        native_extractor = NativeExtractor()
        ocr_extractor = OCRExtractor(lang=self.ocr_lang)

        try:
            native_doc = native_extractor.extract(pdf_path)
        except Exception as exc:
            self._notify(str(exc))
            return None

        pages: list[Page] = []
        for page in native_doc.pages:
            if len(page.text.strip()) >= self.min_chars:
                self._notify(
                    get_message("page_processed_native", self.ui_lang, number=page.number)
                )
                pages.append(page)
                continue

            try:
                ocr_page = ocr_extractor.extract_page(pdf_path, page.number)
                self._notify(
                    get_message("page_processed_ocr", self.ui_lang, number=page.number)
                )
                pages.append(ocr_page)
            except Exception as exc:
                self._notify(
                    get_message(
                        "page_ocr_error",
                        self.ui_lang,
                        number=page.number,
                        error=str(exc),
                    )
                )
                pages.append(Page(number=page.number, text="", method=ExtractionMethod.OCR))

        return ExtractedDocument(source=pdf_path, pages=pages)

    def _extract_with_ocr(self, pdf_path: Path) -> ExtractedDocument | None:
        ocr_extractor = OCRExtractor(lang=self.ocr_lang)

        try:
            doc = ocr_extractor.extract(pdf_path)
        except Exception as exc:
            self._notify(get_message("ocr_not_available", self.ui_lang))
            self._notify(str(exc))
            return None

        for page in doc.pages:
            self._notify(get_message("page_processed_ocr", self.ui_lang, number=page.number))

        return doc

    def _notify(self, message: str) -> None:
        if self.progress_callback:
            self.progress_callback(message)
