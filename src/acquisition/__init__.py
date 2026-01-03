"""
Astronomy RAG Corpus - Data acquisition modules.

This package handles retrieval of source materials from external repositories
(arXiv, ADS). Entry point for the ingestion pipeline.
"""

from .arxiv_client import (
    NetworkError,
    PaperNotFoundError,
    PDFCorruptError,
    SourceUnavailableError,
    download_pdf,
    download_source,
)

__all__ = [
    "download_source",
    "download_pdf",
    "PaperNotFoundError",
    "SourceUnavailableError",
    "PDFCorruptError",
    "NetworkError",
]
