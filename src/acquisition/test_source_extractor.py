"""
Test script for LaTeX source tarball extractor.

Manual test runner for extract_source(). For quick validation during
development — not a pytest test suite. Run directly:

    python src/acquisition/test_source_extractor.py

Exit codes indicate failure type for scripting:
    0 = success
    1 = corrupt tarball
    2 = main tex not found
    3 = extraction error
    4 = unexpected error
"""

import sys
from pathlib import Path

# AI NOTE: sys.path manipulation is a workaround for running this script
# directly without installing the package. When we add proper pytest tests,
# use pytest's discovery or install the package in editable mode instead.
sys.path.insert(0, str(Path(__file__).parent.parent))

from acquisition.source_extractor import (
    CorruptTarballError,
    ExtractionError,
    MainTexNotFoundError,
    SourceManifest,
    extract_source,
)
from logging_config import setup_logging


def print_manifest(manifest: SourceManifest) -> None:
    """Print manifest contents in formatted sections."""
    print(f"\n{'='*60}")
    print("Extraction Manifest")
    print(f"{'='*60}")
    print(f"arXiv ID: {manifest.arxiv_id}")
    print(f"Extraction Directory: {manifest.extraction_dir}\n")
    
    print("Main .tex File:")
    print(f"  {manifest.main_tex}\n")
    
    print(f"Auxiliary .tex Files ({len(manifest.auxiliary_tex)}):")
    if manifest.auxiliary_tex:
        for tex_file in manifest.auxiliary_tex:
            print(f"  {tex_file}")
    else:
        print("  (none)")
    print()
    
    print(f"Bibliography Files ({len(manifest.bib_files)}):")
    if manifest.bib_files:
        for bib_file in manifest.bib_files:
            print(f"  {bib_file}")
    else:
        print("  (none)")
    print()
    
    print(f"Figure Files ({len(manifest.figure_files)}):")
    if manifest.figure_files:
        for fig_file in manifest.figure_files[:10]:  # Show first 10
            print(f"  {fig_file}")
        if len(manifest.figure_files) > 10:
            print(f"  ... and {len(manifest.figure_files) - 10} more")
    else:
        print("  (none)")
    print()
    
    print(f"Style Files ({len(manifest.style_files)}):")
    if manifest.style_files:
        for style_file in manifest.style_files:
            print(f"  {style_file}")
    else:
        print("  (none)")
    print()
    
    print(f"Other Files ({len(manifest.other_files)}):")
    if manifest.other_files:
        for other_file in manifest.other_files[:10]:  # Show first 10
            print(f"  {other_file}")
        if len(manifest.other_files) > 10:
            print(f"  ... and {len(manifest.other_files) - 10} more")
    else:
        print("  (none)")
    print()


def main():
    """Test source extractor with DESIVAST seed paper tarball."""
    setup_logging(level="INFO")
    
    # DESIVAST DR1 catalog paper — our seed paper
    arxiv_id = "2411.00148"
    
    # Paths
    repo_root = Path(__file__).parent.parent.parent
    tarball_path = repo_root / "test_output" / "raw" / f"{arxiv_id.replace('/', '_')}.tar.gz"
    output_dir = repo_root / "test_output" / "extracted"
    
    print(f"\n{'='*60}")
    print("Testing LaTeX Source Extractor")
    print(f"{'='*60}\n")
    print(f"arXiv ID: {arxiv_id}")
    print(f"Tarball: {tarball_path}")
    print(f"Output Directory: {output_dir}\n")
    
    # Check if tarball exists
    if not tarball_path.exists():
        print(f"\n{'='*60}")
        print("ERROR: Tarball Not Found")
        print(f"{'='*60}")
        print(f"Tarball file not found: {tarball_path}")
        print("\nHint: Run test_arxiv_client.py first to download the tarball.")
        return 1
    
    try:
        # Extract tarball
        print(f"{'='*60}")
        print("Extracting Source Tarball")
        print(f"{'='*60}\n")
        
        manifest = extract_source(tarball_path, output_dir)
        
        # Print manifest
        print_manifest(manifest)
        
        # Verify extraction directory exists
        if not manifest.extraction_dir.exists():
            print(f"\n{'='*60}")
            print("ERROR: Extraction Directory Not Found")
            print(f"{'='*60}")
            print(f"Extraction directory not found: {manifest.extraction_dir}")
            return 3
        
        # Verify main tex file exists
        main_tex_path = manifest.extraction_dir / manifest.main_tex
        if not main_tex_path.exists():
            print(f"\n{'='*60}")
            print("ERROR: Main Tex File Not Found")
            print(f"{'='*60}")
            print(f"Main tex file not found: {main_tex_path}")
            return 3
        
        # Success
        print(f"\n{'='*60}")
        print("SUCCESS: Extraction Completed")
        print(f"{'='*60}")
        print(f"Extraction directory: {manifest.extraction_dir}")
        print(f"Total files extracted: {sum([
            len(manifest.auxiliary_tex) + 1,  # +1 for main_tex
            len(manifest.bib_files),
            len(manifest.figure_files),
            len(manifest.style_files),
            len(manifest.other_files)
        ])}\n")
        
        return 0
        
    except CorruptTarballError as e:
        print(f"\n{'='*60}")
        print("ERROR: Corrupt Tarball")
        print(f"{'='*60}")
        print(f"Details: {e}\n")
        return 1
        
    except MainTexNotFoundError as e:
        print(f"\n{'='*60}")
        print("ERROR: Main Tex Not Found")
        print(f"{'='*60}")
        print(f"Details: {e}")
        print("Note: Could not identify main .tex file (no \\documentclass found).\n")
        return 2
        
    except ExtractionError as e:
        print(f"\n{'='*60}")
        print("ERROR: Extraction Failed")
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
