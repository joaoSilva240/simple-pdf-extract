"""Markdown formatter for extracted documents."""

from __future__ import annotations

from pdfstract.domain.models import ExtractedDocument
from pdfstract.formatters.base import Formatter


class MarkdownFormatter(Formatter):
    """Format extracted pages as Markdown."""

    def format(self, document: ExtractedDocument) -> str:
        lines: list[str] = [f"# {document.source.name}", ""]

        for page in document.pages:
            lines.append(f"## Página {page.number}")
            lines.append(page.text)
            lines.append("")

        return "\n".join(lines)

    def extension(self) -> str:
        return "md"
