"""
Data models for LaTeX paper extraction.

Defines structured dataclasses for representing parsed LaTeX papers,
including authors, sections, references, and extraction metadata.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Author:
    """
    Represents an author from a LaTeX paper.

    Attributes:
        name: Full author name
        orcid: ORCID identifier if present
        affiliations: List of institutional affiliations
        email: Email address if present
    """

    name: str
    orcid: str | None = None
    affiliations: list[str] = field(default_factory=list)
    email: str | None = None


@dataclass
class Section:
    """
    Represents a section in a LaTeX paper.

    Attributes:
        title: Section title
        path: Hierarchical path (e.g., "Introduction" or "Methods > Void-Finding Algorithm")
        level: Nesting level (1 = section, 2 = subsection, 3 = subsubsection)
        content: Section body text with math preserved and newcommands expanded
        label: LaTeX label if present
    """

    title: str
    path: str
    level: int
    content: str
    label: str | None = None


@dataclass
class Reference:
    """
    Represents a bibliographic reference from a .bbl file.

    Attributes:
        cite_key: BibTeX citation key
        authors: Parsed author string
        title: Reference title
        year: Publication year
        journal: Journal name if present
        raw: Full raw bibitem/entry for fallback
    """

    cite_key: str
    authors: str
    title: str
    year: str
    journal: str | None = None
    raw: str = ""


@dataclass
class ExtractionInfo:
    """
    Metadata about the extraction process.

    Attributes:
        method: Extraction method ("latex" or "pdf_fallback")
        source_file: Path to source file
        timestamp: ISO 8601 timestamp of extraction
        warnings: List of warning messages generated during extraction
        pylatexenc_version: pylatexenc version used
    """

    method: str
    source_file: str
    timestamp: str
    warnings: list[str] = field(default_factory=list)
    pylatexenc_version: str | None = None


@dataclass
class ExtractedPaper:
    """
    Represents a fully extracted LaTeX paper.

    Attributes:
        arxiv_id: arXiv paper identifier
        title: Paper title
        authors: List of authors
        abstract: Paper abstract
        custom_commands: Mapping of custom LaTeX command names to their expansions
        sections: Ordered list of sections
        references: Mapping of cite_key to Reference objects
        extraction_info: Extraction metadata
    """

    arxiv_id: str
    title: str
    authors: list[Author]
    abstract: str
    custom_commands: dict[str, str]
    sections: list[Section]
    references: dict[str, Reference]
    extraction_info: ExtractionInfo

    def to_dict(self) -> dict[str, Any]:
        """
        Convert ExtractedPaper to a JSON-serializable dictionary.

        Returns:
            Dictionary representation suitable for json.dump()
        """
        # AI NOTE: This method is used for JSON serialization. If adding new
        # fields to ExtractedPaper, update this method to include them. Ensure
        # nested dataclasses are also converted recursively.
        return {
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": [
                {
                    "name": author.name,
                    "orcid": author.orcid,
                    "affiliations": author.affiliations,
                    "email": author.email,
                }
                for author in self.authors
            ],
            "abstract": self.abstract,
            "custom_commands": self.custom_commands,
            "sections": [
                {
                    "title": section.title,
                    "path": section.path,
                    "level": section.level,
                    "content": section.content,
                    "label": section.label,
                }
                for section in self.sections
            ],
            "references": {
                cite_key: {
                    "cite_key": ref.cite_key,
                    "authors": ref.authors,
                    "title": ref.title,
                    "year": ref.year,
                    "journal": ref.journal,
                    "raw": ref.raw,
                }
                for cite_key, ref in self.references.items()
            },
            "extraction_info": {
                "method": self.extraction_info.method,
                "source_file": self.extraction_info.source_file,
                "timestamp": self.extraction_info.timestamp,
                "warnings": self.extraction_info.warnings,
                "pylatexenc_version": self.extraction_info.pylatexenc_version,
            },
        }


def save_json(paper: ExtractedPaper, output_path: Path) -> None:
    """
    Save extracted paper to a JSON file.

    Args:
        paper: ExtractedPaper instance to save
        output_path: Path where JSON file will be written

    Raises:
        OSError: If file cannot be written
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Saving extracted paper to: {output_path}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(paper.to_dict(), f, indent=2, ensure_ascii=False)

    logger.info(f"Successfully saved JSON to: {output_path}")
