<!--
---
title: "Source Code"
description: "Python packages implementing the Astronomy RAG Corpus pipeline"
author: "VintageDon"
date: "2026-01-03"
version: "1.0"
status: "Active"
tags:
  - type: directory-readme
  - domain: corpus
  - phase: foundation
---
-->

# Source Code

Python packages implementing the Astronomy RAG Corpus ingestion and retrieval pipeline. Organized by pipeline stage, with shared utilities at the package root.

---

## 1. Contents

```
src/
├── acquisition/            # arXiv/ADS paper retrieval
│   └── README.md
├── logging_config.py       # Centralized logging setup
├── __init__.py             # Package metadata
└── README.md               # This file
```

---

## 2. Files

| File | Description |
|------|-------------|
| `__init__.py` | Package initialization, version string |
| `logging_config.py` | Centralized logging configuration; call once at entry point |

---

## 3. Subdirectories

| Directory | Description |
|-----------|-------------|
| [acquisition/](acquisition/README.md) | Paper source retrieval from arXiv and ADS |

---

## 4. Future Packages

As phases complete, additional packages will be added:

| Package | Phase | Purpose |
|---------|-------|---------|
| `extraction/` | Foundation | LaTeX/PDF text extraction |
| `storage/` | Foundation | Database operations |
| `retrieval/` | Hybrid Engine | Semantic and graph search |
| `agent/` | Agent | LangGraph workflows |
| `mcp/` | Interface | MCP server implementations |

---

## 5. Related

| Document | Relationship |
|----------|--------------|
| [Project Root](../README.md) | Parent directory |
| [Phase 01 Worklog](../work-logs/01-ideation-and-setup/README.md) | Architecture decisions |
| [Phase 03 Worklog](../work-logs/03-arxiv-client-implementation/README.md) | First implementation |
