<!--
---
title: "Phase 02: GitHub Frameout"
description: "Project management setup, milestone definition, and task breakdown for the Astronomy RAG Corpus"
author: "VintageDon - https://github.com/vintagedon"
ai_contributor: "Claude Opus 4.5"
date: "2026-01-03"
version: "1.0"
phase: phase-02
tags:
  - domain: corpus
  - type: planning
  - tech: github
related_documents:
  - "[Main README](../../README.md)"
  - "[Phase 01: Ideation and Setup](../01-ideation-and-setup/README.md)"
  - "[GDR: Astronomy RAG Data Ingestion Plan](../../.internal-files/Astronomy%20RAG%20Data%20Ingestion%20Plan.pdf)"
---
-->

# Phase 02: GitHub Frameout

> Compiled from: Single session | January 2026  
> Status: Complete  
> Key Outcome: Milestone structure, task breakdown, and GitHub labels for the first three implementation phases

---

## 1. Objective

Define the project management structure for the astronomy RAG corpus, breaking the walking skeleton approach into discrete, testable milestones aligned with GDR section boundaries. This phase established GitHub labels and created actionable task definitions for Acquisition, Extraction, and Storage milestones.

---

## 2. Planning Context

### Original Phase Structure

The Phase 01 work established a seven-phase implementation plan:

| Phase | Name | Description |
|-------|------|-------------|
| 01 | Ideation and Setup | GDR review, repo initialization |
| 02 | Plan Review | Validate seed corpus against research priorities |
| 03 | Foundation | Walking skeleton implementation |
| 04 | Harvester | Bulk acquisition |
| 05 | Hybrid Engine | Neo4j graph construction |
| 06 | Agent | LangGraph state machine |
| 07 | Interface | MCP servers |

### Problem with Original Structure

The "Foundation" and "Harvester" phases were too coarse-grained for effective tracking. A single "walking skeleton" phase encompassed acquisition, extraction, database setup, embedding, and retrieval — too many concerns for a single milestone.

### GDR-Aligned Refinement

Reviewing the GDR document revealed natural section boundaries that map to testable deliverables:

- Section 1.1 — arXiv programmatic retrieval (self-contained)
- Section 1.2 — LaTeX/PDF text extraction (self-contained)
- Section 1.3+ — Database, embeddings, retrieval (grouped)

This suggested reorganizing around GDR sections rather than abstract phases.

---

## 3. Milestone Definitions

### Milestone 1: Acquisition

Description: Establish programmatic access to arXiv and retrieve the seed paper (DESIVAST VAC) with both PDF and LaTeX source artifacts stored in the canonical SMB location.

Scope:

- Select and validate seed paper (confirm arXiv ID, LaTeX availability)
- Define canonical storage path structure
- Implement `arxiv.py` retrieval client
- Download and organize artifacts

Success Criteria: Paper artifacts (PDF + LaTeX source) stored on SMB with captured metadata.

GDR Alignment: Section 1.1 — "Accessing the Bleeding Edge: Programmatic Retrieval from arXiv"

---

### Milestone 2: Extraction

Description: Parse LaTeX source into clean, structured text suitable for embedding, preserving mathematical notation and section hierarchy while handling edge cases gracefully.

Scope:

- Evaluate and implement `pylatexenc` parser
- Handle macro expansion, includes, and math environments
- Preserve document structure as metadata
- Build PDF fallback path using `PyMuPDF`

Success Criteria: Clean text file with preserved structure, validated against original for quality.

GDR Alignment: Section 1.2 — LaTeX extraction and text cleaning

---

### Milestone 3: Storage

Description: Provision the corpus database, design schema for papers and embeddings, implement chunking strategy, and complete the ingestion pipeline with vector storage.

Scope:

- Provision `astronomy_rag_corpus` database on pgsql01
- Design schema (papers, chunks, embeddings tables)
- Evaluate and select embedding model
- Implement chunking with section boundary awareness
- Generate embeddings and store in pgvector
- Build retrieval function with attribution

Success Criteria: End-to-end query works — semantic search returns relevant chunks with bibcode attribution.

GDR Alignment: Sections 1.3+ — Database, embeddings, and retrieval pipeline

---

## 4. Task Breakdown

### Milestone 1: Acquisition Tasks

| ID | Title | Description |
|----|-------|-------------|
| 1.1 | Select seed paper | Identify DESIVAST VAC paper bibcode, confirm arXiv ID exists, verify LaTeX source is available |
| 1.2 | Define storage paths | Establish canonical path structure on SMB (`/AstroCorpus/YYYY/MM/Bibcode/`), document path resolution for Linux/Windows |
| 1.3 | Implement arXiv client | Build retrieval script using `arxiv.py` — query by arXiv ID, capture metadata (title, authors, abstract, categories, dates) |
| 1.4 | Download artifacts | Retrieve both PDF and LaTeX `.tar.gz` source, save to canonical path, log success/failure |
| 1.5 | Extract and organize source | Unpack LaTeX archive, identify main `.tex` file, preserve directory structure for figures/includes |

### Milestone 2: Extraction Tasks

| ID | Title | Description |
|----|-------|-------------|
| 2.1 | Evaluate extraction tools | Test `pylatexenc` against seed paper, assess handling of macros, custom commands, and math environments |
| 2.2 | Implement LaTeX parser | Build extraction pipeline — resolve `\input`/`\include` references, expand standard macros, convert math to readable form |
| 2.3 | Preserve document structure | Extract section/subsection hierarchy as metadata, maintain paragraph boundaries for chunking |
| 2.4 | Handle math notation | Define strategy for equations — inline representation, LaTeX preservation, or symbolic normalization |
| 2.5 | Implement PDF fallback | Build `PyMuPDF` extraction path for papers without LaTeX source, document quality tradeoffs |
| 2.6 | Validate output quality | Manual review of extracted text against original — check for corruption, missing content, garbled math |

