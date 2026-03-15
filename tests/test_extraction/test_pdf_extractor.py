"""
Tests for PDF extractor.
"""

from pathlib import Path

import pytest
from src.extraction.pdf_extractor import extract_from_pdf
from src.logging_config import setup_logging

setup_logging()


def test_extract_from_pdf_with_real_pdf():
    """Test extracting from a real PDF if available."""
    pdf_path = Path("test_output/raw/2411.00148.pdf")

    if not pdf_path.exists():
        pytest.skip(f"PDF file not found: {pdf_path}")

    paper = extract_from_pdf(pdf_path, "2411.00148")

    # Verify extraction method
    assert paper.extraction_info.method == "pdf_fallback"

    # Verify title is non-empty
    assert paper.title, "Title should be non-empty"

    # Verify sections list is non-empty
    assert len(paper.sections) > 0, "Sections list should be non-empty"


def test_extract_from_pdf_file_not_found():
    """Test that FileNotFoundError is raised for non-existent PDF."""
    pdf_path = Path("nonexistent/file.pdf")

    with pytest.raises(FileNotFoundError):
        extract_from_pdf(pdf_path, "2411.00148")


def test_extract_from_pdf_graceful_degradation():
    """Test that extraction doesn't crash on valid PDF input."""
    pdf_path = Path("test_output/raw/2411.00148.pdf")

    if not pdf_path.exists():
        pytest.skip(f"PDF file not found: {pdf_path}")

    # This should not raise an exception, even if extraction is imperfect
    paper = extract_from_pdf(pdf_path, "2411.00148")

    # At minimum, we should get a valid ExtractedPaper object
    assert paper.arxiv_id == "2411.00148"
    assert paper.extraction_info is not None
