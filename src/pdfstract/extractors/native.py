"""Native PDF text extraction using pypdf."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from pdfstract.domain.models import ExtractedDocument, ExtractionMethod, Page


class NativeExtractor:
    """Extract text from digital PDFs using pypdf."""

    def extract(
        self,
        pdf_path: Path,
        pages: set[int] | None = None,
    ) -> ExtractedDocument:
        """Extract text from *pdf_path*, optionally only from the given 1-based page numbers."""
        reader = PdfReader(str(pdf_path))
        extracted: list[Page] = []

        for index, page in enumerate(reader.pages, start=1):
            if pages is not None and index not in pages:
                continue
            text = page.extract_text() or ""
            extracted.append(Page(number=index, text=text, method=ExtractionMethod.NATIVE))

        return ExtractedDocument(source=pdf_path, pages=extracted)