### Milestone 3: Storage Tasks

| ID | Title | Description |
|----|-------|-------------|
| 3.1 | Provision database | Create `astronomy_rag_corpus` database on pgsql01, enable pgvector extension, configure connection in `research.env` |
| 3.2 | Design schema | Define tables: `papers` (bibcode, metadata, paths), `chunks` (text, position, section), `embeddings` (vector, chunk FK) |
| 3.3 | Evaluate embedding models | Test candidate models (e.g., `all-MiniLM-L6-v2`, `BAAI/bge-base`, astronomy-specific if available) against sample text |
| 3.4 | Implement chunking | Build chunker respecting section boundaries, define chunk size/overlap, preserve source attribution per chunk |
| 3.5 | Generate and store embeddings | Process chunks through selected model on GPU node, insert into pgvector with metadata |
| 3.6 | Build retrieval function | Implement semantic query — embed query text, execute vector similarity search, return chunks with bibcode attribution |
| 3.7 | Validate end-to-end | Query the ingested paper, verify relevant chunks returned, confirm attribution chain intact |

---

## 5. GitHub Labels

### Milestone Labels

| Label | Color | Description |
|-------|-------|-------------|
| `milestone:acquisition` | `#1D76DB` (blue) | Milestone 1 - arXiv retrieval and artifact storage |
| `milestone:extraction` | `#5319E7` (purple) | Milestone 2 - LaTeX/PDF text extraction |
| `milestone:storage` | `#0E8A16` (green) | Milestone 3 - Database and embeddings |

### Component Labels

| Label | Color | Description |
|-------|-------|-------------|
| `component:harvester` | `#FBCA04` (yellow) | arXiv/ADS acquisition pipeline |
| `component:parser` | `#F9D0C4` (peach) | LaTeX and PDF extraction |
| `component:database` | `#BFD4F2` (light blue) | PostgreSQL/pgvector schema and queries |
| `component:embeddings` | `#D4C5F9` (lavender) | Embedding model and vector operations |

### Pipeline Stage Labels

| Label | Color | Description |
|-------|-------|-------------|
| `stage:research` | `#C5DEF5` (pale blue) | Investigation or evaluation task |
| `stage:implementation` | `#0052CC` (dark blue) | Active development |
| `stage:validation` | `#006B75` (teal) | Testing and verification |

---

## 6. Key Decisions

### Decision 1: GDR-Aligned Milestones

Decision: Structure milestones around GDR section boundaries rather than abstract phases.

Rationale: GDR sections represent self-contained, testable units of functionality. Section 1.1 (arXiv retrieval) can be completed and validated independently of Section 1.2 (extraction). This reduces risk by proving each component before integration.

Implication: More milestones, but each is tighter and lower-risk.

### Decision 2: Merge Plan Review into Acquisition

Decision: Combine seed paper selection with the Acquisition milestone rather than maintaining a separate "Plan Review" phase.

Rationale: Plan Review as originally conceived was essentially "pick one bibcode" — too lightweight for a standalone phase. Confirming arXiv ID and LaTeX availability is a natural prerequisite task within Acquisition.

Implication: Phase 02 becomes GitHub frameout; actual implementation begins in the next work phase.

### Decision 3: Defer Retrieval to Storage Milestone

Decision: Include the retrieval function in the Storage milestone rather than creating a separate Retrieval milestone.

Rationale: Retrieval is meaningless without stored embeddings. The natural success criterion for Storage is "can we query what we ingested?" — this requires building the retrieval function as part of validation.

Implication: Storage milestone is larger than Acquisition or Extraction, but maintains logical cohesion.

---

## 7. Updated Phase Structure

The project phases now reflect the refined milestone structure:

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| 01 | [Ideation and Setup](../01-ideation-and-setup/README.md) | ✅ Complete | GDR review, repo initialization |
| 02 | [GitHub Frameout](../02-github-frameout/README.md) | ✅ Complete | Milestones, tasks, labels (this phase) |
| 03 | Acquisition | ⬜ Next | arXiv retrieval, seed paper artifacts |
| 04 | Extraction | ⬜ Planned | LaTeX/PDF text extraction |
| 05 | Storage | ⬜ Planned | Database, embeddings, retrieval |
| 06 | Harvester | ⬜ Planned | Bulk acquisition, seed corpus population |
| 07 | Hybrid Engine | ⬜ Planned | Neo4j graph construction |
| 08 | Agent | ⬜ Planned | LangGraph state machine |
| 09 | Interface | ⬜ Planned | MCP servers, Claude Code integration |

---

## 8. Artifacts Produced

| Artifact | Purpose | Location |
|----------|---------|----------|
| Phase worklog | This document | work-logs/02-github-frameout/ |
| Task definitions | 18 discrete tasks across 3 milestones | Documented above, to be created as GitHub issues |
| Label taxonomy | 10 labels for milestone, component, and stage tracking | Documented above, to be created in GitHub |

---

## 9. Next Steps

### Immediate

1. Create GitHub labels as defined
2. Create GitHub issues for Milestone 1 tasks
3. Begin Milestone 1: Acquisition

### Prerequisites for Milestone 1

- GitHub repository access configured
- SMB mount accessible from development environment
- arXiv API access (no key required for basic usage)

---

## 10. Provenance

| Item | Value |
|------|-------|
| Session date | January 3, 2026 |
| Planning scope | Next 3 milestones (Acquisition, Extraction, Storage) |
| Task count | 18 tasks across 3 milestones |
| Label count | 10 new labels (3 milestone, 4 component, 3 stage) |

---

Next: [Phase 03: Acquisition](../03-acquisition/README.md)
