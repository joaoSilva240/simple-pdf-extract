"""Extractors for pdfstract."""

from pdfstract.extractors.base import Extractor
from pdfstract.extractors.native import NativeExtractor
from pdfstract.extractors.ocr import OCRExtractor

__all__ = ["Extractor", "NativeExtractor", "OCRExtractor"]
