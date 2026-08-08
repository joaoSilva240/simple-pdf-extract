"""OCR PDF text extraction using pdf2image + pytesseract."""

from __future__ import annotations

from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

from pdfstract.domain.models import ExtractedDocument, ExtractionMethod, Page


class OCRExtractor:
    """Extract text from scanned PDFs using OCR."""

    def __init__(self, lang: str = "por", dpi: int = 200) -> None:
        self.lang = lang
        self.dpi = dpi

    def extract(
        self,
        pdf_path: Path,
        pages: set[int] | None = None,
    ) -> ExtractedDocument:
        """Extract text from *pdf_path* via OCR, optionally only from the given pages."""
        if pages is None:
            images = convert_from_path(str(pdf_path), dpi=self.dpi)
            extracted: list[Page] = []
            for index, image in enumerate(images, start=1):
                text = self._ocr_image(image)
                extracted.append(Page(number=index, text=text, method=ExtractionMethod.OCR))
            return ExtractedDocument(source=pdf_path, pages=extracted)

        extracted = [self.extract_page(pdf_path, page_number) for page_number in sorted(pages)]
        return ExtractedDocument(source=pdf_path, pages=extracted)

    def extract_page(self, pdf_path: Path, page_number: int) -> Page:
        """Extract text from a single page of *pdf_path* via OCR."""
        images = convert_from_path(
            str(pdf_path),
            dpi=self.dpi,
            first_page=page_number,
            last_page=page_number,
        )
        if not images:
            return Page(number=page_number, text="", method=ExtractionMethod.OCR)

        text = self._ocr_image(images[0])
        return Page(number=page_number, text=text, method=ExtractionMethod.OCR)

    def _ocr_image(self, image: Image.Image) -> str:
        """Run Tesseract OCR on a single image."""
        grayscale = image.convert("L")
        scaled = grayscale.resize((grayscale.width * 2, grayscale.height * 2), Image.LANCZOS)
        return pytesseract.image_to_string(scaled, lang=self.lang) or ""

    def __enter__(self) -> OCRExtractor:
        return self

    def __exit__(self, *exc: object) -> None:
        return None
