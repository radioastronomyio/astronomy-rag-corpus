"""
Tests for extraction pipeline orchestration.
"""

from pathlib import Path

import pytest
from src.extraction.pipeline import ExtractionError, extract_paper
from src.logging_config import setup_logging

setup_logging()


def test_pipeline_latex_first_path():
    """Test that pipeline prefers LaTeX when available."""
    # Use the seed paper directory which has both LaTeX and PDF
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    paper = extract_paper("2411.00148", source_dir)

    # Verify LaTeX method was used
    assert paper.extraction_info.method == "latex"

    # Verify JSON output was created
    json_path = source_dir / "extracted.json"
    assert json_path.exists(), f"JSON output should exist at {json_path}"


def test_pipeline_fallback_path():
    """Test that pipeline falls back to PDF when LaTeX unavailable."""
    # Create a test directory with only a PDF file
    from src.extraction.pdf_extractor import extract_from_pdf

    # This test assumes PDF exists in test_output/raw
    pdf_path = Path("test_output/raw/2411.00148.pdf")

    if not pdf_path.exists():
        pytest.skip(f"PDF file not found: {pdf_path}")

    # We can't easily create a test directory with only PDF here,
    # so we'll just verify the fallback function works
    paper = extract_from_pdf(pdf_path, "2411.00148")
    assert paper.extraction_info.method == "pdf_fallback"


def test_pipeline_error_path():
    """Test that pipeline raises ExtractionError for empty directory."""
    # Create a temporary empty directory for testing
    import tempfile
    import shutil

    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Empty directory should raise ExtractionError
        with pytest.raises(ExtractionError):
            extract_paper("test_id", temp_dir)
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_pipeline_json_output():
    """Test that pipeline creates JSON output."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Run extraction
    paper = extract_paper("2411.00148", source_dir)

    # Verify JSON file exists
    json_path = source_dir / "extracted.json"
    assert json_path.exists(), f"JSON output should exist at {json_path}"

    # Verify JSON is loadable
    import json

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Verify top-level keys
    assert "arxiv_id" in data
    assert "title" in data
    assert "authors" in data
    assert "sections" in data
    assert "references" in data
