# AGENTS.md

Entry point for AI coding agents working on this repository.

## Project Identity

**Domain:** Scientific RAG / Knowledge Engineering
**Repository:** https://github.com/radioastronomyio/astronomy-rag-corpus
**Purpose:** A Federated Knowledge Core for astronomical research literature, supporting Retrieval-Augmented Generation for the DESI research portfolio. The system decouples semantic content (PostgreSQL + pgvector), topological relationships (Neo4j), and physical artifacts (SMB storage), unified by NASA ADS Bibcode as the universal identifier.

**Primary consumers:**

| Project | Repository | Corpus Role |
|---------|-----------|-------------|
| DESI Cosmic Void Galaxies | [desi-cosmic-void-galaxies](https://github.com/radioastronomyio/desi-cosmic-void-galaxies) | Void science literature |
| DESI QSO Anomaly Detection | [desi-qso-anomaly-detection](https://github.com/radioastronomyio/desi-qso-anomaly-detection) | QSO/AGN methodology papers |
| DESI Quasar Outflows | [desi-quasar-outflows](https://github.com/radioastronomyio/desi-quasar-outflows) | Outflow physics literature |

## Current State

**Phase:** Phase 04 (Extraction) next. Phases 01-03 complete (ideation, frameout, arXiv acquisition client).
**Date:** March 2026

See `spec/current-state.md` for detailed status.

## Spec Directory

Detailed project context lives in `spec/`. Load only what you need for the task at hand.

| File | Contents | Read when... |
|------|----------|--------------|
| [current-state.md](spec/current-state.md) | Where we are, recent work, next steps, blockers | Starting any session, always read this first |
| [architecture.md](spec/architecture.md) | System design, layer responsibilities, design decisions, data flow | Designing components, making structural decisions |
| [phases.md](spec/phases.md) | Milestone plan, task statuses, pending decisions | Planning work, picking up tasks |
| [tech-stack.md](spec/tech-stack.md) | Dependencies, connection patterns, env setup, external service constraints | Writing code, debugging connectivity |
| [landscape.md](spec/landscape.md) | RAG/GraphRAG evolution, techniques to consider, prior art | Making design decisions about chunking, retrieval, embedding |

## Session Pattern

1. Read `spec/current-state.md` to orient
2. Load additional spec files relevant to the task
3. Do work
4. Update `spec/current-state.md` before session ends
5. Update other spec files if relevant changes occurred

## Execution Environment

**Primary execution:** ML01 (`/opt/repos/astronomy-rag-corpus/`)
**Agent runtime:** OpenCode (global config at `~/.config/opencode/opencode.json`)
**Session management:** aoe (Agent of Empires)
**Strategic work:** Claude.ai Projects
**Agentic coding:** Claude Code, OpenCode

## Infrastructure

| Component | Resource | Purpose |
|-----------|----------|---------|
| PostgreSQL + pgvector | radio-pgsql01 (10.25.20.8) | Semantic layer, embeddings, vector search |
| Neo4j | radio-neo4j01 (10.25.20.21) | Topological layer, citation graphs |
| SMB Storage | radio-fs02 (10.25.20.15) | Physical layer, PDF/LaTeX artifacts |
| GPU Compute | ML01 (A4000, 16GB) | Embedding generation |
| Database | `astronomy_rag_corpus` | Dedicated corpus database |

Connection patterns follow `/opt/global-env/research.env`. Never hardcode credentials.

## Repository Structure

```
astronomy-rag-corpus/
├── assets/                       # Figures, diagrams, banners
├── docs/
│   ├── documentation-standards/  # Templates, tagging strategy
│   └── data-science-infrastructure.md
├── internal-files/               # GDR documents, working papers
├── shared/                       # Shared resources
├── spec/                         # Project specifications (gitignored)
├── src/                          # Source code
│   ├── acquisition/              # arXiv/ADS paper retrieval
│   ├── extraction/               # LaTeX/PDF text extraction
│   └── storage/                  # Database, embeddings, retrieval
├── staging/                      # Staged work (gitignored)
├── tests/                        # Test suite
├── work-logs/                    # Milestone-based development history
├── AGENTS.md                     # This file
├── CLAUDE.md                     # Pointer to AGENTS.md
├── conftest.py                   # Pytest configuration
├── requirements.txt              # Python dependencies
├── LICENSE                       # MIT
└── LICENSE-DATA                  # Dataset-specific terms
```

## Conventions

- **Commits:** Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- **Branches:** Feature branches off main, PR for merge
- **Code style:** Type hints on all signatures, NumPy-style docstrings, error handling for network/database failures
- **Frontmatter:** YAML frontmatter with tags from `docs/documentation-standards/tagging-strategy.md`
- **Interior READMEs:** Every directory has one

## Related Repositories

| Repository | Relationship |
|-----------|-------------|
| `desi-cosmic-void-galaxies` | Primary consumer, void science literature |
| `desi-qso-anomaly-detection` | Consumer, QSO/AGN methodology papers |
| `desi-quasar-outflows` | Consumer, outflow physics literature |
| `analysis-ready-dataset` | ARD methodology, shared infrastructure patterns |
