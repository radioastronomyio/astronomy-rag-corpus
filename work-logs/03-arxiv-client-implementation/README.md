<!--
---
title: "Milestone 1: Acquisition - arXiv Client Implementation"
description: "arXiv source/PDF downloader and source extraction for corpus acquisition pipeline"
author: "VintageDon - https://github.com/vintagedon"
ai_contributor: "Claude Opus 4.5, GLM 4.7 (via KiloCode)"
date: "2026-01-03"
version: "1.2"
phase: milestone-01
tags:
  - domain: ingestion
  - type: implementation
  - tech: python, arxiv, pypdf
related_documents:
  - "[Phase 01: Ideation and Setup](../01-ideation-and-setup/README.md)"
  - "[Source Code README](../../src/README.md)"
---
-->

# Milestone 1: Acquisition — arXiv Client Implementation

> Compiled from: 4 sessions | January 2026  
> Status: Complete (Tasks 1.3, 1.4, 1.5)  
> Key Outcome: Functional acquisition module downloading LaTeX source and PDF, extracting and organizing source files with security validation

---

## 1. Objective

Implement the acquisition stage of the walking skeleton: an arXiv client that downloads both LaTeX source tarballs and PDFs, then extracts and organizes source files for the extraction pipeline. This establishes parallel artifact paths for the ingestion pipeline — source for LaTeX extraction, PDF as fallback. Fallback orchestration logic comes in Task 2.5.

---

## 2. Context

### Prior Work

Phase 01 established architecture and repository scaffolding. Milestone 1 planning defined:

- Seed paper: arXiv:2411.00148 (DESIVAST DR1 catalog)
- Storage paths: `/mnt/ai-ml/data/rag-corpus` (production on gpu01)
- Implementation approach: LaTeX source preferred, PDF fallback

### Walking Skeleton Strategy

The goal is not a complete acquisition system but minimal viable components proving artifacts through the pipeline. Batch processing, rate limiting, and ADS integration come later.

---

## 3. Task 1.3: LaTeX Source Download

### Implementation Decisions

#### Module Structure

| File | Purpose |
|------|---------|
| `src/logging_config.py` | Centralized logging; single setup call at entry point |
| `src/acquisition/arxiv_client.py` | arXiv source downloader |
| `src/acquisition/__init__.py` | Package exports |
| `src/acquisition/test_arxiv_client.py` | Manual validation script |
| `src/__init__.py` | Package metadata and version |

#### Interface Design

```python
def download_source(arxiv_id: str, output_dir: Path | str) -> Path
```

Simple signature accommodating future batch processing (caller loops). Returns the downloaded file path for pipeline chaining.

#### Error Handling

Custom exceptions for explicit failure modes:

| Exception | Meaning |
|-----------|---------|
| `PaperNotFoundError` | arXiv ID does not exist |
| `SourceUnavailableError` | Paper exists but no LaTeX source |
| `NetworkError` | Connection or timeout failure |

Fail-loud approach: explicit exceptions aid debugging. No silent fallbacks.

#### Logging Pattern

Centralized configuration called once at application entry. Modules use `logging.getLogger(__name__)`. Format includes timestamp, level, module name, and message.

### GLM/KiloCode Observations (Task 1.3)

First substantial use of GLM 4.7 via KiloCode for implementation.

**What Worked:**

- Generated functional code from minimal prompt
- Correct use of `arxiv` library API
- Good docstrings and type hints
- Reasonable overall structure

**Issues Requiring Correction:**

| Issue | Severity | Resolution |
|-------|----------|------------|
| Exception handling bug | Critical | Generic `except Exception` caught custom exceptions and re-wrapped them as `NetworkError`. Fixed by adding explicit re-raise for custom exceptions before the generic handler. |
| Filename versioning | Minor | Used `{arxiv_id}v{year}.tar.gz` which is misleading (arXiv versions are v1, v2, etc.). Simplified to `{arxiv_id}.tar.gz`. |
| Test path hardcoded | Minor | Pointed to Linux production path. Changed to repo-relative `test_output/raw/`. |

**KiloCode Environment Issues:**

- Inline terminal mode caused path interpretation problems on Windows
- `cd /d` syntax failed silently
- Resolution: Disable "Use Inline Terminal" to use VS Code's PowerShell terminal

### Validation (Task 1.3)

| Check | Status | Evidence |
|-------|--------|----------|
| Download executes | ✅ Pass | `test_arxiv_client.py` completes without error |
| Correct file retrieved | ✅ Pass | `2411.00148.tar.gz` (15.7 MB) matches arXiv source |
| Logging functions | ✅ Pass | Console output shows download progress |
| Exceptions propagate | ✅ Pass | Invalid IDs raise `PaperNotFoundError` |

