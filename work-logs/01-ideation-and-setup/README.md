<!--
---
title: "Phase 01: Ideation and Setup"
description: "Project conception, repository scaffolding, and architecture decisions for the Astronomy RAG Corpus"
author: "VintageDon - https://github.com/vintagedon"
ai_contributor: "Claude Opus 4.5"
date: "2025-12-29"
version: "1.0"
phase: phase-01
tags:
  - domain: corpus
  - type: methodology
  - tech: postgresql, neo4j, rag
related_documents:
  - "[Main README](../../README.md)"
  - "[Data Science Infrastructure](../../docs/data-science-infrastructure.md)"
---
-->

# Phase 01: Ideation and Setup

> Compiled from: Single session | December 2025  
> Status: Complete  
> Key Outcome: Repository scaffolding, architecture documentation, and federated knowledge core design for astronomical literature RAG

---

## 1. Objective

Establish the foundation for a specialized astronomical knowledge corpus supporting Retrieval-Augmented Generation. This phase reviewed prior GDR documents, defined the Federated Knowledge Core architecture, and scaffolded the repository with documentation standards adapted from the DESI research portfolio.

---

## 2. Scientific Context

### The Problem

Scientific RAG systems face challenges that general-purpose approaches cannot address. Astronomical literature contains complex mathematical notation that PDF extraction corrupts, specialized terminology that embedding models struggle with, and a rapidly evolving research landscape. Most critically, an AI agent for scientific discovery cannot operate on ambiguous information — its knowledge must be traceable, accurate, and contextually rich.

Standard vector-only RAG retrieves semantically similar text chunks but loses the structural relationships that define scientific consensus. A paper refuting another's methodology may not share semantic content with the original, but understanding that relationship is essential for accurate synthesis.

### The Opportunity

The Proxmox Astronomy Lab's DESI research portfolio — cosmic void galaxies, QSO anomaly detection, and quasar outflows — shares common literature needs. A centralized corpus supporting all three projects provides:

- Consistent literature grounding across the portfolio
- Citation topology preserved for multi-step research
- Claude Code integration via MCP for natural querying during analysis
- Reduced hallucination through verifiable source attribution

### Target Domain

The seed corpus focuses on DESIVAST (void catalog methodology), which is central to all three downstream projects. This provides a constrained, well-defined domain for proving the architecture before expansion.

---

## 3. Source Material

Two Gemini Deep Research documents from mid-2025 provided the architectural foundation:

| Document | Focus | Key Contributions |
|----------|-------|-------------------|
| Astronomy RAG Data Ingestion Plan.pdf | Corpus quality hierarchy, ingestion pipeline | Four-level data quality hierarchy, Python implementation patterns |
| Building Astronomy RAG Corpus.md | Federated architecture, implementation phases | Three-layer knowledge core, walking skeleton approach, MCP integration |

Both documents remain architecturally sound. No major revisions were needed — the infrastructure mapping to actual cluster resources was the primary adaptation required.

---

## 4. Key Architectural Decisions

### Decision 1: Federated Knowledge Core

**Decision:** Separate semantic content, structural relationships, and physical artifacts into purpose-optimized stores.

**Rationale:** Scientific queries require both semantic similarity (what papers say) AND structural relationships (how papers connect). Monolithic vector databases flatten citation topology into metadata fields that cannot be efficiently traversed.

**Implementation:**
- Semantic Layer: PostgreSQL with pgvector for embeddings and vector search
- Topological Layer: Neo4j for citation graphs and authorship networks
- Physical Layer: SMB storage for PDF/LaTeX artifacts with canonical paths

**Implications:** Higher complexity than single-store approaches, but enables graph-boosted retrieval patterns that surface foundational papers keyword search would miss.

### Decision 2: Bibcode as Universal Key

**Decision:** Use NASA ADS Bibcode as the cross-layer identifier bridging all three stores.

