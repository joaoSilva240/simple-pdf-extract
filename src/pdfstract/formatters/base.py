"""Base formatter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from pdfstract.domain.models import ExtractedDocument


class Formatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def format(self, document: ExtractedDocument) -> str:
        """Return the document contents as a string."""

    @abstractmethod
    def extension(self) -> str:
        """Return the file extension for this formatter (without leading dot)."""

    def write(self, document: ExtractedDocument, output_path: Path) -> None:
        """Format and write the document to *output_path*."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.format(document), encoding="utf-8")
