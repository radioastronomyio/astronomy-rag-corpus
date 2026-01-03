"""
arXiv source downloader for Astronomy RAG Corpus.

Downloads LaTeX source tarballs from arXiv for paper ingestion. This module
is the entry point for the acquisition pipeline — downstream extraction
expects .tar.gz files in the format produced here.
"""

import logging
from pathlib import Path

import arxiv

logger = logging.getLogger(__name__)


class PaperNotFoundError(Exception):
    """Raised when arXiv paper ID is not found."""
    pass


class SourceUnavailableError(Exception):
    """Raised when LaTeX source is not available for a paper."""
    pass


class NetworkError(Exception):
    """Raised when network errors occur during download."""
    pass


def download_source(arxiv_id: str, output_dir: Path | str) -> Path:
    """
    Download LaTeX source tarball for given arXiv ID.
    
    Args:
        arxiv_id: arXiv paper identifier (e.g., "2411.00148")
        output_dir: Directory where source tarball will be saved
    
    Returns:
        Path to downloaded source tarball
    
    Raises:
        PaperNotFoundError: If paper ID is not found on arXiv
        SourceUnavailableError: If LaTeX source is not available
        NetworkError: If network errors occur during download
    """
    # AI NOTE: Output filename is {arxiv_id}.tar.gz (no version suffix).
    # Downstream extraction modules expect this naming convention.
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Downloading LaTeX source for arXiv:{arxiv_id}")
    
    try:
        # The arxiv library provides id_list for direct ID lookup, avoiding
        # the complexity of query string construction.
        search = arxiv.Search(id_list=[arxiv_id])
        client = arxiv.Client()
        
        paper = next(client.results(search), None)
        
        if paper is None:
            logger.error(f"Paper not found on arXiv: {arxiv_id}")
            raise PaperNotFoundError(f"arXiv paper not found: {arxiv_id}")
        
        logger.info(f"Found paper: {paper.title}")
        
        filename = f"{arxiv_id.replace('/', '_')}.tar.gz"
        output_path = output_dir / filename
        
        logger.info(f"Downloading source to: {output_path}")
        paper.download_source(dirpath=str(output_dir), filename=filename)
        
        # Defensive verification — arxiv library doesn't raise on all failure
        # modes, so we confirm the file actually exists and has content.
        if not output_path.exists():
            logger.error(f"Source file not created after download: {output_path}")
            raise SourceUnavailableError(f"Source download failed for {arxiv_id}")
        
        if output_path.stat().st_size == 0:
            logger.error(f"Source file is empty: {output_path}")
            output_path.unlink()
            raise SourceUnavailableError(f"Source file is empty for {arxiv_id}")
        
        logger.info(f"Successfully downloaded source: {output_path} ({output_path.stat().st_size} bytes)")
        return output_path
    
    # AI NOTE: Custom exceptions must be re-raised before the generic handler.
    # The generic handler uses string matching which could incorrectly re-wrap
    # our exceptions as NetworkError.
    except PaperNotFoundError:
        raise
    except SourceUnavailableError:
        raise
    except OSError:
        raise
    except Exception as e:
        # Categorize unknown exceptions by inspecting error message content.
        # This is fragile but covers common arxiv library failure modes.
        error_msg = str(e).lower()
        
        if "source" in error_msg and ("unavailable" in error_msg or "not found" in error_msg):
            logger.warning(f"LaTeX source unavailable for {arxiv_id}: {e}")
            raise SourceUnavailableError(f"LaTeX source unavailable for {arxiv_id}: {e}")
        
        if any(keyword in error_msg for keyword in ["http", "network", "connection", "timeout", "url"]):
            logger.error(f"Network error downloading {arxiv_id}: {e}")
            raise NetworkError(f"Network error downloading {arxiv_id}: {e}")
        
        # Fallback: treat unrecognized errors as network issues since they're
        # most commonly transient failures from the arxiv API.
        logger.error(f"Unexpected error downloading {arxiv_id}: {e}")
        raise NetworkError(f"Unexpected error downloading {arxiv_id}: {e}")
