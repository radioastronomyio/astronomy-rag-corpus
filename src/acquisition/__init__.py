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
from .source_extractor import (
    CorruptTarballError,
    ExtractionError,
    MainTexNotFoundError,
    SourceManifest,
    extract_source,
)

__all__ = [
    # arxiv_client exports
    "download_source",
    "download_pdf",
    "PaperNotFoundError",
    "SourceUnavailableError",
    "PDFCorruptError",
    "NetworkError",
    # source_extractor exports
    "extract_source",
    "SourceManifest",
    "MainTexNotFoundError",
    "CorruptTarballError",
    "ExtractionError",
]
