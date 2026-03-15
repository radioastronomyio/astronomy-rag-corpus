"""
Tests for LaTeX parser.
"""

from pathlib import Path

import pytest

from src.extraction.latex_parser import extract_from_latex
from src.logging_config import setup_logging

setup_logging()


def test_extract_from_latex_seed_paper():
    """Test extracting from the seed paper's .tex file."""
    tex_path = Path("test_output/extracted/2411.00148/desi_bgs_voids_y1.tex")

    if not tex_path.exists():
        pytest.skip(f"TeX file not found: {tex_path}")

    paper = extract_from_latex(tex_path, "2411.00148")

    # Verify arxiv_id
    assert paper.arxiv_id == "2411.00148"

    # Verify title contains "DESIVAST"
    assert "DESIVAST" in paper.title, f"Title should contain 'DESIVAST': {paper.title}"

    # Verify author count (large DESI collaboration paper, >30 authors)
    assert len(paper.authors) > 30, (
        f"Author count should be >30, got {len(paper.authors)}"
    )

    # Verify abstract is non-empty and contains "void catalogs"
    assert paper.abstract, "Abstract should be non-empty"
    assert "void" in paper.abstract.lower(), (
        f"Abstract should contain 'void': {paper.abstract}"
    )

    # Verify custom_commands contains "hMpc" key
    assert "hMpc" in paper.custom_commands, (
        f"custom_commands should contain 'hMpc': {paper.custom_commands.keys()}"
    )

    # Verify sections list is non-empty
    assert len(paper.sections) > 0, "Sections list should be non-empty"

    # Verify first section title is "Introduction"
    assert paper.sections[0].title == "Introduction", (
        f"First section title should be 'Introduction', got '{paper.sections[0].title}'"
    )

    # Verify section content contains expanded custom commands (no raw \hMpc)
    for section in paper.sections:
        if section.content:
            assert r"\hMpc" not in section.content, (
                f"Section content should not contain raw '\\hMpc': {section.content[:100]}"
            )

    # Verify math notation is preserved (at least one section contains $ expressions)
    has_math = False
    for section in paper.sections:
        if section.content and "$" in section.content:
            has_math = True
            break
    assert has_math, "At least one section should contain math notation ($...$)"

    # Verify no \begin{figure} text in any section content
    for section in paper.sections:
        if section.content:
            assert r"\begin{figure}" not in section.content, (
                f"Section content should not contain '\\begin{{figure}}': {section.content[:100]}"
            )
            assert r"\begin{table}" not in section.content, (
                f"Section content should not contain '\\begin{{table}}': {section.content[:100]}"
            )

    # Verify section paths are correctly formed (at least one contains " > ")
    has_nested_path = any(" > " in section.path for section in paper.sections)
    assert has_nested_path, (
        "At least one section should have a nested path containing ' > '"
    )


def test_extract_from_latex_file_not_found():
    """Test that FileNotFoundError is raised for non-existent file."""
    tex_path = Path("nonexistent/file.tex")

    with pytest.raises(FileNotFoundError):
        extract_from_latex(tex_path, "2411.00148")
