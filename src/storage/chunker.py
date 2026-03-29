"""
Section-boundary chunking with contextual enrichment.

Splits extracted papers into chunks at section boundaries, adding
contextual preamble for self-contained retrieval.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def chunk_paper(extracted_paper: Dict) -> List[Dict]:
    """
    Chunk an extracted paper into text chunks at section boundaries.

    Each section is chunked into approximately 512 tokens with overlap.
    Chunks include contextual preamble (paper title + section path) for
    self-contained retrieval.

    Args:
        extracted_paper: Dictionary representing an extracted paper (from ExtractedPaper.to_dict())

    Returns:
        List of chunk dictionaries with keys:
        - paper_id: arxiv_id (for foreign key reference)
        - content: Chunk text content
        - context_preamble: "From 'Paper Title', section: Section Path"
        - section_path: Section path string
        - section_level: Section nesting level (1, 2, 3)
        - chunk_index: Sequential chunk index within paper
    """
    # AI NOTE: Chunking strategy follows current best practices for scientific RAG:
    # 1. Section-boundary splitting preserves semantic coherence
    # 2. ~512 tokens per chunk fits in context windows
    # 3. Overlap between chunks prevents boundary issues
    # 4. Contextual preamble makes chunks self-contained for retrieval

    paper_title = extracted_paper.get("title", "")
    arxiv_id = extracted_paper.get("arxiv_id", "")
    sections = extracted_paper.get("sections", [])

    chunks: List[Dict[str, Any]] = []
    global_chunk_index = 0

    for section in sections:
        section_content = section.get("content", "")
        section_path = section.get("path", "")
        section_level = section.get("level", 1)

        # Skip empty sections
        if not section_content or not section_content.strip():
            logger.debug(f"Skipping empty section: {section_path}")
            continue

        # Create context preamble
        context_preamble = f"From '{paper_title}', section: {section_path}"

        # Chunk section content
        section_chunks = _split_section(
            section_content,
            max_tokens=512,
            overlap_tokens=50,
        )

        # Create chunk dictionaries
        for i, chunk_content in enumerate(section_chunks):
            chunks.append(
                {
                    "paper_id": arxiv_id,  # Will be used to lookup paper_id from DB
                    "content": chunk_content,
                    "context_preamble": context_preamble,
                    "section_path": section_path,
                    "section_level": section_level,
                    "chunk_index": global_chunk_index,
                }
            )
            global_chunk_index += 1

        logger.debug(
            f"Chunked section '{section_path}' into {len(section_chunks)} chunks "
            f"(total {global_chunk_index})"
        )

    logger.info(f"Total chunks created for {arxiv_id}: {len(chunks)}")
    return chunks


def _split_section(content: str, max_tokens: int, overlap_tokens: int) -> List[str]:
    """
    Split section content into chunks of approximately max_tokens with overlap.

    Args:
        content: Section text content
        max_tokens: Target tokens per chunk (~512)
        overlap_tokens: Tokens to overlap between chunks (~50)

    Returns:
        List of chunk strings
    """
    # AI NOTE: Simple token estimation based on characters/tokens ratio.
    # For English text, ~4 chars ≈ 1 token is a reasonable approximation.
    # This avoids the cost of a tokenizer call while being accurate enough
    # for chunking decisions.

    # Estimate tokens using character count (4 chars ≈ 1 token)
    chars_per_token = 4
    max_chars = max_tokens * chars_per_token
    overlap_chars = overlap_tokens * chars_per_token

    # Split into paragraphs first to preserve sentence boundaries
    paragraphs = content.split("\n\n")

    # Handle case with no paragraph breaks
    if len(paragraphs) == 1 and len(paragraphs[0]) > max_chars:
        # Single paragraph longer than max_chars - split by character count
        text = paragraphs[0]
        chunks = []
        start = 0
        while start < len(text):
            end = start + max_chars
            if end > len(text):
                end = len(text)
            chunks.append(text[start:end])
            start = end - overlap_chars if end > overlap_chars else start
        return chunks

    chunks: List[str] = []
    current_chunk: List[str] = []
    current_chunk_chars = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            # Empty paragraph - treat as boundary
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_chunk_chars = 0
            continue

        para_chars = len(paragraph)

        # Check if paragraph fits in current chunk
        if current_chunk_chars + para_chars <= max_chars:
            current_chunk.append(paragraph)
            current_chunk_chars += para_chars
        else:
            # Save current chunk if it exists
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))

            # Start new chunk with overlap from previous
            if chunks:
                # Get last chunk for overlap
                last_chunk = chunks[-1]
                last_paragraphs = last_chunk.split("\n\n")

                # Add last N paragraphs as overlap (preserve up to overlap_chars)
                overlap_paragraphs: List[str] = []
                overlap_chars_used = 0

                for para in reversed(last_paragraphs):
                    para_len = len(para) + 2  # +2 for "\n\n"
                    if overlap_chars_used + para_len <= overlap_chars:
                        overlap_paragraphs.insert(0, para)
                        overlap_chars_used += para_len
                    else:
                        break

                if overlap_paragraphs:
                    current_chunk = overlap_paragraphs
                    current_chunk_chars = overlap_chars_used
                else:
                    current_chunk = []
                    current_chunk_chars = 0

            # Add current paragraph to new chunk
            current_chunk.append(paragraph)
            current_chunk_chars += para_chars

    # Don't forget the last chunk
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks
