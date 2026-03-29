"""
Full ingestion pipeline: paper JSON → chunks → embeddings → database.

Orchestrates the complete ingestion process from extracted paper JSON
to populated database tables with chunked and embedded content.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List

import psycopg2
from psycopg2.extras import execute_values

from .chunker import chunk_paper
from .db import get_connection
from .embedder import embed_chunks

logger = logging.getLogger(__name__)


def ingest_paper(extracted_json_path: Path) -> None:
    """
    Ingest an extracted paper JSON file into the database.

    This function:
    1. Loads the JSON file
    2. Inserts paper metadata into papers table
    3. Chunks the paper into text pieces
    4. Generates embeddings for all chunks
    5. Inserts chunks with embeddings into chunks table

    Args:
        extracted_json_path: Path to extracted.json file from extraction pipeline

    Raises:
        FileNotFoundError: If JSON file does not exist
        Exception: If ingestion fails (database, embedding, etc.)
    """
    # AI NOTE: This is the main entry point for paper ingestion.
    # It's idempotent - running twice on the same paper will fail the
    # UNIQUE constraint on arxiv_id and log a warning rather than duplicate.

    extracted_json_path = Path(extracted_json_path)

    if not extracted_json_path.exists():
        raise FileNotFoundError(f"Extracted JSON not found: {extracted_json_path}")

    logger.info(f"Ingesting paper from: {extracted_json_path}")

    # Load extracted paper JSON
    with open(extracted_json_path, "r", encoding="utf-8") as f:
        extracted_paper = json.load(f)

    arxiv_id = extracted_paper.get("arxiv_id")
    title = extracted_paper.get("title")

    logger.info(f"Processing paper: {arxiv_id} - {title}")

    # Get database connection
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            # Step 1: Insert paper metadata (idempotent via arxiv_id UNIQUE constraint)
            _insert_paper(cur, extracted_paper)

            # Get paper_id from database (auto-generated SERIAL)
            cur.execute("SELECT id FROM papers WHERE arxiv_id = %s", (arxiv_id,))
            paper_id = cur.fetchone()[0]

            logger.info(f"Paper inserted with id: {paper_id}")

            # Step 2: Chunk the paper
            chunks = chunk_paper(extracted_paper)
            logger.info(f"Created {len(chunks)} chunks")

            # Step 3: Generate embeddings
            embeddings = embed_chunks(chunks, batch_size=32)
            logger.info(f"Generated {len(embeddings)} embeddings")

            # Step 4: Insert chunks with embeddings
            _insert_chunks(cur, paper_id, chunks, embeddings)

            logger.info(
                f"Successfully ingested {len(chunks)} chunks for paper {arxiv_id}"
            )

        # Commit all changes
        conn.commit()
        logger.info(f"Committed ingestion for {arxiv_id}")

    except psycopg2.IntegrityError as e:
        # Likely UNIQUE constraint violation on arxiv_id
        if "arxiv_id" in str(e) or "duplicate key" in str(e).lower():
            logger.warning(f"Paper {arxiv_id} already exists in database, skipping")
            conn.rollback()
        else:
            logger.error(f"Integrity error during ingestion: {e}")
            conn.rollback()
            raise

    except Exception as e:
        logger.error(f"Ingestion failed for {arxiv_id}: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


def _insert_paper(cur: psycopg2.extensions.cursor, extracted_paper: Dict) -> None:
    """
    Insert paper metadata into papers table.

    Args:
        cur: Database cursor
        extracted_paper: Extracted paper dictionary
    """
    # AI NOTE: Uses INSERT ... ON CONFLICT DO NOTHING for idempotency.
    # If arxiv_id already exists, the insert is skipped silently.
    # The arxiv_id UNIQUE constraint ensures no duplicates.

    query = """
        INSERT INTO papers (
            arxiv_id,
            bibcode,
            title,
            abstract,
            authors,
            sections,
            paper_references,
            extraction_method,
            source_file,
            extracted_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (arxiv_id) DO NOTHING
    """

    cur.execute(
        query,
        (
            extracted_paper.get("arxiv_id"),
            extracted_paper.get("bibcode"),
            extracted_paper.get("title"),
            extracted_paper.get("abstract"),
            json.dumps(extracted_paper.get("authors", [])),
            json.dumps(extracted_paper.get("sections", [])),
            json.dumps(extracted_paper.get("references", {})),
            extracted_paper.get("extraction_info", {}).get("method"),
            extracted_paper.get("extraction_info", {}).get("source_file"),
            extracted_paper.get("extraction_info", {}).get("timestamp"),
        ),
    )


def _insert_chunks(
    cur: psycopg2.extensions.cursor,
    paper_id: int,
    chunks: List[Dict],
    embeddings: List,
) -> None:
    """
    Insert chunks with embeddings into chunks table.

    Args:
        cur: Database cursor
        paper_id: Foreign key to papers table
        chunks: List of chunk dictionaries
        embeddings: List of numpy embedding arrays
    """
    # AI NOTE: Uses execute_values for efficient batch insert of chunks.
    # The search_vector tsvector column is automatically populated by the
    # chunks_search_vector_update trigger - do NOT set it manually.
    # Metadata is stored as JSONB with token_count and char_count.

    # Prepare data for batch insert
    data = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        content = chunk.get("content", "")
        metadata = {
            "token_count": _estimate_tokens(content),
            "char_count": len(content),
            "overlap_tokens": 50,  # From chunker configuration
        }

        data.append(
            (
                paper_id,
                i,  # chunk_index
                content,
                chunk.get("context_preamble", ""),
                chunk.get("section_path", ""),
                chunk.get("section_level", 1),
                embedding.tolist(),  # Convert numpy array to list for psycopg2
                json.dumps(metadata),
            )
        )

    # Batch insert using execute_values for efficiency
    query = """
        INSERT INTO chunks (
            paper_id,
            chunk_index,
            content,
            context_preamble,
            section_path,
            section_level,
            embedding,
            metadata
        ) VALUES %s
    """

    execute_values(cur, query, data, template=None, page_size=len(data))


def _estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count (4 chars ≈ 1 token)
    """
    # AI NOTE: Simple character-based estimation is sufficient for metadata.
    # 4 characters ≈ 1 token is a reasonable approximation for English text.
    return len(text) // 4
