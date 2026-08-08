"""OCR PDF text extraction using pypdfium2 + rapidocr."""

from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image
from rapidocr import RapidOCR

from pdfstract.domain.models import ExtractedDocument, ExtractionMethod, Page


class OCRExtractor:
    """Extract text from scanned PDFs using OCR.

    Pages are rendered to PIL images with pypdfium2 (no external binaries) and
    recognized with rapidocr (ONNX models bundled with the package).
    """

    def __init__(self, lang: str = "por", scale: float = 2.0) -> None:
        """Create an OCR extractor.

        *lang* is kept for interface compatibility (the pipeline passes
        ``ocr_lang="por"``), but rapidocr's bundled models are multilingual and
        do not use it to select a recognizer.
        """
        self.lang = lang
        self.scale = scale
        self._ocr_engine: RapidOCR | None = None

    @property
    def engine(self) -> RapidOCR:
        """Return the shared RapidOCR engine, creating it on first use."""
        if self._ocr_engine is None:
            self._ocr_engine = RapidOCR()
        return self._ocr_engine

    def extract(
        self,
        pdf_path: Path,
        pages: set[int] | None = None,
    ) -> ExtractedDocument:
        """Extract text from *pdf_path* via OCR, optionally only from the given pages."""
        if pages is None:
            extracted: list[Page] = []
            pdf = pdfium.PdfDocument(str(pdf_path))
            try:
                for index in range(len(pdf)):
                    image = self._render_page(pdf, index)
                    text = self._ocr_image(image)
                    extracted.append(Page(number=index + 1, text=text, method=ExtractionMethod.OCR))
            finally:
                pdf.close()
            return ExtractedDocument(source=pdf_path, pages=extracted)

        extracted = [self.extract_page(pdf_path, page_number) for page_number in sorted(pages)]
        return ExtractedDocument(source=pdf_path, pages=extracted)

    def extract_page(self, pdf_path: Path, page_number: int) -> Page:
        """Extract text from a single page of *pdf_path* via OCR."""
        pdf = pdfium.PdfDocument(str(pdf_path))
        try:
            image = self._render_page(pdf, page_number - 1)
        finally:
            pdf.close()

        text = self._ocr_image(image)
        return Page(number=page_number, text=text, method=ExtractionMethod.OCR)

    def _render_page(self, pdf: pdfium.PdfDocument, index: int) -> Image.Image:
        """Render a 0-based page of an open pdfium document as a PIL image."""
        page = pdf[index]
        bitmap = page.render(scale=self.scale)
        return bitmap.to_pil()

    def _ocr_image(self, image: Image.Image) -> str:
        """Run rapidocr on a single image and return the recognized text."""
        result = self.engine(image)
        if result.txts is None:
            return ""
        return "\n".join(result.txts)
