"""
LaTeX extraction module for astronomical papers.

Provides functions and models for extracting structured content from LaTeX
source files or PDF fallback, including metadata, sections, and references.
"""

from .latex_parser import extract_from_latex
from .models import ExtractedPaper, save_json
from .pdf_extractor import extract_from_pdf
from .pipeline import ExtractionError, extract_paper

__all__ = [
    "extract_paper",
    "extract_from_latex",
    "extract_from_pdf",
    "ExtractedPaper",
    "save_json",
    "ExtractionError",
]
