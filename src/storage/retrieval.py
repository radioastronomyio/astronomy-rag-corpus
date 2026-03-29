"""
Hybrid retrieval with dense + sparse + Reciprocal Rank Fusion.

Combines vector similarity search and full-text search using RRF
to provide high-quality ranked results.
"""

import logging
from typing import Any, Dict, List

import psycopg2
from psycopg2 import extras
from sentence_transformers import SentenceTransformer

from .db import get_connection
from .embedder import MODEL_NAME, get_embedding_dimension

logger = logging.getLogger(__name__)

# RRF constant (k=60 as per RRF formula)
RRF_K = 60


def hybrid_search(query: str, top_k: int = 10) -> List[Dict]:
    """
    Perform hybrid search combining dense vector and sparse full-text search.

    Uses Reciprocal Rank Fusion (RRF) to merge dense and sparse results:
    score(dense) + score(sparse) where score = 1 / (k + rank)

    Args:
        query: User search query
        top_k: Number of results to return (default 10)

    Returns:
        List of result dictionaries sorted by RRF score, each with:
        - chunk_id: Chunk database ID
        - content: Chunk text content
        - context_preamble: Context preamble
        - section_path: Section path
        - paper_title: Paper title
        - arxiv_id: Paper arXiv ID
        - paper_id: Paper database ID
        - rrf_score: Combined RRF score
        - dense_rank: Rank in dense search
        - sparse_rank: Rank in sparse search
    """
    # AI NOTE: Hybrid retrieval with RRF is baseline expectation, not an
    # advanced option. The combination of semantic (dense) and keyword (sparse)
    # search provides better recall than either alone, and RRF provides a principled
    # ranking method that doesn't require training data.

    logger.info(f"Hybrid search for query: '{query}' (top_k={top_k})")

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            # Step 1: Dense vector search (semantic similarity)
            dense_results = _dense_search(cur, query, top_k * 2)  # Get more for RRF
            logger.info(f"Dense search returned {len(dense_results)} results")

            # Step 2: Sparse full-text search (BM25/ts_rank)
            sparse_results = _sparse_search(cur, query, top_k * 2)  # Get more for RRF
            logger.info(f"Sparse search returned {len(sparse_results)} results")

            # Step 3: Reciprocal Rank Fusion
            fused_results = _reciprocal_rank_fusion(dense_results, sparse_results)

            # Sort by RRF score and limit to top_k
            fused_results.sort(key=lambda x: x["rrf_score"], reverse=True)
            fused_results = fused_results[:top_k]

            # Enrich results with paper metadata
            _enrich_with_paper_metadata(cur, fused_results)

            logger.info(f"Returning {len(fused_results)} fused results")
            return fused_results

    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        raise

    finally:
        conn.close()


def _dense_search(cur: Any, query: str, limit: int) -> List[Dict]:
    """
    Perform dense vector similarity search.

    Args:
        cur: Database cursor
        query: Search query
        limit: Maximum results to return

    Returns:
        List of results with rank
    """
    # AI NOTE: Embeds the query using the same model as document embeddings.
    # Uses cosine distance (<=>) for vector similarity search against the
    # HNSW index idx_chunks_embedding.

    # Load model and embed query
    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode(query, normalize_embeddings=True)

    # Vector similarity search using pgvector <-> operator (cosine distance)
    search_query = """
        SELECT
            c.id,
            c.content,
            c.context_preamble,
            c.section_path,
            p.title,
            p.arxiv_id,
            c.paper_id
        FROM chunks c
        JOIN papers p ON c.paper_id = p.id
        WHERE c.embedding <-> %s::vector
        ORDER BY c.embedding <-> %s::vector
        LIMIT %s
    """

    cur.execute(
        search_query, (query_embedding.tolist(), query_embedding.tolist(), limit)
    )

    results = []
    for rank, row in enumerate(cur.fetchall(), start=1):
        results.append(
            {
                "chunk_id": row[0],
                "content": row[1],
                "context_preamble": row[2],
                "section_path": row[3],
                "paper_title": row[4],
                "arxiv_id": row[5],
                "paper_id": row[6],
                "dense_rank": rank,
                "sparse_rank": None,  # Will be filled by fusion
            }
        )

    return results


