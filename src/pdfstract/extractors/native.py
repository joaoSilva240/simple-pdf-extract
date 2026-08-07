"""Native PDF text extraction using pypdf."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from pdfstract.domain.models import ExtractionMethod, ExtractedDocument, Page


class NativeExtractor:
    """Extract text from digital PDFs using pypdf."""

    def extract(self, pdf_path: Path) -> ExtractedDocument:
        """Extract text from every page of *pdf_path*."""
        reader = PdfReader(str(pdf_path))
        pages: list[Page] = []

        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(Page(number=index, text=text, method=ExtractionMethod.NATIVE))

        return ExtractedDocument(source=pdf_path, pages=pages)

    def __enter__(self) -> NativeExtractor:
        return self

    def __exit__(self, *exc: object) -> None:
        return None
