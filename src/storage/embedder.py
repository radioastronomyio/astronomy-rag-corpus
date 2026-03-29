"""
Embedding generation with nomic-embed-text.

Generates 768-dimensional embeddings using sentence-transformers
with GPU acceleration when available.
"""

import logging
from typing import Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Model name as specified in task requirements
MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
# Embedding dimension (768 as per schema)
EMBEDDING_DIM = 768


def embed_chunks(chunks: List[Dict], batch_size: int = 32) -> List[np.ndarray]:
    """
    Generate embeddings for a list of chunks using nomic-embed-text.

    Args:
        chunks: List of chunk dictionaries with 'content' and 'context_preamble' keys
        batch_size: Batch size for embedding generation (default 32)

    Returns:
        List of numpy arrays, each with shape (768,)

    Raises:
        Exception: If model loading or embedding fails
    """
    # AI NOTE: Embeddings are generated for the concatenation of
    # context_preamble + content. This ensures the embedding captures
    # the full contextual information, not just the chunk text.
    # Model runs on GPU if available (CUDA), otherwise CPU.

    # Prepare texts for embedding
    texts = []
    for chunk in chunks:
        context_preamble = chunk.get("context_preamble", "")
        content = chunk.get("content", "")
        full_text = f"{context_preamble}\n\n{content}"
        texts.append(full_text)

    logger.info(f"Loading embedding model: {MODEL_NAME}")

    try:
        # Load model (sentence-transformers handles GPU/CPU automatically)
        model = SentenceTransformer(MODEL_NAME)
        logger.info(
            f"Model loaded successfully, dimension: {model.get_sentence_embedding_dimension()}"
        )

        # Generate embeddings in batches
        logger.info(
            f"Generating embeddings for {len(texts)} chunks with batch_size={batch_size}"
        )
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,  # L2 normalization for cosine similarity
        )

        logger.info(f"Embeddings generated successfully, shape: {embeddings.shape}")

        return list(embeddings)

    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise


def get_embedding_dimension() -> int:
    """
    Return the embedding dimension for the configured model.

    Returns:
        Embedding dimension (768 for nomic-embed-text-v1.5)
    """
    return EMBEDDING_DIM