def _sparse_search(cur: Any, query: str, limit: int) -> List[Dict]:
    """
    Perform sparse full-text search using ts_rank.

    Args:
        cur: Database cursor
        query: Search query
        limit: Maximum results to return

    Returns:
        List of results with rank
    """
    # AI NOTE: Uses PostgreSQL's ts_rank function for BM25 ranking against
    # the search_vector tsvector column. This column is automatically populated
    # by the chunks_search_vector_update trigger - do NOT set it manually.
    # Uses plainto_tsquery for simple case-insensitive search.

    search_query = """
        SELECT
            c.id,
            c.content,
            c.context_preamble,
            c.section_path,
            p.title,
            p.arxiv_id,
            c.paper_id
        FROM chunks c
        JOIN papers p ON c.paper_id = p.id
        WHERE c.search_vector @@ plainto_tsquery('english', %s)
        ORDER BY ts_rank(c.search_vector, plainto_tsquery('english', %s))
        LIMIT %s
    """

    cur.execute(search_query, (query, query, limit))

    results = []
    for rank, row in enumerate(cur.fetchall(), start=1):
        results.append(
            {
                "chunk_id": row[0],
                "content": row[1],
                "context_preamble": row[2],
                "section_path": row[3],
                "paper_title": row[4],
                "arxiv_id": row[5],
                "paper_id": row[6],
                "dense_rank": None,  # Will be filled by fusion
                "sparse_rank": rank,
            }
        )

    return results


def _reciprocal_rank_fusion(
    dense_results: List[Dict], sparse_results: List[Dict]
) -> List[Dict]:
    """
    Merge dense and sparse results using Reciprocal Rank Fusion.

    Args:
        dense_results: Results from dense vector search
        sparse_results: Results from sparse full-text search

    Returns:
        List of fused results sorted by RRF score
    """
    # AI NOTE: RRF formula: score = 1 / (k + rank) where k=60.
    # This gives higher scores to results that appear earlier in either ranking.
    # Each unique chunk (by chunk_id) gets one RRF score.

    # Build lookup by chunk_id
    sparse_by_id = {r["chunk_id"]: r for r in sparse_results}

    fused = {}

    # Process dense results
    for result in dense_results:
        chunk_id = result["chunk_id"]
        dense_rank = result["dense_rank"]

        # Calculate dense score: 1 / (k + rank)
        dense_score = 1 / (RRF_K + dense_rank)

        if chunk_id in fused:
            # Already seen (appears in both rankings)
            sparse_result = sparse_by_id.get(chunk_id)
            if sparse_result:
                sparse_rank = sparse_result["sparse_rank"]
                sparse_score = 1 / (RRF_K + sparse_rank)
                fused[chunk_id]["rrf_score"] += sparse_score
                fused[chunk_id]["sparse_rank"] = sparse_rank
        else:
            # Only in dense
            result["rrf_score"] = dense_score
            result["sparse_rank"] = None
            fused[chunk_id] = result

    # Process sparse results (only those not already seen)
    for result in sparse_results:
        chunk_id = result["chunk_id"]

        if chunk_id not in fused:
            # Only in sparse
            sparse_rank = result["sparse_rank"]
            sparse_score = 1 / (RRF_K + sparse_rank)

            result["rrf_score"] = sparse_score
            fused[chunk_id] = result

    return list(fused.values())


def _enrich_with_paper_metadata(cur: Any, results: List[Dict]) -> None:
    """
    Enrich results with additional paper metadata if needed.

    Args:
        cur: Database cursor
        results: Results list to enrich in-place
    """
    # AI NOTE: Currently only paper title and arxiv_id are included from
    # the JOIN. Future expansion could include bibcode, abstract preview, etc.
    # This function is a placeholder for that future enhancement.

    # Results already have paper_title and arxiv_id from the JOIN queries
    # Nothing additional to fetch at this time
    pass
