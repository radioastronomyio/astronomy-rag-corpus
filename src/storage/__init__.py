"""
Storage and retrieval layer for Astronomy RAG Corpus.

Provides chunking, embedding, ingestion, and hybrid retrieval for
extracted astronomical papers.
"""

from .chunker import chunk_paper
from .db import get_connection
from .embedder import embed_chunks
from .ingest import ingest_paper
from .retrieval import hybrid_search

__all__ = [
    "get_connection",
    "chunk_paper",
    "embed_chunks",
    "ingest_paper",
    "hybrid_search",
]
