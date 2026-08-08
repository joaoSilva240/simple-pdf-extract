"""Plain text formatter for extracted documents."""

from __future__ import annotations

from pdfstract.domain.models import ExtractedDocument
from pdfstract.formatters.base import Formatter


class PlainTextFormatter(Formatter):
    """Format extracted pages as plain text."""

    def format(self, document: ExtractedDocument) -> str:
        blocks: list[str] = []

        for page in document.pages:
            blocks.append(page.text)

        return "\n\n".join(blocks)

    def extension(self) -> str:
        return "txt"
