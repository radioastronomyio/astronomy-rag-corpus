"""
Extraction pipeline orchestration.

Provides a unified entry point for extracting papers from either LaTeX source
or PDF fallback, with automatic method selection and graceful degradation.
"""

import logging
from pathlib import Path
from typing import Optional

from .latex_parser import extract_from_latex
from .models import ExtractedPaper, save_json
from .pdf_extractor import extract_from_pdf

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Raised when extraction cannot be completed."""

    pass


def extract_paper(arxiv_id: str, source_dir: Path) -> ExtractedPaper:
    """
    Extract paper from source directory using available input formats.

    Attempts LaTeX extraction first (preferred), falls back to PDF if LaTeX
    is unavailable or fails. Automatically identifies main LaTeX file and
    writes JSON output to source_dir.

    Args:
        arxiv_id: arXiv paper identifier
        source_dir: Directory containing source files (.tex, .pdf, .bbl)

    Returns:
        ExtractedPaper with extracted content

    Raises:
        ExtractionError: If no valid input files found or all extraction methods fail
    """
    # AI NOTE: This is the main entry point for paper extraction. It handles
    # automatic format detection and graceful fallback. The pipeline tries LaTeX
    # first (highest quality), then PDF (best-effort fallback).

    source_dir = Path(source_dir)

    if not source_dir.exists():
        raise ExtractionError(f"Source directory does not exist: {source_dir}")

    if not source_dir.is_dir():
        raise ExtractionError(f"Source path is not a directory: {source_dir}")

    # Try LaTeX extraction first
    paper = _try_latex_extraction(arxiv_id, source_dir)

    if paper is None:
        # Fall back to PDF extraction
        paper = _try_pdf_extraction(arxiv_id, source_dir)

    if paper is None:
        raise ExtractionError(
            f"No valid input files found in {source_dir}. Expected .tex or .pdf file."
        )

    # Save JSON output
    json_path = source_dir / "extracted.json"
    save_json(paper, json_path)
    logger.info(f"Saved extraction to {json_path}")

    return paper


def _try_latex_extraction(arxiv_id: str, source_dir: Path) -> Optional[ExtractedPaper]:
    """
    Attempt LaTeX extraction from source directory.

    Args:
        arxiv_id: arXiv paper identifier
        source_dir: Directory containing source files

    Returns:
        ExtractedPaper if successful, None otherwise
    """
    # Find all .tex files
    tex_files = list(source_dir.glob("*.tex"))

    if not tex_files:
        logger.debug(f"No .tex files found in {source_dir}")
        return None

    # Identify main tex file (contains \begin{document})
    main_tex_path: Optional[Path] = None

    for tex_file in tex_files:
        try:
            with open(tex_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                if "\\begin{document}" in content:
                    main_tex_path = tex_file
                    logger.debug(f"Identified main LaTeX file: {tex_file.name}")
                    break
        except Exception as e:
            logger.warning(f"Failed to read {tex_file}: {e}")

    if not main_tex_path:
        logger.warning(f"No main LaTeX file found in {source_dir}")
        return None

    # Attempt LaTeX extraction
    try:
        logger.info(f"Attempting LaTeX extraction from: {main_tex_path}")
        return extract_from_latex(main_tex_path, arxiv_id)
    except Exception as e:
        logger.warning(f"LaTeX extraction failed: {e}")
        return None


def _try_pdf_extraction(arxiv_id: str, source_dir: Path) -> Optional[ExtractedPaper]:
    """
    Attempt PDF extraction from source directory.

    Args:
        arxiv_id: arXiv paper identifier
        source_dir: Directory containing source files

    Returns:
        ExtractedPaper if successful, None otherwise
    """
    # Find PDF file (look for arxiv_id.pdf or any .pdf)
    pdf_files = list(source_dir.glob("*.pdf"))

    if not pdf_files:
        logger.debug(f"No .pdf files found in {source_dir}")
        return None

    # Prefer arxiv_id.pdf if available, otherwise use first PDF
    pdf_path: Optional[Path] = None
    preferred_name = f"{arxiv_id.replace('/', '_')}.pdf"

    for pdf_file in pdf_files:
        if pdf_file.name == preferred_name:
            pdf_path = pdf_file
            logger.debug(f"Found preferred PDF: {pdf_file.name}")
            break

    if not pdf_path and pdf_files:
        pdf_path = pdf_files[0]
        logger.debug(f"Using available PDF: {pdf_path.name}")

    if not pdf_path:
        return None

    # Attempt PDF extraction
    try:
        logger.info(f"Attempting PDF extraction from: {pdf_path}")
        return extract_from_pdf(pdf_path, arxiv_id)
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return None
