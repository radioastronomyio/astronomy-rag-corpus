"""
PDF fallback extraction for papers without LaTeX source.

Uses pymupdf (fitz) to extract text from PDF files when LaTeX source
is unavailable. This is a best-effort fallback with lower fidelity than LaTeX.
"""

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import fitz

from .models import Author, ExtractionInfo, ExtractedPaper, Reference, Section

logger = logging.getLogger(__name__)


def extract_from_pdf(pdf_path: Path, arxiv_id: str) -> ExtractedPaper:
    """
    Extract structured content from a PDF file.

    This is a best-effort fallback for papers without LaTeX source.
    Section detection and metadata extraction are heuristic-based.

    Args:
        pdf_path: Path to PDF file
        arxiv_id: arXiv paper identifier

    Returns:
        ExtractedPaper with extracted content

    Raises:
        FileNotFoundError: If PDF file does not exist
        OSError: If file cannot be read
    """
    # AI NOTE: PDF extraction is inherently lower quality than LaTeX source.
    # This fallback exists for papers where LaTeX is unavailable. Don't over-engineer
    # it - reasonable best-effort is the standard approach.

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logger.info(f"Extracting from PDF file: {pdf_path}")

    # Initialize extraction info with warning
    extraction_info = ExtractionInfo(
        method="pdf_fallback",
        source_file=str(pdf_path),
        timestamp=datetime.now(timezone.utc).isoformat(),
        warnings=[
            "PDF extraction has lower fidelity than LaTeX source. "
            "Math notation and structure may be imperfect."
        ],
        pylatexenc_version=None,
    )

    # Open PDF and extract text
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        logger.error(f"Failed to open PDF {pdf_path}: {e}")
        raise OSError(f"Failed to open PDF {pdf_path}: {e}")

    try:
        # Extract title from metadata or first page
        title = _extract_title(doc, extraction_info)

        # Extract authors from first page (best-effort)
        authors = _extract_authors(doc, extraction_info)

        # Extract abstract (best-effort)
        abstract = _extract_abstract(doc, extraction_info)

        # Extract sections from document body
        sections = _extract_sections(doc, extraction_info)
        logger.info(f"Extracted {len(sections)} sections from PDF")

        # References - best-effort from final pages
        references = _extract_references(doc, extraction_info)
        logger.info(f"Extracted {len(references)} references from PDF")
    finally:
        doc.close()

    return ExtractedPaper(
        arxiv_id=arxiv_id,
        title=title,
        authors=authors,
        abstract=abstract,
        custom_commands={},  # PDF has no custom commands
        sections=sections,
        references=references,
        extraction_info=extraction_info,
    )


def _extract_title(doc: fitz.Document, extraction_info: ExtractionInfo) -> str:
    """
    Extract paper title from PDF metadata or first page.

    Args:
        doc: PyMuPDF document
        extraction_info: Extraction info for warning logging

    Returns:
        Paper title
    """
    # Try metadata first
    metadata = doc.metadata
    if metadata and isinstance(metadata, dict):
        title = metadata.get("title", "")
        if title:
            title = title.strip()
    else:
        title = ""

    if title and len(title) > 10:
        return title

    # Fallback: first non-empty text from first page
    if doc.page_count > 0:
        page = doc[0]
        text = page.get_text()
        if text and isinstance(text, str):
            # Split into lines and find the longest non-empty line
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            for line in lines:
                # Skip lines that look like headers/footers (too short, all caps, etc.)
                if len(line) > 20 and not line.isupper():
                    return line

    extraction_info.warnings.append("Could not reliably extract title from PDF")
    return ""


def _extract_authors(
    doc: fitz.Document, extraction_info: ExtractionInfo
) -> List[Author]:
    """
    Extract authors from first page (best-effort).

    Args:
        doc: PyMuPDF document
        extraction_info: Extraction info for warning logging

    Returns:
        List of Author objects (may be empty)
    """
    # AI NOTE: Author extraction from PDF is heuristic-based and often imperfect.
    # Look for patterns like "Author1, Author2, and Author3" on the first page.

    if doc.page_count == 0:
        extraction_info.warnings.append("No pages in PDF for author extraction")
        return []

    page = doc[0]
    text = page.get_text()

    if not text or not isinstance(text, str):
        extraction_info.warnings.append(
            "Could not extract text from first page for author extraction"
        )
        return []

    # Look for author patterns
    # Common patterns: "Author1, Author2, Author3" or "Author1 and Author2"
    authors: List[Author] = []

    # Try to find a line with multiple names
    lines = text.split("\n")
    for i, line in enumerate(lines[:20]):  # Check first 20 lines only
        if not isinstance(line, str):
            continue

        line = line.strip()

        # Skip title-like lines
        if line.isupper() or len(line) < 10:
            continue

        # Look for comma-separated names or "and" separator
        if "," in line or " and " in line.lower():
            # Split by comma or " and " (case-insensitive to match the condition)
            name_parts = re.split(r",|\s+and\s+", line, flags=re.IGNORECASE)

            for part in name_parts:
                part = part.strip()
                # Filter out common false positives
                if len(part) > 3 and len(part) < 50:
                    if not any(
                        keyword in part.lower()
                        for keyword in ["university", "institute", "department"]
                    ):
                        authors.append(Author(name=part))

            if authors:
                break

    if not authors:
        extraction_info.warnings.append("Could not reliably extract authors from PDF")

    return authors


