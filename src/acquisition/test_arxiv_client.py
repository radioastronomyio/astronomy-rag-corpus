"""
Test script for arXiv source downloader.

Manual test runner for download_source(). For quick validation during
development — not a pytest test suite. Run directly:

    python src/acquisition/test_arxiv_client.py

Exit codes indicate failure type for scripting:
    0 = success
    1 = paper not found
    2 = source unavailable  
    3 = network error
    4 = unexpected error
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
    SourceUnavailableError,
    download_source,
)
from logging_config import setup_logging


def main():
    """Test arXiv source downloader with DESIVAST seed paper."""
    setup_logging(level="INFO")
    
    # DESIVAST DR1 catalog paper — our seed paper for the walking skeleton.
    # This paper has LaTeX source available, making it a reliable test case.
    arxiv_id = "2411.00148"
    
    # Output to repo-local directory (gitignored). Production paths on gpu01
    # are different — this is for local development testing only.
    output_dir = Path(__file__).parent.parent.parent / "test_output" / "raw"
    
    print(f"\n{'='*60}")
    print("Testing arXiv Source Downloader")
    print(f"{'='*60}\n")
    print(f"arXiv ID: {arxiv_id}")
    print(f"Output Directory: {output_dir}\n")
    
    try:
        result_path = download_source(arxiv_id, output_dir)
        
        print(f"\n{'='*60}")
        print("SUCCESS: Download completed")
        print(f"{'='*60}")
        print(f"Source file: {result_path}")
        print(f"File size: {result_path.stat().st_size} bytes")
        print("\n")
        
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
