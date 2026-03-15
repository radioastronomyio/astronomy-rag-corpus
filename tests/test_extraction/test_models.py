"""
Tests for extraction data models.
"""

import json

from src.extraction.models import (
    Author,
    ExtractionInfo,
    ExtractedPaper,
    Reference,
    Section,
    save_json,
)
from src.logging_config import setup_logging

setup_logging()


def test_author_defaults():
    """Test that Author dataclass has correct defaults."""
    author = Author(name="Test Author")
    assert author.name == "Test Author"
    assert author.orcid is None
    assert author.affiliations == []
    assert author.email is None


def test_section_defaults():
    """Test that Section dataclass has correct defaults."""
    section = Section(title="Test Section", path="Test", level=1, content="Content")
    assert section.title == "Test Section"
    assert section.path == "Test"
    assert section.level == 1
    assert section.content == "Content"
    assert section.label is None


def test_reference_defaults():
    """Test that Reference dataclass has correct defaults."""
    ref = Reference(cite_key="key1", authors="Author", title="Title", year="2024")
    assert ref.cite_key == "key1"
    assert ref.authors == "Author"
    assert ref.title == "Title"
    assert ref.year == "2024"
    assert ref.journal is None
    assert ref.raw == ""


def test_extraction_info_defaults():
    """Test that ExtractionInfo dataclass has correct defaults."""
    info = ExtractionInfo(
        method="latex", source_file="test.tex", timestamp="2024-01-01T00:00:00+00:00"
    )
    assert info.method == "latex"
    assert info.source_file == "test.tex"
    assert info.timestamp == "2024-01-01T00:00:00+00:00"
    assert info.warnings == []
    assert info.pylatexenc_version is None


def test_extracted_paper_to_dict_roundtrip():
    """Test that ExtractedPaper.to_dict() produces JSON-serializable output."""
    paper = ExtractedPaper(
        arxiv_id="2411.00148",
        title="Test Paper",
        authors=[Author(name="Author1")],
        abstract="Test abstract",
        custom_commands={"cmd1": "expansion"},
        sections=[
            Section(title="Section 1", path="Section 1", level=1, content="Content")
        ],
        references={
            "key1": Reference(
                cite_key="key1", authors="Author", title="Title", year="2024"
            )
        },
        extraction_info=ExtractionInfo(
            method="latex",
            source_file="test.tex",
            timestamp="2024-01-01T00:00:00+00:00",
        ),
    )

    result_dict = paper.to_dict()

    # Verify top-level structure
    assert "arxiv_id" in result_dict
    assert "title" in result_dict
    assert "authors" in result_dict
    assert "abstract" in result_dict
    assert "custom_commands" in result_dict
    assert "sections" in result_dict
    assert "references" in result_dict
    assert "extraction_info" in result_dict

    # Verify nested structures
    assert result_dict["arxiv_id"] == "2411.00148"
    assert result_dict["title"] == "Test Paper"
    assert len(result_dict["authors"]) == 1
    assert result_dict["authors"][0]["name"] == "Author1"
    assert result_dict["abstract"] == "Test abstract"
    assert result_dict["custom_commands"]["cmd1"] == "expansion"
    assert len(result_dict["sections"]) == 1
    assert result_dict["sections"][0]["title"] == "Section 1"
    assert "key1" in result_dict["references"]
    assert result_dict["references"]["key1"]["cite_key"] == "key1"
    assert result_dict["extraction_info"]["method"] == "latex"

    # Test JSON serialization
    json_str = json.dumps(result_dict)
    assert json_str is not None

    # Test JSON deserialization
    loaded_dict = json.loads(json_str)
    assert loaded_dict == result_dict
