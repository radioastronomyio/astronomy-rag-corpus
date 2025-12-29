<!--
---
title: "Tagging Strategy"
description: "Controlled vocabulary for document classification and RAG retrieval in astronomy-rag-corpus"
author: "VintageDon - https://github.com/vintagedon"
ai_contributor: "Claude Opus 4.5 (Anthropic)"
date: "2025-12-29"
version: "1.0"
tags:
  - domain: documentation
  - type: specification
related_documents:
  - "[Interior README Template](interior-readme-template.md)"
  - "[General KB Template](general-kb-template.md)"
---
-->

# Tagging Strategy

## 1. Purpose

This document defines the controlled tag vocabulary for all documentation in astronomy-rag-corpus, enabling consistent classification for human navigation and RAG system retrieval.

---

## 2. Scope

Covers all tag categories, valid values, and usage guidance. Does not cover front-matter field structure—see individual templates for field requirements.

---

## 3. Tag Categories

### Phase Tags

Pipeline implementation phases from the architectural GDR. Documents may belong to multiple phases.

| Tag | Description |
|-----|-------------|
| `phase-01` | Foundation — DB setup, SMB mounts, Walking Skeleton |
| `phase-02` | Harvester — ADS/arXiv acquisition, seed corpus population |
| `phase-03` | Hybrid Engine — Neo4j graph construction, hybrid retrieval |
| `phase-04` | Agent — LangGraph state machine, multi-step research |
| `phase-05` | Interface — MCP servers, Claude Code integration |

**Usage**: Tag with all phases a document supports. A methodology doc explaining text extraction used in phases 01-03 would carry `phase-01`, `phase-02`, `phase-03`.

---

### Domain Tags

Primary functional area. Usually one per document.

| Tag | Description |
|-----|-------------|
| `corpus` | Literature collection, document storage, artifact management |
| `ingestion` | Text extraction, LaTeX parsing, PDF processing |
| `retrieval` | Vector search, semantic queries, hybrid search |
| `graph` | Citation networks, authorship, Neo4j operations |
| `agent` | LangGraph workflows, multi-step research, state management |
| `interface` | MCP servers, Claude Code integration, API exposure |
| `validation` | Data quality, integrity checks, QA |
| `documentation` | Methodology, specifications, standards |
| `infrastructure` | Database, storage, compute configuration |

**Usage**: Choose the primary domain. A document about validating ingestion pipelines is `validation`, not `ingestion`.

---

### Type Tags

Document purpose and structure.

| Tag | Description |
|-----|-------------|
| `methodology` | How we do something |
| `reference` | Lookup information (data dictionary, schema) |
| `guide` | Step-by-step procedures |
| `decision-record` | Why we chose X over Y |
| `specification` | Formal requirements |
| `source-code` | Code files and scripts |
| `configuration` | Config files, parameters |
| `data-manifest` | Data inventory and provenance |

**Usage**: One type per document. If a document explains both *how* and *why*, choose the dominant purpose.

---

### Tech Tags

Technologies and external dependencies.

| Tag | Description |
|-----|-------------|
| `python` | Python scripts, libraries |
| `postgresql` | PostgreSQL database, pgvector |
| `neo4j` | Graph database operations |
| `langraph` | LangGraph agent framework |
| `mcp` | Model Context Protocol servers |
| `arxiv` | arXiv API, paper retrieval |
| `ads` | NASA ADS API, bibliographic data |
| `latex` | LaTeX parsing, pylatexenc |
| `pdf` | PDF extraction, PyMuPDF |
| `fits` | FITS header extraction, astropy |

**Usage**: Tag when the document is specific to that technology. A general corpus methodology doc doesn't need `arxiv`; a doc about arXiv query syntax does.

---

### Corpus Layer Tags

For corpus architecture documentation (from GDR quality hierarchy).

| Tag | Description |
|-----|-------------|
| `layer-ground-truth` | Structured observational data (DESI, SIMBAD, VizieR) |
| `layer-metadata` | FITS headers, observational context |
| `layer-high-fidelity` | LaTeX source text extraction |
| `layer-best-effort` | PDF text extraction (fallback) |

**Usage**: Tag corpus documents with the layer(s) they address.

---

### Architecture Layer Tags

For the Federated Knowledge Core (from GDR).

| Tag | Description |
|-----|-------------|
| `semantic-layer` | PostgreSQL, embeddings, vector search |
| `topological-layer` | Neo4j, citation graphs, authorship networks |
| `physical-layer` | SMB storage, artifact management |

**Usage**: Tag architecture documents with the layer(s) they address.

---

## 4. References

| Reference | Link |
|-----------|------|
| Main README | [../../README.md](../../README.md) |
| Interior README Template | [interior-readme-template.md](interior-readme-template.md) |
| General KB Template | [general-kb-template.md](general-kb-template.md) |

---
