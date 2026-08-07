"""Base extractor interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from pdfstract.domain.models import ExtractedDocument


class Extractor(ABC):
    """Abstract base class for PDF text extractors."""

    @abstractmethod
    def extract(self, pdf_path: Path) -> ExtractedDocument:
        """Extract text from the given PDF file."""
