"""
LaTeX source tarball extractor for Astronomy RAG Corpus.

Extracts arXiv source tarballs and organizes files for the extraction pipeline.
Identifies the main .tex file, auxiliary .tex files, bibliography files, figures,
and style files. Returns a manifest for downstream processing.
"""

import logging
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Raised when tarball extraction fails."""
    pass


class MainTexNotFoundError(Exception):
    """Raised when main .tex file cannot be identified."""
    pass


class CorruptTarballError(Exception):
    """Raised when tarball is corrupted or invalid."""
    pass


@dataclass
class SourceManifest:
    """
    Manifest of extracted LaTeX source files.
    
    Provides categorized lists of files found in the extracted source tarball.
    All paths are relative to the extraction directory root.
    
    Attributes:
        arxiv_id: arXiv paper identifier
        main_tex: Path to primary .tex file (contains \\documentclass)
        auxiliary_tex: List of other .tex files (chapters, appendices, includes)
        bib_files: List of bibliography files (.bib)
        figure_files: List of image files (.png, .jpg, .jpeg, .pdf, .eps, .epsf)
        style_files: List of LaTeX style/class files (.sty, .cls)
        other_files: List of all other files (README, Makefile, etc.)
        extraction_dir: Root directory of extracted content
    """
    arxiv_id: str
    main_tex: Path
    auxiliary_tex: list[Path]
    bib_files: list[Path]
    figure_files: list[Path]
    style_files: list[Path]
    other_files: list[Path]
    extraction_dir: Path


def _find_main_tex(extraction_dir: Path) -> Path:
    """
    Identify the main .tex file by searching for \\documentclass.
    
    Scans all .tex files in extraction_dir (recursively) and returns the first
    file that contains \\documentclass at the beginning. This is the standard
    LaTeX convention for identifying the main document file.
    
    Args:
        extraction_dir: Root directory of extracted source
    
    Returns:
        Path to main .tex file (relative to extraction_dir)
    
    Raises:
        MainTexNotFoundError: If no .tex file contains \\documentclass
    """
    # AI NOTE: We search recursively because some arXiv tarballs have nested
    # directory structures (e.g., main.tex in a subdirectory). The first match
    # is returned — in ambiguous cases, this is usually the correct main file.
    
    for tex_file in extraction_dir.rglob("*.tex"):
        try:
            with open(tex_file, "r", encoding="utf-8", errors="ignore") as f:
                # Read first 10 lines to find \\documentclass
                for _ in range(10):
                    line = f.readline()
                    if not line:
                        break
                    if "\\documentclass" in line:
                        # Return path relative to extraction_dir
                        relative_path = tex_file.relative_to(extraction_dir)
                        logger.debug(f"Found main tex file: {relative_path}")
                        return relative_path
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Could not read {tex_file}: {e}")
            continue
    
    # No main tex file found
    raise MainTexNotFoundError(
        f"No .tex file containing \\documentclass found in {extraction_dir}"
    )


def _categorize_file(file_path: Path, main_tex: Path) -> Optional[str]:
    """
    Categorize a file by its extension and relation to main tex.
    
    Returns one of: 'auxiliary_tex', 'bib', 'figure', 'style', 'other'.
    Returns None if file is the main tex file (already categorized separately).
    
    Args:
        file_path: Path to file (relative to extraction_dir)
        main_tex: Path to main tex file (relative to extraction_dir)
    
    Returns:
        Category string or None if file is main tex
    """
    # AI NOTE: File categorization is based on extensions. This is a heuristic
    # that works for standard LaTeX projects. Edge cases (e.g., non-standard
    # extensions) will be categorized as 'other' and still accessible.
    
    if file_path == main_tex:
        return None
    
    suffix = file_path.suffix.lower()
    
    # LaTeX files (excluding main)
    if suffix == ".tex":
        return "auxiliary_tex"
    
    # Bibliography files
    if suffix == ".bib":
        return "bib"
    
    # Figure files (common formats in arXiv submissions)
    if suffix in {".png", ".jpg", ".jpeg", ".pdf", ".eps", ".epsf", ".ps"}:
        return "figure"
    
    # Style/class files
    if suffix in {".sty", ".cls"}:
        return "style"
    
    # Everything else
    return "other"


def extract_source(
    tarball_path: Path | str,
    output_dir: Path | str
) -> SourceManifest:
    """
    Extract arXiv source tarball and categorize files.
    
    Extracts the tarball to {output_dir}/{arxiv_id}/, identifies the main
    .tex file, and categorizes all files into the manifest. Handles nested
    directory structures within the tarball.
    
    Args:
        tarball_path: Path to .tar.gz source tarball
        output_dir: Parent directory where extracted content will be stored
    
    Returns:
        SourceManifest with categorized file lists and extraction directory
    
    Raises:
        CorruptTarballError: If tarball is corrupted or invalid
        MainTexNotFoundError: If main .tex file cannot be identified
        ExtractionError: If extraction fails for other reasons
    
    Example:
        >>> manifest = extract_source("2411.00148.tar.gz", "./extracted")
        >>> print(f"Main tex: {manifest.main_tex}")
        >>> print(f"Bib files: {manifest.bib_files}")
    """
    # AI NOTE: arXiv tarball naming is {arxiv_id}.tar.gz (no version suffix).
    # We extract this ID to create the output directory. The extraction
    # directory structure is {output_dir}/{arxiv_id}/.
    
    tarball_path = Path(tarball_path)
    output_dir = Path(output_dir)
    
    # Extract arXiv ID from tarball filename
    # Expected format: 2411.00148.tar.gz or 2411_00148.tar.gz
    arxiv_id = tarball_path.stem.replace(".tar", "").replace("_", "/")
    
    extraction_dir = output_dir / arxiv_id
    
    logger.info(f"Extracting source tarball: {tarball_path}")
    logger.info(f"Extraction directory: {extraction_dir}")
    
    try:
        # Create extraction directory (will fail if already exists with content)
        extraction_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract tarball
        logger.debug(f"Opening tarball: {tarball_path}")
        with tarfile.open(tarball_path, "r:gz") as tar:
            # AI NOTE: Some arXiv tarballs extract into a subdirectory
            # (e.g., 2411.00148/), others extract files directly.
            # We extract everything and handle both cases in categorization.
            
            # Security validation before extracting
            # AI NOTE: Malicious tarballs can contain paths like "../../../etc/passwd"
            # or symlinks pointing outside. We validate all members before extraction.
            extraction_dir_resolved = extraction_dir.resolve()
            
            for member in tar.getmembers():
                # Resolve the full path this member would extract to
                member_path = (extraction_dir / member.name).resolve()
                
                # Check path stays within extraction directory
                try:
                    member_path.relative_to(extraction_dir_resolved)
                except ValueError:
                    raise CorruptTarballError(
                        f"Tarball contains path escaping extraction dir: {member.name}"
                    )
                
                # Check symlinks don't point outside extraction directory
                if member.issym():
                    link_target = Path(member.linkname)
                    # Resolve relative to the directory containing the symlink
                    symlink_dir = member_path.parent
                    resolved_target = (symlink_dir / link_target).resolve()
                    try:
                        resolved_target.relative_to(extraction_dir_resolved)
                    except ValueError:
                        raise CorruptTarballError(
                            f"Tarball contains symlink escaping extraction dir: "
                            f"{member.name} -> {member.linkname}"
                        )
            
            # Extract all members
            tar.extractall(path=extraction_dir)
            logger.debug(f"Extracted {len(tar.getmembers())} members")
        
        logger.info(f"Extraction successful: {extraction_dir}")
        
        # Find main tex file
        logger.debug("Searching for main .tex file...")
        main_tex = _find_main_tex(extraction_dir)
        logger.info(f"Main .tex file: {main_tex}")
        
        # Categorize all files
        logger.debug("Categorizing extracted files...")
        
        auxiliary_tex: list[Path] = []
        bib_files: list[Path] = []
        figure_files: list[Path] = []
        style_files: list[Path] = []
        other_files: list[Path] = []
        
        # Walk through extraction directory recursively
        for file_path in extraction_dir.rglob("*"):
            # Skip directories
            if not file_path.is_file():
                continue
            
            # Get relative path
            relative_path = file_path.relative_to(extraction_dir)
            
            # Categorize file
            category = _categorize_file(relative_path, main_tex)
            
            if category == "auxiliary_tex":
                auxiliary_tex.append(relative_path)
            elif category == "bib":
                bib_files.append(relative_path)
            elif category == "figure":
                figure_files.append(relative_path)
            elif category == "style":
                style_files.append(relative_path)
            elif category == "other":
                other_files.append(relative_path)
            # main_tex is not added to any list (handled separately)
        
        # Sort lists for consistent output
        auxiliary_tex.sort()
        bib_files.sort()
        figure_files.sort()
        style_files.sort()
        other_files.sort()
        
        # Log summary
        logger.info("Extraction summary:")
        logger.info(f"  Main .tex: {main_tex}")
        logger.info(f"  Auxiliary .tex files: {len(auxiliary_tex)}")
        logger.info(f"  Bibliography files: {len(bib_files)}")
        logger.info(f"  Figure files: {len(figure_files)}")
        logger.info(f"  Style files: {len(style_files)}")
        logger.info(f"  Other files: {len(other_files)}")
        
        # Create and return manifest
        manifest = SourceManifest(
            arxiv_id=arxiv_id,
            main_tex=main_tex,
            auxiliary_tex=auxiliary_tex,
            bib_files=bib_files,
            figure_files=figure_files,
            style_files=style_files,
            other_files=other_files,
            extraction_dir=extraction_dir,
        )
        
        return manifest
    
    except tarfile.TarError as e:
        logger.error(f"Tarball extraction failed: {e}")
        raise CorruptTarballError(f"Corrupt or invalid tarball: {e}")
    
    except MainTexNotFoundError:
        # Re-raise as-is (already has context)
        raise
    
    except OSError as e:
        logger.error(f"File system error during extraction: {e}")
        raise ExtractionError(f"Extraction failed due to file system error: {e}")
    
    except CorruptTarballError:
        # Re-raise as-is (specific error with context)
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}")
        raise ExtractionError(f"Unexpected error during extraction: {e}")
