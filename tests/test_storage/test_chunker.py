"""
Tests for chunker module (unit tests, no DB required).
"""

import pytest

from src.storage.chunker import chunk_paper
from src.logging_config import setup_logging

setup_logging()


def test_chunk_paper_with_real_data():
    """Test chunking with real extracted paper data."""
    import json
    from pathlib import Path

    # Load seed paper extraction
    json_path = Path("test_output/extracted/2411.00148/extracted.json")

    if not json_path.exists():
        pytest.skip(f"Extraction JSON not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        extracted_paper = json.load(f)

    # Chunk the paper
    chunks = chunk_paper(extracted_paper)

    # Assertions
    assert len(chunks) > 10, f"Should have >10 chunks, got {len(chunks)}"

    # Each chunk should have required fields
    for chunk in chunks:
        assert "paper_id" in chunk, "Chunk should have paper_id"
        assert "content" in chunk, "Chunk should have content"
        assert "context_preamble" in chunk, "Chunk should have context_preamble"
        assert "section_path" in chunk, "Chunk should have section_path"
        assert "section_level" in chunk, "Chunk should have section_level"
        assert "chunk_index" in chunk, "Chunk should have chunk_index"

    # Check first chunk
    assert "DESIVAST" in chunks[0]["context_preamble"], (
        "Context should include paper title"
    )
    assert "2411.00148" == chunks[0]["paper_id"], "paper_id should match arxiv_id"

    # Check non-empty content
    for chunk in chunks:
        assert chunk["content"].strip(), (
            f"Chunk content should be non-empty, got: {chunk['content'][:50]}"
        )


def test_chunk_preserves_section_boundaries():
    """Test that chunking respects section boundaries."""
    test_paper = {
        "title": "Test Paper",
        "arxiv_id": "test.12345",
        "sections": [
            {
                "title": "Introduction",
                "path": "Introduction",
                "level": 1,
                "content": "This is the introduction. " * 100,  # Short section
            },
            {
                "title": "Methods",
                "path": "Methods",
                "level": 1,
                "content": "This is the methods section. " * 100,  # Short section
            },
        ],
    }

    chunks = chunk_paper(test_paper)

    # Should have chunks from both sections
    section_paths = [chunk["section_path"] for chunk in chunks]
    assert "Introduction" in section_paths, "Should have Introduction chunks"
    assert "Methods" in section_paths, "Should have Methods chunks"


def test_chunk_with_long_section():
    """Test that long sections are split into multiple chunks."""
    test_paper = {
        "title": "Test Paper",
        "arxiv_id": "test.12345",
        "sections": [
            {
                "title": "Long Section",
                "path": "Long Section",
                "level": 1,
                "content": "This is a very long section. " * 200,  # Long section
            }
        ],
    }

    chunks = chunk_paper(test_paper)

    # Should have multiple chunks from the long section
    long_section_chunks = [
        chunk for chunk in chunks if chunk["section_path"] == "Long Section"
    ]

    assert len(long_section_chunks) > 1, (
        f"Long section should be split into >1 chunk, got {len(long_section_chunks)}"
    )

    # Chunks should be ordered
    chunk_indices = [chunk["chunk_index"] for chunk in long_section_chunks]
    assert chunk_indices == sorted(chunk_indices), (
        "Chunks should be ordered by chunk_index"
    )


def test_chunk_empty_section():
    """Test that empty sections are skipped."""
    test_paper = {
        "title": "Test Paper",
        "arxiv_id": "test.12345",
        "sections": [
            {
                "title": "Empty Section",
                "path": "Empty Section",
                "level": 1,
                "content": "",  # Empty section
            },
            {
                "title": "Normal Section",
                "path": "Normal Section",
                "level": 1,
                "content": "This is a normal section.",
            },
        ],
    }

    chunks = chunk_paper(test_paper)

    # Empty section should be skipped
    section_paths = [chunk["section_path"] for chunk in chunks]
    assert "Empty Section" not in section_paths, "Empty section should be skipped"
    assert "Normal Section" in section_paths, "Normal section should be included"


def test_chunk_context_preamble():
    """Test that context preamble is correctly formatted."""
    test_paper = {
        "title": "Test Paper Title",
        "arxiv_id": "test.12345",
        "sections": [
            {
                "title": "Introduction",
                "path": "Methods > Void-Finding Algorithm",
                "level": 2,
                "content": "Section content here.",
            }
        ],
    }

    chunks = chunk_paper(test_paper)

    # Check context preamble format
    expected_preamble = (
        "From 'Test Paper Title', section: Methods > Void-Finding Algorithm"
    )
    assert chunks[0]["context_preamble"] == expected_preamble, (
        f"Context preamble should match, got: {chunks[0]['context_preamble']}"
    )
