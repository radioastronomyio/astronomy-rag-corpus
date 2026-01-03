<!--
---
title: "Acquisition Module"
description: "Paper source retrieval from arXiv and NASA ADS"
author: "VintageDon"
date: "2026-01-03"
version: "1.1"
status: "Active"
tags:
  - type: directory-readme
  - domain: ingestion
  - phase: foundation
  - tech: arxiv, pypdf, python
---
-->

# Acquisition Module

Paper source retrieval from arXiv and NASA ADS. Downloads LaTeX source tarballs (preferred) and PDFs for corpus ingestion. This is the first stage of the ingestion pipeline.

---

## 1. Contents

```
acquisition/
├── arxiv_client.py         # arXiv source and PDF downloader
├── source_extractor.py      # LaTeX source tarball extractor
├── test_arxiv_client.py    # Manual validation script
├── __init__.py             # Package exports
└── README.md               # This file
```

---

## 2. Files

| File | Description |
|------|-------------|
| `arxiv_client.py` | Downloads LaTeX source tarballs and PDFs from arXiv given an arXiv ID |
| `source_extractor.py` | Extracts and categorizes LaTeX source tarballs into manifest |
| `test_arxiv_client.py` | Manual test script; downloads seed paper to `test_output/raw/` |
| `__init__.py` | Exports download functions, extract_source, and custom exceptions |

---

## 3. Usage

### Download LaTeX Source

```python
from acquisition import download_source, PaperNotFoundError, SourceUnavailableError

try:
    path = download_source("2411.00148", output_dir="./raw")
    print(f"Downloaded to: {path}")
except PaperNotFoundError:
    print("Paper not found on arXiv")
except SourceUnavailableError:
    print("LaTeX source not available for this paper")
```

### Download PDF

```python
from acquisition import download_pdf, PaperNotFoundError, PDFCorruptError

try:
    path = download_pdf("2411.00148", output_dir="./raw")
    print(f"Downloaded to: {path}")
except PaperNotFoundError:
    print("Paper not found on arXiv")
except PDFCorruptError:
    print("PDF failed validation (corrupt or malformed)")
```

Both functions log metadata to `{output_dir}/download_metadata.csv` for tracking during iterative testing.

### Extract LaTeX Source

```python
from acquisition import extract_source, MainTexNotFoundError, CorruptTarballError

try:
    manifest = extract_source("2411.00148.tar.gz", output_dir="./extracted")
    print(f"Main tex: {manifest.main_tex}")
    print(f"Auxiliary tex: {manifest.auxiliary_tex}")
    print(f"Bib files: {manifest.bib_files}")
    print(f"Figures: {manifest.figure_files}")
except MainTexNotFoundError:
    print("Could not identify main .tex file")
except CorruptTarballError:
    print("Tarball is corrupted or invalid")
```

The `SourceManifest` dataclass provides categorized lists of all extracted files:
- `main_tex`: Primary .tex file (contains `\documentclass`)
- `auxiliary_tex`: Other .tex files (chapters, appendices, includes)
- `bib_files`: Bibliography files (.bib)
- `figure_files`: Image files (.png, .jpg, .pdf, .eps, etc.)
- `style_files`: LaTeX style/class files (.sty, .cls)
- `other_files`: All other files (README, Makefile, etc.)
- `extraction_dir`: Root directory of extracted content

---

## 4. Exceptions

| Exception | Meaning |
|-----------|---------|
| `PaperNotFoundError` | arXiv ID does not exist |
| `SourceUnavailableError` | Paper exists but LaTeX source not available |
| `PDFCorruptError` | Downloaded PDF fails validation (magic bytes or structure) |
| `NetworkError` | Connection or timeout failure |
| `CorruptTarballError` | Source tarball is corrupted or invalid |
| `MainTexNotFoundError` | No .tex file containing `\documentclass` found |
| `ExtractionError` | General extraction failure (file system, etc.) |

---

## 5. Metadata Tracking

Both download functions append to `download_metadata.csv`:

| Column | Type | Notes |
|--------|------|-------|
| timestamp | ISO datetime | UTC, timezone-aware |
| arxiv_id | string | Paper identifier |
| artifact_type | string | "source" or "pdf" |
| file_size_bytes | int | Downloaded file size |
| page_count | int/null | PDF pages, null for source |
| validation_status | string | "valid", "corrupt", "skipped" |

---

## 6. Future Additions

| Component | Purpose |
|-----------|---------|
| `ads_client.py` | NASA ADS metadata and bibcode retrieval |
| `batch_download.py` | Bulk acquisition with rate limiting |
| `test_source_extractor.py` | Automated tests for extraction logic |
| Fallback logic (Task 2.5) | Orchestration: try source, fall back to PDF |

---

## 7. Related

| Document | Relationship |
|----------|--------------|
| [src/](../README.md) | Parent package |
| [Milestone 1 Worklog](../../work-logs/03-arxiv-client-implementation/README.md) | Implementation details |