**Rationale:** Bibcodes are stable (don't change after assignment), unique (one per paper), and directly resolvable to authoritative ADS records. Alternative identifiers have coverage gaps — not all papers have arXiv IDs or DOIs.

**Implications:** Papers without bibcodes are excluded from the corpus. This is acceptable for the astronomy domain where ADS coverage is comprehensive.

### Decision 3: LaTeX-First Extraction

**Decision:** Prioritize LaTeX source over PDF for text extraction.

**Rationale:** PDF-to-text conversion corrupts mathematical notation, mangles equations, and introduces OCR artifacts. A paper's equation `$\Lambda$CDM` becomes garbage like `CDM` or `ACDM`. This corrupted text poisons the embedding space and degrades retrieval quality.

**Alternatives Considered:** PDF-only with symbol normalization post-processing. Rejected because normalization cannot recover semantic meaning from corrupted equations.

**Implications:** More complex extraction pipeline with fallback handling, but dramatically higher text fidelity. arXiv provides LaTeX source for most papers; PDF is the fallback for older or journal-only publications.

### Decision 4: Corpus Quality Hierarchy

**Decision:** Establish a four-level hierarchy prioritizing data sources by fidelity.

| Level | Source | Fidelity | Use |
|-------|--------|----------|-----|
| 1 | DESI, SIMBAD, VizieR catalogs | Ground truth | Factual grounding |
| 2 | FITS headers | Instrument provenance | Observational context |
| 3 | arXiv LaTeX source | High fidelity | Primary text |
| 4 | PDF extraction | Best effort | Fallback only |

**Rationale:** Never promote lower-quality data when higher exists. Ground truth catalog data anchors claims; PDF text fills gaps when LaTeX unavailable.

### Decision 5: Walking Skeleton Approach

**Decision:** Prove the minimal end-to-end loop before adding complexity.

**Scope:** Single arXiv paper → LaTeX extraction → clean text + bibcode → PostgreSQL → semantic query → return with attribution

**Rationale:** Complex systems fail in integration, not components. The walking skeleton validates that the pieces connect before investing in bulk ingestion, graph construction, or agent workflows.

**Implications:** Phase 03 (Foundation) delivers a working retrieval loop with minimal features. Subsequent phases add capability incrementally.

---

## 5. Infrastructure Mapping

The GDR documents assumed generic infrastructure. This phase mapped requirements to actual Proxmox cluster resources.

### Compute Resources

| Component | Resource | Specs | Purpose |
|-----------|----------|-------|---------|
| PostgreSQL + pgvector | radio-pgsql01 | 8 vCPU, 32GB RAM | Semantic layer |
| Neo4j | radio-neo4j01 | 6 vCPU, 24GB RAM | Topological layer |
| SMB Storage | radio-fs02 | Windows Server 2025 | Physical layer |
| GPU | radio-gpu01 | A4000, 16GB vRAM | Embedding generation |

### Database Allocation

**Decision:** Dedicated `astronomy_rag_corpus` database on pgsql01.

**Rationale:** Separation from existing DESI catalog data (desi_void_desivast, desi_void_fastspecfit) keeps literature and observational data cleanly partitioned.

### Path Resolution

**Challenge:** Linux VMs mount SMB at `/mnt/astro_corpus/`; Windows uses UNC paths `\\radio-fs02\AstroCorpus\`.

**Solution:** Store canonical relative paths (`YYYY/MM/Bibcode.pdf`) in database; resolve to OS-specific absolute paths at runtime via environment detection.

---

## 6. Repository Structure

```
astronomy-rag-corpus/
├── .internal-files/              # GDR documents (gitignored)
├── .kilocode/                    # Agent configuration
│   └── rules/memory-bank/        # Persistent context
├── docs/                         # Documentation
│   ├── data-science-infrastructure.md
│   └── documentation-standards/  # Templates (8 files)
├── scratch/                      # Working files (gitignored)
├── work-logs/                    # Milestone development
│   └── 01-ideation-and-setup/    # This phase
└── README.md
```

### Future Directories (as phases complete)

```
├── src/
│   ├── harvester/                # ADS/arXiv acquisition
│   ├── extraction/               # LaTeX/PDF processing
│   ├── retrieval/                # Hybrid search
│   ├── agent/                    # LangGraph workflows
│   └── mcp/                      # MCP servers
```

### Documentation Standards

Adapted from desi-cosmic-void-galaxies with RAG corpus-specific modifications:

| Template | Purpose |
|----------|---------|
| interior-readme-template.md | Directory navigation |
| worklog-readme-template.md | Phase documentation |
| general-kb-template.md | Standalone documents |
| tagging-strategy.md | Controlled vocabulary |
| script-header-*.md | Python, Shell, PowerShell headers |

**Key Adaptations:**
- Phase tags updated: Foundation → Harvester → Hybrid Engine → Agent → Interface
- Domain tags updated: corpus, ingestion, retrieval, graph, agent, interface
- Tech tags updated: arxiv, ads, latex, langraph, mcp
- Corpus layer tags added: ground-truth, metadata, high-fidelity, best-effort
- Architecture layer tags added: semantic-layer, topological-layer, physical-layer

---

## 7. Implementation Phases

| Phase | Name | Description | Status |
|-------|------|-------------|--------|
| 01 | Ideation and Setup | GDR review, repo scaffolding | ✅ Complete |
| 02 | Plan Review | Validate seed corpus against 2026 research priorities | ⬜ Next |
| 03 | Foundation | Walking skeleton (single paper → retrieval) | ⬜ Planned |
| 04 | Harvester | Bulk ADS/arXiv acquisition, seed corpus population | ⬜ Planned |
| 05 | Hybrid Engine | Neo4j graph construction, hybrid retrieval | ⬜ Planned |
| 06 | Agent | LangGraph state machine, multi-step research | ⬜ Planned |
| 07 | Interface | MCP servers, Claude Code integration | ⬜ Planned |

---

## 8. Technology Stack

### Primary Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Implementation language |
| PostgreSQL | 16 | Semantic layer, embeddings |
| pgvector | Latest | Vector similarity search |
| Neo4j | 5 | Topological layer, citation graphs |
| LangGraph | Latest | Stateful agent orchestration |

### Ingestion Libraries

| Library | Purpose |
|---------|---------|
| arxiv.py | arXiv paper retrieval |
| ads | NASA ADS bibliographic data |
| pylatexenc | LaTeX → clean text |
| PyMuPDF | PDF extraction (fallback) |
| astropy | FITS header handling |

### Integration

| Technology | Purpose |
|------------|---------|
| MCP SDK | Claude Code integration |
| sentence-transformers | Embedding generation |

---

## 9. Research Portfolio Integration

### Downstream Consumers

| Project | Focus | Corpus Role |
|---------|-------|-------------|
| desi-cosmic-void-galaxies | Environmental quenching, ARD factory | Void science literature |
| desi-qso-anomaly-detection | ML anomaly detection on QSO spectra | QSO/AGN methodology |
| desi-quasar-outflows | AGN feedback and outflow energetics | Outflow physics |

### Seed Corpus Focus

DESIVAST papers — void catalog methodology and foundational void science literature. This is central to all three projects, providing a constrained domain for initial development.

---

## 10. Artifacts Produced

| Artifact | Purpose | Location |
|----------|---------|----------|
| Primary README | Project overview, architecture diagrams | Repository root |
| Interior READMEs | Directory navigation (4 files) | docs/, work-logs/, etc. |
| Documentation standards | Templates and tagging (8 files) | docs/documentation-standards/ |
| Memory bank | AI agent context (7 files) | .kilocode/rules/memory-bank/ |
| Phase worklog | This document | work-logs/01-ideation-and-setup/ |

---

## 11. Lessons Learned

| Challenge | Resolution |
|-----------|------------|
| GDR currency | Documents from mid-2025 remain architecturally sound; no major revisions needed |
| Infrastructure mapping | Actual cluster resources slot cleanly into GDR design; dedicated database preferred |
| Template adaptation | Domain/phase tags customized for RAG corpus; structure unchanged |

**Key Insight:** The Federated Knowledge Core architecture inverts traditional RAG thinking. Instead of flattening everything into a vector store and hoping metadata filters recover structure, preserve structure explicitly in a graph database and use vectors for semantic access. The marginal complexity is justified by the retrieval patterns it enables.

---

## 12. Next Phase

**Enables:** Phase 02 (Plan Review) can now validate seed corpus selection against 2026 research priorities.

**Dependencies resolved:** Repository structure, documentation standards, architecture decisions all established.

**Open items for Phase 02:**
- Review 2026 research priorities across DESI portfolio
- Validate DESIVAST as seed corpus focus
- Identify specific arXiv IDs for initial harvesting
- Confirm paper selection covers downstream project needs

---

## 13. Provenance

| Item | Value |
|------|-------|
| Repository created | December 2025 |
| Python target | 3.11+ |
| Primary runtime | Proxmox Astronomy Lab cluster |
| GDR sources | Astronomy RAG Data Ingestion Plan.pdf, Building Astronomy RAG Corpus.md |

---

Next: [Phase 02: Plan Review](../02-plan-review/README.md)
