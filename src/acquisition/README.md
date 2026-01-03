<!--
---
title: "Acquisition Module"
description: "Paper source retrieval from arXiv and NASA ADS"
author: "VintageDon"
date: "2026-01-03"
version: "1.0"
status: "Active"
tags:
  - type: directory-readme
  - domain: ingestion
  - phase: foundation
  - tech: arxiv, python
---
-->

# Acquisition Module

Paper source retrieval from arXiv and NASA ADS. Downloads LaTeX source tarballs (preferred) or PDF fallbacks for corpus ingestion. This is the first stage of the ingestion pipeline.

---

## 1. Contents

```
acquisition/
├── arxiv_client.py         # arXiv source downloader
├── test_arxiv_client.py    # Manual validation script
├── __init__.py             # Package exports
└── README.md               # This file
```

---

## 2. Files

| File | Description |
|------|-------------|
| `arxiv_client.py` | Downloads LaTeX source tarballs from arXiv given an arXiv ID |
| `test_arxiv_client.py` | Manual test script; downloads seed paper to `test_output/raw/` |
| `__init__.py` | Exports `download_source` and custom exceptions |

---

## 3. Usage

```python
from acquisition import download_source, PaperNotFoundError

try:
    path = download_source("2411.00148", output_dir="./raw")
    print(f"Downloaded to: {path}")
except PaperNotFoundError:
    print("Paper not found on arXiv")
```

---

## 4. Exceptions

| Exception | Meaning |
|-----------|---------|
| `PaperNotFoundError` | arXiv ID does not exist |
| `SourceUnavailableError` | Paper exists but LaTeX source not available |
| `NetworkError` | Connection or timeout failure |

---

## 5. Future Additions

| Component | Purpose |
|-----------|---------|
| `ads_client.py` | NASA ADS metadata and bibcode retrieval |
| `batch_download.py` | Bulk acquisition with rate limiting |

---

## 6. Related

| Document | Relationship |
|----------|--------------|
| [src/](../README.md) | Parent package |
| [Phase 03 Worklog](../../work-logs/03-arxiv-client-implementation/README.md) | Implementation details |
