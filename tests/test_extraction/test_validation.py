"""
Output quality validation tests for extraction.

These tests validate the quality of extracted papers, ensuring structural
completeness, content fidelity, and correctness. They serve as acceptance
criteria for the Phase 04 milestone.
"""

import json
from pathlib import Path

import pytest
from src.extraction.pipeline import extract_paper
from src.logging_config import setup_logging

setup_logging()


def test_structural_completeness():
    """Test that extracted paper has all required fields."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON for validation
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # All top-level keys present
    assert "arxiv_id" in data, "arxiv_id should be present"
    assert "title" in data, "title should be present"
    assert "authors" in data, "authors should be present"
    assert "abstract" in data, "abstract should be present"
    assert "sections" in data, "sections should be present"
    assert "references" in data, "references should be present"
    assert "custom_commands" in data, "custom_commands should be present"
    assert "extraction_info" in data, "extraction_info should be present"

    # All fields non-empty (except lists/dicts which can be empty)
    assert data["arxiv_id"], "arxiv_id should be non-empty"
    assert data["title"], "title should be non-empty"
    assert isinstance(data["authors"], list), "authors should be a list"
    assert isinstance(data["sections"], list), "sections should be a list"
    assert isinstance(data["references"], dict), "references should be a dict"
    assert isinstance(data["custom_commands"], dict), "custom_commands should be a dict"


def test_author_fidelity():
    """Test that authors are correctly extracted."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Author count - DESI paper has >30 authors
    authors = data["authors"]
    assert len(authors) > 30, f"Author count should be >30, got {len(authors)}"

    # First author should contain "Rincon"
    assert "Rincon" in authors[0]["name"], (
        f"First author should contain 'Rincon', got {authors[0]['name']}"
    )


def test_section_coverage():
    """Test that major sections are present."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sections = data["sections"]
    section_titles = [s["title"].lower() for s in sections]

    # Check for major sections (allow some variation in naming)
    has_intro = any("intro" in title for title in section_titles)
    has_data = any("data" in title for title in section_titles)
    has_conclusions = any("concl" in title for title in section_titles)

    assert has_intro, "Should have an Introduction section"
    assert has_data, "Should have a Data section"
    assert has_conclusions, "Should have a Conclusions section"


def test_section_ordering():
    """Test that sections appear in document order."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sections = data["sections"]
    section_titles = [s["title"].lower() for s in sections]

    # Introduction should come before Conclusions — capture first occurrence
    intro_index = -1
    conclusions_index = -1

    for i, title in enumerate(section_titles):
        if "intro" in title and intro_index == -1:
            intro_index = i
        if "concl" in title and conclusions_index == -1:
            conclusions_index = i

    assert intro_index >= 0, "Introduction section not found"
    assert conclusions_index >= 0, "Conclusions section not found"
    assert intro_index < conclusions_index, (
        "Introduction should come before Conclusions"
    )


def test_math_preservation():
    """Test that math notation is preserved."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Combine all section content
    all_content = "".join(s["content"] for s in data["sections"])

    # Count math notation occurrences
    dollar_count = all_content.count("$")
    assert dollar_count >= 10, f"Should have at least 10 $ symbols, got {dollar_count}"


def test_custom_command_expansion():
    """Test that custom commands are expanded in section content."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Combine all section content
    all_content = "".join(s["content"] for s in data["sections"])

    # No raw custom commands in section content
    assert r"\hMpc" not in all_content, "Raw \\hMpc should not appear in sections"
    assert r"\Vsquared" not in all_content, (
        "Raw \\Vsquared should not appear in sections"
    )


def test_no_frontmatter_bleed():
    """Test that frontmatter content doesn't bleed into sections."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Combine all section content
    all_content = "".join(s["content"] for s in data["sections"])

    # No email commands in section content
    assert r"\email" not in all_content, (
        "Frontmatter \\email should not appear in sections"
    )


def test_no_float_bleed():
    """Test that figure/table floats don't appear in section content."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check each section
    for section in data["sections"]:
        content = section["content"]
        assert r"\begin{figure}" not in content, (
            f"Section '{section['title']}' should not contain \\begin{{figure}}"
        )
        assert r"\includegraphics" not in content, (
            f"Section '{section['title']}' should not contain \\includegraphics"
        )


def test_reference_completeness():
    """Test that references are extracted."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # This paper has extensive bibliography (>50 references)
    references = data["references"]
    assert len(references) > 50, f"Should have >50 references, got {len(references)}"


def test_reference_quality():
    """Test that references have reasonable quality."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Count high-quality references (have authors, title, year)
    references = data["references"]
    high_quality_count = sum(
        1
        for ref in references.values()
        if ref.get("authors") and ref.get("title") and ref.get("year")
    )

    quality_ratio = high_quality_count / len(references) if references else 0
    assert quality_ratio >= 0.8, (
        f"At least 80% of references should be complete, got {quality_ratio:.2%}"
    )


def test_abstract_content():
    """Test that abstract contains expected content."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    abstract = data["abstract"].lower()

    # Should contain key phrases
    assert "void" in abstract, "Abstract should contain 'void'"
    assert "catalog" in abstract, "Abstract should contain 'catalog'"
    assert "desi" in abstract, "Abstract should contain 'desi'"
    assert "dr1" in abstract, "Abstract should contain 'dr1'"


def test_json_roundtrip():
    """Test that JSON can be loaded and has correct types."""
    source_dir = Path("test_output/extracted/2411.00148")

    if not source_dir.exists():
        pytest.skip(f"Source directory not found: {source_dir}")

    # Load from JSON
    json_path = source_dir / "extracted.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Verify types
    assert isinstance(data["arxiv_id"], str), "arxiv_id should be string"
    assert isinstance(data["title"], str), "title should be string"
    assert isinstance(data["abstract"], str), "abstract should be string"
    assert isinstance(data["authors"], list), "authors should be list"
    assert isinstance(data["sections"], list), "sections should be list"
    assert isinstance(data["references"], dict), "references should be dict"
    assert isinstance(data["custom_commands"], dict), "custom_commands should be dict"
    assert isinstance(data["extraction_info"], dict), "extraction_info should be dict"