---

## 4. Task 1.4: PDF Download

### Implementation Decisions

#### New Function

```python
def download_pdf(arxiv_id: str, output_dir: Path | str) -> Path
```

Mirrors `download_source()` signature. Both functions are independent — fallback orchestration happens in Task 2.5.

#### New Exception

| Exception | Meaning |
|-----------|---------|
| `PDFCorruptError` | Downloaded PDF fails validation |

#### PDF Validation

Two-layer validation catches different failure modes:

1. **Magic bytes** (`%PDF-`) — Fast check for non-PDF content
2. **pypdf structural parse** — Catches truncated, malformed, or encrypted PDFs

Any validation failure deletes the corrupt file and raises `PDFCorruptError`.

#### Metadata Tracking

New helper function `_log_download_metadata()` appends to `download_metadata.csv`:

| Column | Type | Notes |
|--------|------|-------|
| timestamp | ISO datetime | UTC, timezone-aware |
| arxiv_id | string | Paper identifier |
| artifact_type | string | "source" or "pdf" |
| file_size_bytes | int | Downloaded file size |
| page_count | int/null | PDF pages, null for source |
| validation_status | string | "valid", "corrupt", "skipped" |

Both `download_source()` and `download_pdf()` log to this CSV.

### GLM/KiloCode Observations (Task 1.4)

**What Worked:**

- Correctly mirrored existing pattern from `download_source()`
- Proper pypdf usage for validation
- CSV metadata tracking implemented cleanly

**Issues Requiring Correction:**

| Issue | Severity | Resolution |
|-------|----------|------------|
| pypdf import inside try block | Minor | Import was inside validation try/except, causing misleading `NetworkError` if pypdf not installed. Moved to module-level imports. |
| Deprecated datetime.utcnow() | Minor | Python 3.12 deprecation. Changed to `datetime.now(timezone.utc)`. |
| Test docstring missing exit code | Minor | Exit code 5 for `PDFCorruptError` not documented. Updated docstring. |

**Review provided via Claude.ai** — items caught during code review and fed back to KiloCode for correction.

### Validation (Task 1.4)

| Check | Status | Evidence |
|-------|--------|----------|
| PDF download executes | ✅ Pass | `test_arxiv_client.py` downloads PDF |
| PDF validation works | ✅ Pass | 17 pages extracted from seed paper |
| Metadata CSV created | ✅ Pass | Both source and PDF logged correctly |
| Corrupt PDF detection | ✅ Pass | Magic bytes check catches non-PDF content |
| Source download unchanged | ✅ Pass | Existing functionality still works |

### Test Output (Combined)

```
arXiv ID: 2411.00148
Source file: test_output/raw/2411.00148.tar.gz (15.7 MB)
PDF file: test_output/raw/2411.00148.pdf (10.6 MB, 17 pages)
Metadata CSV: test_output/raw/download_metadata.csv
Status: SUCCESS
```

---

## 5. Task 1.5: Extract and Organize Source

### Implementation Decisions

#### New Module

| File | Purpose |
|------|--------|
| `src/acquisition/source_extractor.py` | Tarball extraction and file categorization |
| `src/acquisition/test_source_extractor.py` | Manual validation script |

#### Interface Design

```python
def extract_source(tarball_path: Path | str, output_dir: Path | str) -> SourceManifest
```

Extracts tarball to `{output_dir}/{arxiv_id}/` and returns a manifest categorizing all files.

#### SourceManifest Dataclass

| Field | Type | Description |
|-------|------|-------------|
| `arxiv_id` | str | Paper identifier |
| `main_tex` | Path | Primary .tex file (contains `\documentclass`) |
| `auxiliary_tex` | list[Path] | Other .tex files (chapters, appendices) |
| `bib_files` | list[Path] | Bibliography files (.bib) |
| `figure_files` | list[Path] | Images (.png, .jpg, .pdf, .eps) |
| `style_files` | list[Path] | LaTeX style/class files (.sty, .cls) |
| `other_files` | list[Path] | Everything else |
| `extraction_dir` | Path | Root of extracted content |

#### New Exceptions

| Exception | Meaning |
|-----------|--------|
| `ExtractionError` | Generic extraction failure |
| `MainTexNotFoundError` | No .tex file contains `\documentclass` |
| `CorruptTarballError` | Tarball is corrupted or contains unsafe paths |

#### Security Validation

Two-layer security check before extraction:

1. **Path traversal** — Uses `Path.resolve()` + `relative_to()` to ensure all paths stay within extraction directory
2. **Symlink validation** — Checks that symlink targets resolve within extraction directory

Malicious tarballs (path traversal, external symlinks) raise `CorruptTarballError`.