def _extract_abstract(doc: fitz.Document, extraction_info: ExtractionInfo) -> str:
    """
    Extract abstract from PDF (best-effort).

    Args:
        doc: PyMuPDF document
        extraction_info: Extraction info for warning logging

    Returns:
        Abstract text (may be empty)
    """
    # AI NOTE: Abstract detection is heuristic. Look for "Abstract" heading
    # followed by text that isn't a section header.

    for page in doc[: min(3, doc.page_count)]:  # Check first 3 pages
        text = page.get_text()

        if not text or not isinstance(text, str):
            continue

        # Look for "Abstract" heading
        abstract_match = re.search(
            r"(?:^|\n)\s*[Aa]bstract\s*[:.\-]*\s*\n\s*([^\n]+(?:\n[^\n]+)*)", text
        )

        if abstract_match:
            abstract = abstract_match.group(1).strip()
            # Remove section headings that might have been captured
            abstract = re.sub(r"\n\s*\d+\.\s*[A-Z][^\n]*", "", abstract)
            abstract = abstract.strip()
            return abstract[:2000]  # Limit length

    extraction_info.warnings.append("Could not reliably extract abstract from PDF")
    return ""


def _extract_sections(
    doc: fitz.Document, extraction_info: ExtractionInfo
) -> List[Section]:
    """
    Extract sections from PDF document body.

    Args:
        doc: PyMuPDF document
        extraction_info: Extraction info for warning logging

    Returns:
        List of Section objects
    """
    # AI NOTE: Section detection is pattern-based. Look for numbered sections
    # (1., 2., etc.), ALL CAPS headings, or bold/underlined text that
    # looks like a section heading. Most-specific patterns first so that
    # "1.2.3. Subsubsection" matches level 3 before "1.2." matches level 2.

    sections: List[Section] = []

    # Section heading patterns, ordered most-specific first
    section_patterns = [
        (r"^\d+\.\d+\.\d+\.\s+[A-Z][^\n]*", 3),  # Subsubsection: "1.1.1. Details"
        (r"^\d+\.\d+\.\s+[A-Z][^\n]*", 2),        # Subsection: "1.1. Background"
        (r"^\d+\.\s+[A-Z][^\n]+", 1),              # Numbered: "1. Introduction"
        (r"^[A-Z][A-Z\s]+$", 2),                   # ALL CAPS: "INTRODUCTION"
        (r"^[IVX]+\.\s+[A-Z][^\n]+", 1),           # Roman numeral: "I. Introduction"
    ]

    current_section: Optional[Dict[str, Any]] = None
    current_content: List[str] = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text()

        if not text or not isinstance(text, str):
            continue

        lines = text.split("\n")

        for line in lines:
            if not isinstance(line, str):
                continue

            line = line.strip()

            # Check if this line is a section heading
            is_section = False
            section_level = 1
            section_title = ""

            for pattern, level in section_patterns:
                match = re.match(pattern, line)
                if match:
                    is_section = True
                    section_level = level
                    section_title = match.group(0).strip()
                    break

            if is_section and section_title:
                # Save previous section
                if current_section:
                    content = "\n".join(current_content).strip()
                    if content:
                        sections.append(
                            Section(
                                title=current_section["title"],
                                path=current_section["title"],
                                level=current_section["level"],
                                content=content,
                            )
                        )

                # Start new section
                current_section = {"title": section_title, "level": section_level}
                current_content = []
            elif current_section:
                # Add line to current section content
                current_content.append(line)

    # Save final section
    if current_section:
        content = "\n".join(current_content).strip()
        if content:
            sections.append(
                Section(
                    title=current_section["title"],
                    path=current_section["title"],
                    level=current_section["level"],
                    content=content,
                )
            )

    if not sections:
        extraction_info.warnings.append("Could not reliably detect sections in PDF")

    return sections


def _extract_references(doc: fitz.Document, extraction_info: ExtractionInfo) -> dict:
    """
    Extract references from PDF final pages (best-effort).

    Args:
        doc: PyMuPDF document
        extraction_info: Extraction info for warning logging

    Returns:
        Dictionary of references (may be empty)
    """
    # AI NOTE: Reference extraction from PDF is difficult. This is a best-effort
    # attempt that looks for bibliography sections and parses entries.

    # Look for bibliography section in final pages
    bib_start_page = -1

    for page_num in range(max(0, doc.page_count - 5), doc.page_count):
        page = doc[page_num]
        text = page.get_text()

        if not text or not isinstance(text, str):
            continue

        text_lower = text.lower()

        # Common bibliography heading patterns
        if any(
            pattern in text_lower
            for pattern in ["references", "bibliography"]
        ):
            bib_start_page = page_num
            break

    if bib_start_page == -1:
        extraction_info.warnings.append("Could not locate bibliography in PDF")
        return {}

    # Extract references from bibliography section
    references = {}
    ref_pattern = re.compile(r"^\[(\d+)\]\s+(.+)$", re.MULTILINE)

    for page_num in range(bib_start_page, doc.page_count):
        page = doc[page_num]
        text = page.get_text()

        if not text or not isinstance(text, str):
            continue

        for match in ref_pattern.finditer(text):
            ref_num = match.group(1)
            ref_text = match.group(2).strip()

            references[f"ref_{ref_num}"] = Reference(
                cite_key=f"ref_{ref_num}",
                authors=ref_text[:50],  # Best-effort
                title="",
                year="",
                journal=None,
                raw=ref_text,
            )

    if not references:
        extraction_info.warnings.append(
            "Could not parse references from PDF bibliography"
        )

    return references
