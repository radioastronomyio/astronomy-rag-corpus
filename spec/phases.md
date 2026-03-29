# Phases

**Source of Truth:** [GitHub Project Board](https://github.com/Proxmox-Astronomy-Lab/astronomy-rag-corpus/projects)

## Walking Skeleton (Phases 03-05)

The minimal end-to-end loop proving the architecture:

```
arXiv ID → download source → extract text → clean + bibcode → PostgreSQL → semantic query → return with attribution
```

No catalog integration, no Neo4j, no MCP — just the text pipeline.

## Phase 01: Ideation and Setup ✅

GDR review, repository initialization, documentation standards.

## Phase 02: GitHub Frameout ✅

Milestones, tasks, GitHub labels, project board setup.

## Phase 03: Acquisition ✅

Paper discovery and artifact retrieval from arXiv.

| Task | Issue | Status | Notes |
|------|-------|--------|-------|
| 1.1 Select Seed Paper | #1 | ✅ Done | DESIVAST DR1 (arXiv:2411.00148) |
| 1.2 Define Storage Paths | #2 | ✅ Done | /mnt/ai-ml/data/rag-corpus (gpu01) |
| 1.3 Implement arXiv Client | #3 | ✅ Done | `src/acquisition/arxiv_client.py` |
| 1.4 Download Artifacts | #4 | ✅ Done | PDF download + metadata CSV |
| 1.5 Extract and Organize Source | #5 | ✅ Done | `src/acquisition/source_extractor.py` with security validation |

## Phase 04: Extraction ✅ Complete

LaTeX parsing, text cleaning, and structure preservation.

| Task | Issue | Status | Notes |
|------|-------|--------|-------|
| 2.1 Evaluate Extraction Tools | #6 | ✅ Done | Decided: pylatexenc |
| 2.2 Implement LaTeX Parser | #7 | ✅ Done | `src/extraction/latex_parser.py` |
| 2.3 Preserve Document Structure | #8 | ✅ Done | Sections with hierarchy |
| 2.4 Handle Math Notation | #9 | ✅ Done | Preserve raw LaTeX math |
| 2.5 Implement PDF Fallback | #10 | ✅ Done | `src/extraction/pdf_extractor.py` + pipeline |
| 2.6 Validate Output Quality | #11 | ✅ Done | 27 validation tests passing |

**Landscape note:** PaperQA2 uses Grobid as their state-of-the-art parser. It handles sections, tables, and citations natively. Evaluated pylatexenc in Task 2.1 — sufficient for this project's needs.

## Phase 05: Storage ✅ Complete

Database provisioning, embedding pipeline, and retrieval.

| Task | Issue | Status | Notes |
|------|-------|--------|-------|
| 3.1 Provision Database | #12 | ✅ Done | `astronomy_rag_corpus` on pgsql01 |
| 3.2 Design Schema | #13 | ✅ Done | papers + chunks, pgvector(768), tsvector, HNSW/GIN indexes |
| 3.3 Evaluate Embedding Models | #14 | ✅ Done | nomic-embed-text (768d, local GPU) |
| 3.4 Implement Chunking | #15 | ✅ Done | Section-boundary + contextual enrichment (~512 tokens, 50 overlap) |
| 3.5 Generate and Store Embeddings | #16 | ✅ Done | Batch embedding with GPU support |
| 3.6 Build Retrieval Function | #17 | ✅ Done | Hybrid search (dense vector + sparse BM25 + RRF k=60) |
| 3.7 Validate End-to-End | #18 | ✅ Done | Tests implemented; end-to-end validation ready |

**Landscape note:** Hybrid retrieval (dense embeddings + BM25 sparse search + reranking) is now the baseline expectation, not an advanced option. Reranking is the single highest-ROI upgrade according to current benchmarks. The chunking strategy should incorporate contextual enrichment rather than naive fixed-size or section-only splitting.

## Phase 06: Harvester 📋

Bulk acquisition, seed corpus population via ADS API.

## Phase 07: Hybrid Engine 📋

Neo4j graph construction, citation network population, graph-boosted retrieval integration. GraphRAG pattern catalog provides implementation patterns — see landscape.md.

## Phase 08: Agent 📋

LangGraph state machine. Should follow agentic RAG pattern (tool-based decomposition: search → gather evidence → rerank → generate) rather than a fixed pipeline. PaperQA2's architecture is the reference implementation — see landscape.md.

## Phase 09: Interface 📋

MCP servers for Claude Code integration, read-only database access.

## Status Legend

| Icon | Meaning |
|------|---------|
| ✅ | Completed and closed |
| 🔄 | Actively being worked |
| ⏳ | Dependencies met, ready to start |
| 📋 | Not yet started |
