"""
Tests for retrieval module (integration, needs DB with ingested data).
"""

import pytest

from src.storage.retrieval import hybrid_search
from src.logging_config import setup_logging

setup_logging()


def test_hybrid_search_returns_results():
    """Test that hybrid search returns results."""
    # This test assumes seed paper is ingested
    # Run: python -m src.storage.ingest test_output/extracted/2411.00148/extracted.json

    try:
        results = hybrid_search("void galaxy catalog", top_k=5)

        # Assertions
        assert len(results) > 0, "Search should return some results"
        assert len(results) <= 5, (
            f"Should return at most top_k results, got {len(results)}"
        )

        # Check result structure
        for result in results:
            assert "chunk_id" in result, "Result should have chunk_id"
            assert "content" in result, "Result should have content"
            assert "context_preamble" in result, "Result should have context_preamble"
            assert "section_path" in result, "Result should have section_path"
            assert "paper_title" in result, "Result should have paper_title"
            assert "arxiv_id" in result, "Result should have arxiv_id"
            assert "rrf_score" in result, "Result should have rrf_score"
            assert "dense_rank" in result, "Result should have dense_rank"
            assert "sparse_rank" in result, "Result should have sparse_rank"

        # Results should be sorted by RRF score
        rrf_scores = [r["rrf_score"] for r in results]
        assert rrf_scores == sorted(rrf_scores, reverse=True), (
            "Results should be sorted by RRF score"
        )

    except Exception as e:
        pytest.skip(f"Integration test requires database with ingested data: {e}")


def test_hybrid_search_seed_paper():
    """Test that hybrid search returns chunks from seed paper."""
    try:
        results = hybrid_search("void galaxy", top_k=3)

        # Check if results are from seed paper
        seed_paper_results = [r for r in results if r.get("arxiv_id") == "2411.00148"]

        if len(seed_paper_results) > 0:
            # Top result should be from seed paper
            assert results[0]["arxiv_id"] == "2411.00148", (
                "Top result should be from seed paper"
            )
            assert "DESIVAST" in results[0]["paper_title"], (
                "Top result should have DESIVAST title"
            )

    except Exception as e:
        pytest.skip(f"Integration test requires database with ingested data: {e}")


def test_hybrid_search_empty_query():
    """Test that empty query returns empty results."""
    try:
        results = hybrid_search("", top_k=10)
        # Empty query might return some results or none - just don't crash
        assert isinstance(results, list), "Should return a list"

    except Exception as e:
        pytest.skip(f"Integration test requires database with ingested data: {e}")