### GLM/KiloCode Observations (Task 1.5)

**What Worked:**

- Generated complete module from detailed prompt
- Correct dataclass structure
- Good file categorization logic
- Proper exception hierarchy

**Issues Requiring Correction:**

| Issue | Severity | Resolution |
|-------|----------|------------|
| Path traversal check | High | Original used substring matching (`".." in path`). Fixed to use `Path.resolve()` + `relative_to()` for proper containment check. |
| Missing symlink validation | High | Added check that symlink targets resolve within extraction directory. |
| Python execution pattern | Minor | KiloCode kept using full interpreter path instead of activated venv. Need to update KC custom instructions. |

**Review provided via KiloCode Code Review function** — first use of KC's built-in review caught both security issues.

### Validation (Task 1.5)

| Check | Status | Evidence |
|-------|--------|----------|
| Extraction executes | ✅ Pass | `test_source_extractor.py` completes |
| Main tex identified | ✅ Pass | `ms.tex` found as main document |
| Files categorized | ✅ Pass | 52 figures, 1 bib, 0 aux tex, 3 other |
| Security validation | ✅ Pass | Path traversal check uses resolve() |
| Symlink check | ✅ Pass | External symlinks would raise error |

### Test Output

```
arXiv ID: 2411.00148
Extraction dir: test_output/extracted/2411.00148
Main tex: ms.tex
Auxiliary tex: 0
Bib files: 1 (ms.bib)
Figure files: 52
Style files: 0
Other files: 3 (aastex631.cls, ms.bbl, orcid-ID.png)
Status: SUCCESS
```

---

## 6. Files Produced

| File | Lines | Purpose |
|------|-------|---------|
| `src/__init__.py` | 12 | Package metadata |
| `src/logging_config.py` | 35 | Centralized logging setup |
| `src/acquisition/__init__.py` | 30 | Module exports (updated for 1.5) |
| `src/acquisition/arxiv_client.py` | 280 | arXiv downloader (source + PDF) |
| `src/acquisition/source_extractor.py` | 290 | Tarball extraction and categorization |
| `src/acquisition/test_arxiv_client.py` | 85 | Manual test script (download) |
| `src/acquisition/test_source_extractor.py` | 75 | Manual test script (extraction) |
| `src/README.md` | 55 | Package interior README |
| `src/acquisition/README.md` | 80 | Module interior README (updated) |

### Modified Files

| File | Change |
|------|--------|
| `.gitignore` | Added `test_output/` directory |
| `requirements.txt` | Added `pypdf>=3.0.0` |

---

## 7. Lessons Learned

### Technical

- The `arxiv` library handles rate limiting internally but error messages require string matching to categorize (fragile)
- arXiv source availability is not guaranteed; some papers only have PDF
- Test scripts should use repo-relative paths, not production paths
- PDF validation should be two-layer (magic bytes + structural) for defense in depth
- Metadata CSV during development provides useful batch analysis without filesystem queries

### Process

- GLM produces solid first-pass code but requires review for edge cases
- Detailed prompts about environment prevent wasted iterations
- KiloCode shell mode has Windows path issues; use integrated terminal
- Claude.ai code review catches issues KiloCode misses (deprecated APIs, import scoping)
- Dual-audience commenting (AI NOTEs) should be added during review, not left to implementation agent

### Documentation

- Work-logs organized by milestone, not individual tasks
- Walking skeleton confirms integration before investing in features
- Dual-audience commenting standard applied to new code

---

## 8. Next Steps

This completes Milestone 1: Acquisition (Tasks 1.3, 1.4, 1.5).

Immediate next tasks:

- **Task 2.1:** Evaluate extraction tools (pylatexenc, TexSoup, pandoc)
- **Task 2.2:** Implement LaTeX parser
- **Task 2.5:** Implement source→PDF fallback logic

The pipeline continues: organized source files → LaTeX parsing → clean text → database.

---

## 9. Provenance

| Item | Value |
|------|-------|
| Development machine | Windows workstation |
| Python interpreter | `D:\development-environments\ml-compat-3.12\python.exe` |
| Target runtime | gpu01 (Linux, `/mnt/ai-ml/rag-corpus`) |
| Test artifacts | `test_output/raw/2411.00148.{tar.gz,pdf}`, `test_output/extracted/2411.00148/` |
| Branch (1.3) | `3-task-13-implement-arxiv-client` |
| Branch (1.4) | `task-1_4-download-artifacts` |
| Branch (1.5) | `task-1_5-extract-organize-source` |
| Sessions | 4 (1.3 planning, 1.3 impl, 1.4 impl+review, 1.5 impl+review) |

---

Next: [Milestone 2: Extraction](../04-text-extraction/README.md)
