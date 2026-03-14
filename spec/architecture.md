# Architecture

## Federated Knowledge Core

The system separates content from context, bridged by NASA ADS Bibcode as the universal key. Unlike monolithic vector database approaches that flatten scientific discourse into embeddings alone, three distinct layers are optimized for different query patterns.

### Semantic Layer

- **Purpose:** Store and query the textual content of papers
- **Implementation:** PostgreSQL 16 with pgvector on radio-pgsql01
- **Capabilities:** Chunked text, embeddings, vector similarity search, full-text search fallback

### Topological Layer

- **Purpose:** Store and traverse relationships between papers
- **Implementation:** Neo4j 5 on radio-neo4j01
- **Capabilities:** Citation graphs, authorship networks, concept links, graph traversal queries

### Physical Layer

- **Purpose:** Immutable storage of source artifacts
- **Implementation:** SMB share on radio-fs02
- **Capabilities:** PDF files, LaTeX source bundles, FITS headers, canonical relative paths (`YYYY/MM/Bibcode.pdf`)

### Universal Key

NASA ADS Bibcode bridges all three layers. Papers without bibcodes are excluded from the corpus. Bibcodes are stable, unique, and directly resolvable to authoritative ADS records.

## Graph-Boosted Retrieval

Semantic search results are refined and expanded based on citation topology. A query about "DESI void galaxy quenching" retrieves relevant chunks, then expands context via the citation graph to include foundational papers that may not semantically match but are topologically indispensable.

This pattern is validated by PaperQA2's citation traversal approach and the broader GraphRAG pattern catalog — see `landscape.md` for current state of the art.

## Data Flow

```
arXiv/ADS → Harvester → SMB (artifacts) + PostgreSQL (text/embeddings) + Neo4j (citations)
                                    ↓
                            Retrieval Engine (hybrid: dense + sparse + graph)
                                    ↓
                        LangGraph Agent / MCP Server
                                    ↓
                            Claude Code / User
```

## Repository Structure

```
astronomy-rag-corpus/
├── spec/                         # Project specification (this directory)
├── docs/                         # Documentation
│   ├── data-science-infrastructure.md
│   └── documentation-standards/
├── src/                          # Source code
│   ├── acquisition/              # arXiv/ADS paper retrieval (complete)
│   │   ├── arxiv_client.py       # Download source and PDF
│   │   ├── source_extractor.py   # Extract and organize tarballs
│   │   └── __init__.py
│   └── logging_config.py         # Centralized logging setup
├── scratch/                      # Working files (gitignored)
├── test_output/                  # Test artifacts (gitignored)
├── work-logs/                    # Milestone development logs
├── AGENTS.md                     # Agent router
└── README.md                     # Public-facing README
```

Future source directories as phases complete:

- `src/extraction/` — LaTeX parsing, PDF fallback
- `src/retrieval/` — Hybrid search implementation
- `src/agent/` — LangGraph workflows
- `src/mcp/` — MCP server implementations
- `src/harvester/` — Bulk ADS/arXiv acquisition

## Design Decisions

### Federated vs Monolithic Vector Store (2025-12-29)

**Decision:** Three-layer federated architecture.
**Rationale:** Scientific queries require both semantic similarity AND structural relationships. Monolithic vector stores lose citation topology.
**Trade-off:** Higher complexity, but enables graph-boosted retrieval.

### LaTeX-First Extraction (2025-12-29)

**Decision:** Prioritize LaTeX source over PDF for text extraction.
**Rationale:** PDF-to-text corrupts mathematical notation, equations, and symbols. LaTeX preserves semantic structure.
**Trade-off:** More complex extraction pipeline, dramatically higher text quality.

### Bibcode as Universal Key (2025-12-29)

**Decision:** NASA ADS Bibcode for cross-layer identification.
**Rationale:** Stable, unique, directly resolvable. arXiv IDs and DOIs don't cover all papers.
**Trade-off:** Papers without bibcodes excluded from corpus.

## Design Principles

1. **Quality Hierarchy:** Ground truth data > metadata > LaTeX text > PDF text. Never promote lower-quality data when higher exists.
2. **Citation Anchoring:** Text chunks explicitly tagged with bibcode. Generated citations validated against Neo4j graph.
3. **Graceful Degradation:** If LaTeX unavailable, fall back to PDF. If PDF fails, log and skip rather than ingest garbage.

## Constraints

- Must use existing cluster resources (no cloud services)
- SMB share for artifacts (no S3-compatible object storage)
- GPU memory constrains embedding batch sizes — batch processing required
- MCP servers use read-only database users; human approval gates for query execution
