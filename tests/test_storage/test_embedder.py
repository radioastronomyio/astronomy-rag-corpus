"""
Tests for embedder module (needs model download).
"""

import numpy as np
import pytest

from src.storage.embedder import embed_chunks, get_embedding_dimension
from src.logging_config import setup_logging

setup_logging()


def test_get_embedding_dimension():
    """Test that embedding dimension is correct."""
    dim = get_embedding_dimension()
    assert dim == 768, f"Embedding dimension should be 768, got {dim}"


def test_embed_chunks():
    """Test embedding generation for chunks."""
    test_chunks = [
        {
            "paper_id": "test.12345",
            "content": "Test chunk content one.",
            "context_preamble": "From 'Test Paper', section: Introduction",
            "section_path": "Introduction",
            "section_level": 1,
            "chunk_index": 0,
        },
        {
            "paper_id": "test.12345",
            "content": "Test chunk content two.",
            "context_preamble": "From 'Test Paper', section: Methods",
            "section_path": "Methods",
            "section_level": 1,
            "chunk_index": 1,
        },
        {
            "paper_id": "test.12345",
            "content": "Test chunk content three.",
            "context_preamble": "From 'Test Paper', section: Conclusions",
            "section_path": "Conclusions",
            "section_level": 1,
            "chunk_index": 2,
        },
    ]

    # Embed chunks (model will be downloaded first time)
    embeddings = embed_chunks(test_chunks, batch_size=2)

    # Assertions
    assert len(embeddings) == 3, f"Should have 3 embeddings, got {len(embeddings)}"

    for i, embedding in enumerate(embeddings):
        assert isinstance(embedding, np.ndarray), f"Embedding {i} should be numpy array"
        assert embedding.shape == (768,), (
            f"Embedding {i} should have shape (768,), got {embedding.shape}"
        )
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 0.01, (
            f"Embedding {i} should be normalized (L2 norm approx 1), got {norm}"
        )


def test_embed_empty_chunks():
    """Test embedding of empty chunk list."""
    embeddings = embed_chunks([], batch_size=32)
    assert len(embeddings) == 0, "Empty chunks should produce empty embeddings"
