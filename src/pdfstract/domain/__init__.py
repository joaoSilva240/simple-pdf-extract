"""Domain layer for pdfstract."""

from pdfstract.domain.config import (
    DEFAULT_DATA_DIR,
    DEFAULT_FORMAT,
    DEFAULT_OCR_LANGUAGE,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_UI_LANGUAGE,
    MIN_CHARS_FOR_NATIVE,
    OCR_FALLBACK_LANGUAGE,
)
from pdfstract.domain.models import ExtractionMethod, ExtractedDocument, Page
from pdfstract.domain.pipeline import ExtractionPipeline

__all__ = [
    "DEFAULT_DATA_DIR",
    "DEFAULT_FORMAT",
    "DEFAULT_OCR_LANGUAGE",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_UI_LANGUAGE",
    "MIN_CHARS_FOR_NATIVE",
    "OCR_FALLBACK_LANGUAGE",
    "ExtractionMethod",
    "ExtractedDocument",
    "Page",
    "ExtractionPipeline",
]
