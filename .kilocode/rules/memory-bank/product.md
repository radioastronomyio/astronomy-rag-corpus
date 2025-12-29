# Astronomy RAG Corpus Product Overview

## Problems Solved

This project addresses:

- **LLM Hallucination in Scientific Contexts:** Standard LLMs confidently generate plausible-sounding but incorrect scientific claims. RAG grounds responses in verifiable literature.
- **Citation Topology Loss:** Vector-only retrieval finds semantically similar text but loses the structural relationships that define scientific consensus — which papers refute others, who the key authors are, what foundational work underpins a claim.
- **PDF Extraction Artifacts:** Mathematical notation, equations, and specialized symbols are corrupted during PDF-to-text conversion, poisoning the embedding space with garbage.
- **Disconnected Research Tools:** Literature review and data analysis happen in separate workflows. MCP integration brings literature access directly into coding sessions.

## How It Works

The Astronomy RAG Corpus implements a Federated Knowledge Core with three layers bridged by NASA ADS Bibcode:

**Semantic Layer (PostgreSQL + pgvector):** Stores chunked text and embeddings, enabling vector similarity search for "what papers say about X."

**Topological Layer (Neo4j):** Stores citation graphs, authorship networks, and concept relationships, enabling graph traversal for "how papers relate to each other."

**Physical Layer (SMB Storage):** Stores PDF and LaTeX artifacts with canonical relative paths, ensuring every retrieved claim traces back to a human-readable document.

The "Graph-Boosted Retrieval" pattern refines semantic search results by expanding context through citation topology. A query returns not just semantically similar chunks, but also highly-cited foundational papers that may not match semantically but are topologically indispensable.

## Goals and Outcomes

### Primary Goals

1. **Ground DESI Research in Literature:** Enable Claude-based research assistance with full citation attribution for void science, QSO anomaly detection, and quasar outflow projects.
2. **Preserve Scientific Structure:** Maintain citation networks and authorship relationships that define how knowledge is organized in astronomy.
3. **Enable Multi-Step Research:** Support LangGraph agents that can perform iterative literature investigation — hypothesis → evidence gathering → refinement cycles.

### User Experience Goals

- Researchers query literature naturally through Claude Code during analysis sessions
- Every claim includes traceable citations to source papers
- Graph traversal surfaces foundational papers that keyword search misses
- LaTeX-quality text preserves mathematical meaning in retrieved chunks

### Success Metrics

- **Retrieval Relevance:** Top-5 chunks include at least one directly relevant paper for domain queries
- **Citation Accuracy:** Generated citations correspond to papers actually in the corpus (no hallucinated bibcodes)
- **Coverage:** Seed corpus includes foundational papers for DESIVAST methodology and dependent research
