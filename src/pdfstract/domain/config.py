"""Configuration constants for pdfstract."""

from pathlib import Path

DEFAULT_DATA_DIR = Path("data")
DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_UI_LANGUAGE = "pt"
DEFAULT_OCR_LANGUAGE = "por"
DEFAULT_FORMAT = "md"
OCR_FALLBACK_LANGUAGE = "eng"
MIN_CHARS_FOR_NATIVE = 10
