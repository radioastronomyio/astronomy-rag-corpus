# Astronomy RAG Corpus Architecture

## Overview

The Astronomy RAG Corpus implements a Federated Knowledge Core architecture that separates content from context, bridged by a universal identifier. Unlike monolithic vector database approaches that flatten scientific discourse into embeddings alone, this system maintains three distinct layers optimized for different query patterns.

The architecture enables "Graph-Boosted Retrieval" — semantic search results are refined and expanded based on citation topology. This is critical for astronomy, where foundational papers describing core physics may not semantically match modern survey terminology but are topologically essential to accurate answers.

## Core Components

### Semantic Layer
**Purpose:** Store and query the textual content of papers  
**Location:** PostgreSQL with pgvector on radio-pgsql01  
**Key Characteristics:** Chunked text, embeddings, vector similarity search, full-text search fallback

### Topological Layer
**Purpose:** Store and traverse relationships between papers  
**Location:** Neo4j on radio-neo4j01  
**Key Characteristics:** Citation graphs, authorship networks, concept links, graph traversal queries

### Physical Layer
**Purpose:** Immutable storage of source artifacts  
**Location:** SMB share on radio-fs02  
**Key Characteristics:** PDF files, LaTeX source bundles, FITS headers, canonical relative paths

### Universal Key
**Purpose:** Bridge all three layers  
**Implementation:** NASA ADS Bibcode  
**Key Characteristics:** Unique per paper, stable over time, resolvable to ADS record

## Structure

```
astronomy-rag-corpus/
├── .internal-files/              # GDR documents (gitignored)
├── .kilocode/                    # Agent configuration
│   └── rules/memory-bank/        # This memory bank
├── docs/                         # Documentation
│   ├── data-science-infrastructure.md
│   └── documentation-standards/  # Templates
├── scratch/                      # Working files (gitignored)
├── src/                          # Source code
│   ├── acquisition/              # arXiv/ADS paper retrieval
│   │   ├── arxiv_client.py       # Download source and PDF
│   │   ├── source_extractor.py   # Extract and organize tarballs
│   │   └── __init__.py
│   ├── logging_config.py         # Centralized logging setup
│   └── __init__.py
├── test_output/                  # Test artifacts (gitignored)
│   ├── raw/                      # Downloaded files
│   └── extracted/                # Extracted source trees
├── work-logs/                    # Milestone development
│   ├── 01-ideation-and-setup/
│   ├── 02-github-project-frameout/
│   └── 03-arxiv-client-implementation/
└── README.md
```

**Future directories (as phases complete):**
- `src/extraction/` — LaTeX parsing, PDF fallback
- `src/retrieval/` — Hybrid search implementation
- `src/agent/` — LangGraph workflows
- `src/mcp/` — MCP server implementations
- `src/harvester/` — Bulk ADS/arXiv acquisition

## Design Patterns and Principles

### Key Patterns

- **Federated Knowledge Core:** Separate semantic, topological, and physical concerns into purpose-optimized stores
- **Bibcode-Centric Integration:** All cross-layer joins happen through bibcode, never through fragile text matching
- **LaTeX-First Extraction:** Prioritize structured source over rendered PDF to preserve mathematical fidelity
- **Canonical Relative Paths:** Store OS-agnostic paths (`YYYY/MM/Bibcode.pdf`) resolved at runtime by environment

### Design Principles

1. **Quality Hierarchy:** Ground truth data > metadata > LaTeX text > PDF text. Never promote lower-quality data when higher exists.
2. **Citation Anchoring:** Text chunks explicitly tagged with bibcode. Generated citations validated against Neo4j graph.
3. **Graceful Degradation:** If LaTeX unavailable, fall back to PDF. If PDF fails, log and skip rather than ingest garbage.

## Integration Points

### Internal Integrations
- **desi-cosmic-void-galaxies:** Primary consumer for void science literature
- **desi-qso-anomaly-detection:** Consumer for QSO/AGN methodology papers
- **desi-quasar-outflows:** Consumer for outflow physics literature

### External Integrations
- **NASA ADS API:** Bibliographic data, citation lists, abstract retrieval
- **arXiv API:** Paper downloads (PDF and LaTeX source)
- **SIMBAD/VizieR:** Object cross-references (future enhancement)

## Data Flow

```
arXiv/ADS → Harvester → SMB (artifacts) + PostgreSQL (text/embeddings) + Neo4j (citations)
                                    ↓
                            Retrieval Engine
                                    ↓
                        LangGraph Agent / MCP Server
                                    ↓
                            Claude Code / User
```

## Architectural Decisions

### Decision 1: Federated vs Monolithic Vector Store
**Date:** 2025-12-29  
**Decision:** Implement three-layer federated architecture  
**Rationale:** Scientific queries require both semantic similarity AND structural relationships. Monolithic vector stores lose citation topology.  
**Alternatives Considered:** Single pgvector database with metadata columns  
**Implications:** Higher complexity, but enables graph-boosted retrieval patterns

### Decision 2: LaTeX-First Extraction
**Date:** 2025-12-29  
**Decision:** Prioritize LaTeX source over PDF for text extraction  
**Rationale:** PDF-to-text corrupts mathematical notation, equations, and symbols. LaTeX preserves semantic structure.  
**Alternatives Considered:** PDF-only with symbol normalization  
**Implications:** More complex extraction pipeline, but dramatically higher text quality

### Decision 3: Bibcode as Universal Key
**Date:** 2025-12-29  
**Decision:** Use NASA ADS Bibcode as the cross-layer identifier  
**Rationale:** Bibcodes are stable, unique, and directly resolvable to authoritative records  
**Alternatives Considered:** arXiv ID (not all papers have one), DOI (not all papers have one)  
**Implications:** Papers without bibcodes excluded from corpus

## Constraints and Limitations

- **Infrastructure Constraint:** Must use existing Proxmox cluster resources (no cloud services)
- **Storage Constraint:** SMB share for artifacts (no S3-compatible object storage)
- **GPU Constraint:** Single A4000 (16GB vRAM) for embedding generation — batch processing required
- **Security Constraint:** MCP servers use read-only database users; human approval gates for query execution

## Future Considerations

### Planned Improvements
- Knowledge graph expansion to include astronomical objects (link papers to SIMBAD objects)
- Multi-modal embeddings for figures and tables

### Scalability Considerations
- Initial seed corpus ~1000 papers; architecture supports 100K+ with index optimization
- Embedding generation is batch-oriented to work within GPU memory constraints

### Known Technical Debt
- None yet (greenfield project)
