# Landscape

**Last Reviewed:** 2026-03-14

This file tracks developments in RAG, GraphRAG, and scientific literature processing that may influence design decisions. Updated periodically (target: every ~90 days or before major phase transitions).

## PaperQA2 — Scientific RAG Reference Implementation

FutureHouse's PaperQA2 is the current state of the art for scientific literature RAG. It achieved superhuman performance on question answering, summarization, and contradiction detection tasks. Key design elements:

- **Agentic architecture:** RAG decomposed into tools (Paper Search, Gather Evidence, Citation Traversal, Generate Answer) invoked by a language agent, not a fixed pipeline. The agent iteratively refines queries and evaluates candidate answers.
- **Reranking and Contextual Summarization (RCS):** After initial dense vector retrieval, each chunk is scored and summarized by an LLM in the context of the query. This is the highest-impact design choice — it filters noise and allows examining far more text per question.
- **Citation traversal:** Exploits the citation graph as hierarchical indexing. Papers found as citers/citees of relevant chunks are added as additional sources. This directly validates our Neo4j topological layer.
- **Grobid parser:** Used as the state-of-the-art document parser for sections, tables, and citations. Worth evaluating alongside pylatexenc in Phase 04.

**Relevance:** Our architecture aligns well with PaperQA2's approach. The federated knowledge core (semantic + topological + physical) maps to their tool decomposition. The LangGraph agent in Phase 08 should follow this pattern.

**Source:** arxiv.org/abs/2409.13740, futurehouse.org

## CosmoPaperQA — Astronomy-Specific RAG Benchmark

A July 2025 paper introduced CosmoPaperQA, a benchmark of 105 expert-validated Q&A pairs for evaluating RAG agents in astrophysics, along with SciRag, a modular evaluation framework. Findings:

- Commercial RAG solutions (OpenAI Assistant: 89-91%, VertexAI: 87%) outperformed academic tools (PaperQA2: 82%) on this benchmark
- Hybrid architectures (ChromaDB + mixed embeddings) showed competitive performance at lower cost
- Baseline LLMs without RAG scored ~16% — confirming RAG is essential for expert-level scientific queries
- 5000-token chunks with 250-token overlap were used for scientific documents

**Relevance:** Provides concrete evaluation methodology we can adopt. Validates that domain-specific benchmarking matters.

**Source:** arxiv.org/abs/2507.07155

## Chunking Evolution

The field has moved past the binary of "fixed-size vs section-boundary" chunking:

- **Contextual retrieval:** Before embedding, each chunk is enriched with document-level context (title, section path, short summary). Makes chunks self-contained. Higher compute cost but preserves semantic coherence.
- **Late chunking:** Process entire document through a long-context embedding model, then chunk the token representations. Preserves global context in embeddings without LLM cost. Requires compatible embedding models (e.g., jina-embeddings-v3).
- **Cross-granularity retrieval:** Index at sentence level, assemble context at query time. Avoids boundary failures.
- **Semantic chunking:** Split by meaning rather than token count. Up to ~70% retrieval improvement over naive baselines in benchmarks.

**Practical consensus (as of early 2026):**
- Start with recursive/semantic chunking at 256-512 tokens
- Add contextual enrichment before embedding
- Use hybrid retrieval (dense + sparse/BM25) with reciprocal rank fusion
- Add reranking as the single highest-ROI post-retrieval step

**Relevance:** Phase 05 chunking decisions should treat hybrid retrieval + reranking as the baseline, not an advanced option.

## GraphRAG Maturation

Graph-enhanced RAG is now a well-documented pattern class:

- **Neo4j as de facto standard:** Combines graph database + vector search natively. Our existing Neo4j infrastructure is well-positioned.
- **GraphRAG Pattern Catalog:** Open-source catalog of graph retrieval patterns (graphrag.com). Provides concrete implementation references.
- **LazyGraphRAG:** Microsoft's approach reduces indexing cost to 0.1% of full GraphRAG while maintaining query performance. Relevant for scaling beyond the seed corpus.
- **LinearRAG:** Relation-free graph construction method, accepted at ICLR 2026. Simplifies knowledge graph building.
- **Key challenge identified:** Noisy retrieval from graphs can degrade performance. GraphRAG-FI (EMNLP 2025) proposes filtering + integration to balance external knowledge with LLM reasoning.

**Relevance:** Phase 07 (Hybrid Engine) has more implementation options than when originally planned. The pattern catalog and LazyGraphRAG are worth reviewing before building.

## Embedding Models to Evaluate

For Phase 05, current options worth benchmarking on astronomy text:

- **General-purpose:** OpenAI text-embedding-3-large, Gemini text-embedding-001 (top MTEB scores)
- **Open-source:** jina-embeddings-v3 (supports late chunking), BGE-large, nomic-embed
- **Scientific:** No astronomy-specific embedding model exists yet, but domain fine-tuning on astronomy abstracts is feasible with sentence-transformers
- **Local option:** Any model that fits in GPU memory for batch processing

The CosmoPaperQA benchmark showed that embedding model choice matters less than the reranking step — a mediocre embedding model with good reranking outperforms a great embedding model without it.

## Things to Revisit Before Each Phase

| Before Phase | Review |
|-------------|--------|
| 04 (Extraction) | Grobid capabilities, any new LaTeX parsing tools |
| 05 (Storage) | Embedding model benchmarks, chunking best practices, reranking options |
| 07 (Hybrid Engine) | GraphRAG pattern catalog, LazyGraphRAG, Neo4j vector search capabilities |
| 08 (Agent) | PaperQA2 architecture updates, LangGraph evolution, agentic RAG patterns |
