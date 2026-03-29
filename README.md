<!--
---
title: "Astronomy RAG Corpus"
description: "Specialized astronomical knowledge corpus for Retrieval-Augmented Generation supporting DESI research"
author: "VintageDon"
date: "2026-03-29"
version: "1.1"
status: "Active"
tags:
  - type: project-root
  - domain: [corpus, rag, astronomy]
  - tech: [python, postgresql, neo4j, langraph, mcp]
related_documents:
  - "[DESI Cosmic Void Galaxies](https://github.com/radioastronomyio/desi-cosmic-void-galaxies)"
  - "[DESI QSO Anomaly Detection](https://github.com/radioastronomyio/desi-qso-anomaly-detection)"
  - "[DESI Quasar Outflows](https://github.com/radioastronomyio/desi-quasar-outflows)"
---
-->

# 📚 Astronomy RAG Corpus

[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2016-336791?logo=postgresql)](https://www.postgresql.org/)
[![Neo4j](https://img.shields.io/badge/Graph-Neo4j%205-4581C3?logo=neo4j)](https://neo4j.com/)
[![pgvector](https://img.shields.io/badge/Vector-pgvector-336791?logo=postgresql)](https://github.com/pgvector/pgvector)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Agent-LangGraph-1C3C3C?logo=langchain)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

![Repository Banner](assets/repo-banner.jpg)

> A Federated Knowledge Core for astronomical research, decoupling semantic meaning from structural relationships to enable expert-level RAG and autonomous Deep Research agents.

This repository builds a specialized knowledge corpus from astronomical literature, designed to support Retrieval-Augmented Generation (RAG) for the DESI research portfolio. The system grounds LLM responses in verifiable scientific data, preserves citation topology, and enables multi-step research workflows through Claude Code and MCP integration.

---

## 🔭 Background

Building a scientific RAG system extends far beyond document aggregation. Astronomical literature contains complex mathematical notation, specialized terminology, and a rapidly evolving research landscape. Most critically, an AI agent for scientific discovery cannot operate on ambiguous information; its knowledge must be traceable, accurate, and contextually rich.

Retrieval-Augmented Generation (RAG) addresses LLM hallucination by grounding responses in retrieved documents. Standard RAG retrieves semantically similar text chunks, but scientific questions often require understanding *how papers relate*: which work refutes another, who the key authors are, what foundational papers underpin a claim.

![Scientific RAG Infographic](assets/scientific-rag-infographic.jpg)

This system implements a Federated Knowledge Core that separates:

- What papers say (semantic content via embeddings)
- How papers connect (citation topology via graph)
- Where artifacts live (physical storage for reproducibility)

The architecture enables "Graph-Boosted Retrieval," where semantic search results are refined by citation topology. A query about "DESI void galaxy quenching" retrieves relevant chunks, then expands context to include highly-cited foundational papers that may not semantically match but are topologically indispensable.

---

## 🎯 Research Portfolio

This corpus supports the radioastronomy.io DESI research portfolio:

| Project | Focus | Corpus Role |
|---------|-------|-------------|
| [desi-cosmic-void-galaxies](https://github.com/radioastronomyio/desi-cosmic-void-galaxies) | Environmental quenching, ARD factory | Primary consumer, void science literature |
| [desi-qso-anomaly-detection](https://github.com/radioastronomyio/desi-qso-anomaly-detection) | ML anomaly detection on QSO spectra | QSO/AGN methodology papers |
| [desi-quasar-outflows](https://github.com/radioastronomyio/desi-quasar-outflows) | AGN feedback and outflow energetics | Outflow physics literature |

Seed corpus focus: DESIVAST (void catalog methodology), central to all three projects.

---

## 🏗️ Architecture

### Federated Knowledge Core

The system decouples content from context, bridged by NASA ADS Bibcode as the universal key.

![Federated Knowledge Core](assets/federated-knowledge-core-infographic.jpg)

### Corpus Quality Hierarchy

Data sources prioritized by structure, fidelity, and reliability:

| Level | Source | Content | Fidelity |
|-------|--------|---------|----------|
| 1 | DESI, SIMBAD, VizieR | Structured catalog data | Ground truth |
| 2 | FITS Headers | Observational metadata | Instrument provenance |
| 3 | arXiv LaTeX | Clean text from source | High fidelity |
| 4 | PDF Extraction | Text from rendered documents | Best effort |

LaTeX-first extraction is critical. PDF-to-text conversion corrupts mathematical notation, mangles equations, and introduces OCR artifacts that poison the embedding space.

---

## 📋 Implementation Phases

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| 01 | [Ideation and Setup](work-logs/01-ideation-and-setup/README.md) | ✅ Complete | GDR review, repo initialization |
| 02 | [GitHub Frameout](work-logs/02-github-project-frameout/README.md) | ✅ Complete | Milestones, tasks, GitHub labels |
| 03 | [Acquisition](work-logs/03-arxiv-client-implementation/README.md) | ✅ Complete | arXiv client, PDF download, source extraction |
| 04 | Extraction | ⬜ Next | LaTeX/PDF text extraction |
| 05 | Storage | ⬜ Planned | Database, embeddings, retrieval |
| 06 | Harvester | ⬜ Planned | Bulk acquisition, seed corpus population |
| 07 | Hybrid Engine | ⬜ Planned | Neo4j graph construction |
| 08 | Agent | ⬜ Planned | LangGraph state machine |
| 09 | Interface | ⬜ Planned | MCP servers, Claude Code integration |

### Walking Skeleton (Phases 03-05)

The minimal end-to-end loop proving the architecture, split across three milestones:

```
arXiv ID → download source → LaTeX extraction → clean text + bibcode → PostgreSQL → semantic query → return with attribution
```

No catalog integration, no Neo4j, no MCP, just the text pipeline.

---

## 🖥️ Infrastructure

This project runs on the [radioastronomy.io](https://github.com/radioastronomyio/proxmox-astronomy-lab) research cluster.

| Component | Resource | Purpose |
|-----------|----------|---------|
| PostgreSQL + pgvector | radio-pgsql01 (10.25.20.8) | Semantic layer, embeddings, vector search |
| Neo4j | radio-neo4j01 (10.25.20.21) | Topological layer, citation graphs |
| SMB Storage | radio-fs02 (10.25.20.15) | Physical layer, PDF/LaTeX artifacts |
| GPU Compute | ML01 (A4000, 16GB) | Embedding generation |
| Database | `astronomy_rag_corpus` | Dedicated corpus database |

Connection patterns follow the standard `/opt/global-env/research.env` configuration.

---

## 📁 Repository Structure

```
astronomy-rag-corpus/
├── 📂 assets/                      # Figures, diagrams, banners
├── 📂 docs/
│   ├── 📂 documentation-standards/ # Templates, tagging strategy
│   └── 📄 data-science-infrastructure.md
├── 📂 internal-files/              # GDR documents, working papers
├── 📂 shared/                      # Shared resources
├── 📂 spec/                        # Project specifications
├── 📂 src/                         # Source code
│   ├── 📂 acquisition/             # arXiv/ADS paper retrieval
│   ├── 📂 extraction/              # LaTeX/PDF text extraction
│   └── 📂 storage/                 # Database, embeddings, retrieval
├── 📂 staging/                     # Staged work
├── 📂 tests/                       # Test suite
├── 📂 work-logs/                   # Milestone-based development history
├── 📄 conftest.py                  # Pytest configuration
├── 📄 requirements.txt             # Python dependencies
├── 📄 LICENSE
├── 📄 LICENSE-DATA
└── 📄 README.md                    # This file
```

---

## 🔧 Key Technologies

| Category | Technology | Purpose |
|----------|------------|---------|
| Databases | PostgreSQL 16 + pgvector | Vector storage, semantic search |
| | Neo4j 5 | Citation graphs, authorship networks |
| Ingestion | arxiv.py | arXiv paper retrieval |
| | ads | NASA ADS bibliographic data |
| | pylatexenc | LaTeX to clean text |
| | PyMuPDF | PDF extraction (fallback) |
| | astropy | FITS header extraction |
| Orchestration | LangGraph | Stateful agentic workflows |
| Interface | MCP | Claude Code integration |

---

## 🤝 OSS Program Acknowledgments

This repository benefits from open source programs that provide free or discounted tooling to qualifying public repositories.

### Active

| Program | Provides | Use Case |
|---------|----------|----------|
| [CodeRabbit](https://coderabbit.ai) | AI code review (Pro tier) | PR review with codebase context |
| [Atlassian](https://www.atlassian.com/software/views/open-source-license-request) | Jira, Confluence (Standard tier) | Project tracking, documentation |

### Available

| Program | Provides | Planned Use |
|---------|----------|-------------|
| [Snyk](https://snyk.io/plans/) | Security scanning | Dependency vulnerability detection |
| [SonarCloud](https://www.sonarsource.com/open-source-editions/) | Code quality analysis | Static analysis |

---

## 📄 License

[MIT](LICENSE) © 2025 VintageDon

---

## 🙏 Acknowledgments

- [DESI Collaboration](https://www.desi.lbl.gov/) for data releases and VAC documentation
- [NASA ADS](https://ui.adsabs.harvard.edu/) for bibliographic data and API access
- [arXiv](https://arxiv.org/) for open access preprints
- [CDS](https://cds.u-strasbg.fr/) for SIMBAD and VizieR services

---

Last Updated: 2026-03-29 | Current Phase: 04 Extraction Next
