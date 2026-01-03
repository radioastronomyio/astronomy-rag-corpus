"""
arXiv source downloader for Astronomy RAG Corpus.

Downloads LaTeX source tarballs and PDFs from arXiv for paper ingestion. This module
is the entry point for the acquisition pipeline — downstream extraction
expects .tar.gz files in the format produced here.
"""

import csv
import logging
from datetime import datetime, timezone
from pathlib import Path

import arxiv
from pypdf import PdfReader

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


class PDFCorruptError(Exception):
    """Raised when downloaded PDF fails validation."""
    pass


def _log_download_metadata(
    output_dir: Path,
    arxiv_id: str,
    artifact_type: str,
    file_size_bytes: int,
    page_count: int | None = None,
    validation_status: str = "valid",
) -> None:
    """
    Log download metadata to CSV file.
    
    Appends a row to download_metadata.csv in output_dir. Creates the file
    with headers if it doesn't exist. Used during iterative testing to track
    what's been downloaded without re-querying the filesystem.
    
    Args:
        output_dir: Directory containing the downloaded artifact
        arxiv_id: arXiv paper identifier
        artifact_type: Type of artifact ("source" or "pdf")
        file_size_bytes: Size of downloaded file in bytes
        page_count: Number of pages (None for source tarballs)
        validation_status: Status of validation ("valid", "corrupt", "skipped")
    """
    # AI NOTE: CSV schema is used by test scripts and future batch analysis.
    # If adding columns, update fieldnames list and all _log_download_metadata
    # call sites to provide the new values.
    csv_path = output_dir / "download_metadata.csv"
    
    # Create CSV with headers if it doesn't exist
    file_exists = csv_path.exists()
    
    with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "timestamp",
            "arxiv_id",
            "artifact_type",
            "file_size_bytes",
            "page_count",
            "validation_status",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "arxiv_id": arxiv_id,
            "artifact_type": artifact_type,
            "file_size_bytes": file_size_bytes,
            "page_count": page_count,
            "validation_status": validation_status,
        })
    
    logger.debug(f"Logged metadata to {csv_path}")


def download_pdf(arxiv_id: str, output_dir: Path | str) -> Path:
    """
    Download PDF for given arXiv ID.
    
    Args:
        arxiv_id: arXiv paper identifier (e.g., "2411.00148")
        output_dir: Directory where PDF will be saved
    
    Returns:
        Path to downloaded PDF file
    
    Raises:
        PaperNotFoundError: If paper ID is not found on arXiv
        PDFCorruptError: If downloaded PDF fails validation
        NetworkError: If network errors occur during download
    """
    # AI NOTE: Output filename is {arxiv_id}.pdf (slashes normalized to underscores).
    # This parallels download_source() naming. Fallback orchestration in Task 2.5
    # expects both artifacts to exist with these names.
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Downloading PDF for arXiv:{arxiv_id}")
    
    try:
        search = arxiv.Search(id_list=[arxiv_id])
        client = arxiv.Client()
        
        paper = next(client.results(search), None)
        
        if paper is None:
            logger.error(f"Paper not found on arXiv: {arxiv_id}")
            raise PaperNotFoundError(f"arXiv paper not found: {arxiv_id}")
        
        logger.info(f"Found paper: {paper.title}")
        
        filename = f"{arxiv_id.replace('/', '_')}.pdf"
        output_path = output_dir / filename
        
        logger.info(f"Downloading PDF to: {output_path}")
        paper.download_pdf(dirpath=str(output_dir), filename=filename)
        
        # Defensive verification
        if not output_path.exists():
            logger.error(f"PDF file not created after download: {output_path}")
            raise PDFCorruptError(f"PDF download failed for {arxiv_id}")
        
        file_size = output_path.stat().st_size
        if file_size == 0:
            logger.error(f"PDF file is empty: {output_path}")
            output_path.unlink()
            raise PDFCorruptError(f"PDF file is empty for {arxiv_id}")
        
        # Two-layer validation: magic bytes catch non-PDFs fast, pypdf catches
        # truncated or malformed structure. Both must pass.
        try:
            # Check magic bytes
            with open(output_path, "rb") as f:
                header = f.read(5)
                if header != b"%PDF-":
                    logger.error(f"Invalid PDF magic bytes: {output_path}")
                    output_path.unlink()
                    raise PDFCorruptError(f"Invalid PDF magic bytes for {arxiv_id}")
            
            # Try to read PDF and get page count
            reader = PdfReader(output_path)
            page_count = len(reader.pages)
            
            logger.info(f"PDF validation successful: {page_count} pages")
            
        except PDFCorruptError:
            # Already a PDFCorruptError from magic bytes check, re-raise as-is
            raise
        except Exception as e:
            # AI NOTE: Any pypdf exception (malformed PDF, encryption, etc.)
            # becomes PDFCorruptError. This is intentional — we want binary
            # pass/fail for downstream pipeline decisions.
            logger.error(f"PDF validation failed for {arxiv_id}: {e}")
            output_path.unlink()
            raise PDFCorruptError(f"PDF validation failed for {arxiv_id}: {e}")
        
        # Log metadata
        _log_download_metadata(
            output_dir=output_dir,
            arxiv_id=arxiv_id,
            artifact_type="pdf",
            file_size_bytes=file_size,
            page_count=page_count,
            validation_status="valid",
        )
        
        logger.info(f"Successfully downloaded PDF: {output_path} ({file_size} bytes)")
        return output_path
    
    # AI NOTE: Custom exceptions must be re-raised before the generic handler.
    # The generic handler uses string matching which could incorrectly re-wrap
    # our exceptions as NetworkError. Pattern mirrors download_source().
    except PaperNotFoundError:
        raise
    except PDFCorruptError:
        raise
    except OSError:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        
        if any(keyword in error_msg for keyword in ["http", "network", "connection", "timeout", "url"]):
            logger.error(f"Network error downloading {arxiv_id}: {e}")
            raise NetworkError(f"Network error downloading {arxiv_id}: {e}")
        
        logger.error(f"Unexpected error downloading {arxiv_id}: {e}")
        raise NetworkError(f"Unexpected error downloading {arxiv_id}: {e}")


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
        
        file_size = output_path.stat().st_size
        if file_size == 0:
            logger.error(f"Source file is empty: {output_path}")
            output_path.unlink()
            raise SourceUnavailableError(f"Source file is empty for {arxiv_id}")
        
        # Log metadata
        _log_download_metadata(
            output_dir=output_dir,
            arxiv_id=arxiv_id,
            artifact_type="source",
            file_size_bytes=file_size,
            page_count=None,
            validation_status="valid",
        )
        
        logger.info(f"Successfully downloaded source: {output_path} ({file_size} bytes)")
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
