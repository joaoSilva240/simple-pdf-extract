"""Domain models for pdfstract."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ExtractionMethod(str, Enum):
    """Method used to extract text from a PDF page."""

    NATIVE = "native"
    OCR = "ocr"


@dataclass
class Page:
    """A single extracted page."""

    number: int
    text: str
    method: ExtractionMethod


@dataclass
class ExtractedDocument:
    """A document extracted from a PDF file."""

    source: Path
    pages: list[Page]
