"""
Test script for arXiv source and PDF downloader.

Manual test runner for download_source() and download_pdf(). For quick validation
during development — not a pytest test suite. Run directly:

    python src/acquisition/test_arxiv_client.py

Exit codes indicate failure type for scripting:
    0 = success
    1 = paper not found
    2 = source unavailable
    3 = network error
    4 = unexpected error
    5 = PDF corrupt
"""

import sys
from pathlib import Path

# AI NOTE: sys.path manipulation is a workaround for running this script
# directly without installing the package. When we add proper pytest tests,
# use pytest's discovery or install the package in editable mode instead.
sys.path.insert(0, str(Path(__file__).parent.parent))

from acquisition.arxiv_client import (
    NetworkError,
    PaperNotFoundError,
    PDFCorruptError,
    SourceUnavailableError,
    download_pdf,
    download_source,
)
from logging_config import setup_logging


def main():
    """Test arXiv source and PDF downloader with DESIVAST seed paper."""
    setup_logging(level="INFO")
    
    # DESIVAST DR1 catalog paper — our seed paper for the walking skeleton.
    # This paper has both LaTeX source and PDF available.
    arxiv_id = "2411.00148"
    
    # Output to repo-local directory (gitignored). Production paths on gpu01
    # are different — this is for local development testing only.
    output_dir = Path(__file__).parent.parent.parent / "test_output" / "raw"
    
    print(f"\n{'='*60}")
    print("Testing arXiv Downloader (Source + PDF)")
    print(f"{'='*60}\n")
    print(f"arXiv ID: {arxiv_id}")
    print(f"Output Directory: {output_dir}\n")
    
    try:
        # Test source download
        print(f"{'='*60}")
        print("Test 1: Download LaTeX Source")
        print(f"{'='*60}\n")
        
        source_path = download_source(arxiv_id, output_dir)
        
        print(f"\n{'='*60}")
        print("SUCCESS: Source download completed")
        print(f"{'='*60}")
        print(f"Source file: {source_path}")
        print(f"File size: {source_path.stat().st_size} bytes\n")
        
        # Test PDF download
        print(f"\n{'='*60}")
        print("Test 2: Download PDF")
        print(f"{'='*60}\n")
        
        pdf_path = download_pdf(arxiv_id, output_dir)
        
        print(f"\n{'='*60}")
        print("SUCCESS: PDF download completed")
        print(f"{'='*60}")
        print(f"PDF file: {pdf_path}")
        print(f"File size: {pdf_path.stat().st_size} bytes\n")
        
        # Check metadata CSV
        metadata_path = output_dir / "download_metadata.csv"
        if metadata_path.exists():
            print(f"\n{'='*60}")
            print("Metadata CSV Created")
            print(f"{'='*60}")
            print(f"Location: {metadata_path}")
            print(f"File size: {metadata_path.stat().st_size} bytes\n")
        else:
            print(f"\nWARNING: Metadata CSV not found at {metadata_path}\n")
        
        return 0
        
    except PaperNotFoundError as e:
        print(f"\n{'='*60}")
        print("ERROR: Paper Not Found")
        print(f"{'='*60}")
        print(f"Details: {e}\n")
        return 1
        
    except SourceUnavailableError as e:
        print(f"\n{'='*60}")
        print("WARNING: Source Unavailable")
        print(f"{'='*60}")
        print(f"Details: {e}")
        print("Note: Some papers on arXiv do not have LaTeX source available.\n")
        return 2
        
    except PDFCorruptError as e:
        print(f"\n{'='*60}")
        print("ERROR: PDF Corrupt")
        print(f"{'='*60}")
        print(f"Details: {e}")
        print("Note: Downloaded PDF failed validation.\n")
        return 5
        
    except NetworkError as e:
        print(f"\n{'='*60}")
        print("ERROR: Network Error")
        print(f"{'='*60}")
        print(f"Details: {e}\n")
        return 3
        
    except Exception as e:
        print(f"\n{'='*60}")
        print("ERROR: Unexpected Error")
        print(f"{'='*60}")
        print(f"Details: {e}\n")
        return 4


if __name__ == "__main__":
    sys.exit(main())
