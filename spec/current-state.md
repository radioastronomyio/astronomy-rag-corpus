# Current State

**Last Updated:** 2026-03-14

## Status

Phase 03 (Acquisition) is **complete**. Phase 04 (Extraction) has not been started. The project has been on hold since January 3, 2026 (~10 weeks).

All acquisition functionality is implemented, tested, and merged. The seed paper (DESIVAST DR1, arXiv:2411.00148) has been downloaded and extracted to `test_output/extracted/2411.00148/`.

## What Exists

- `src/acquisition/arxiv_client.py` — LaTeX source and PDF download from arXiv
- `src/acquisition/source_extractor.py` — Tarball extraction with security validation (path traversal, symlink checks)
- Metadata tracking via `download_metadata.csv`
- Centralized logging in `src/logging_config.py`
- Work logs for Phases 01-03 in `work-logs/`

## Seed Paper Details

- **Paper:** DESIVAST DR1 (arXiv:2411.00148)
- **Location:** `test_output/extracted/2411.00148/`
- **Main tex:** `desi_bgs_voids_y1.tex`
- **Contents:** 52 figures, 1 bib file, aastex631.cls style
- **Ready for:** LaTeX extraction testing

## Next Steps

### Immediate

1. Create `spec/` directory and migrate from `.kilocode/` memory bank (in progress)
2. Delete `.kilocode/` directory after migration
3. Begin Phase 04: Extraction — evaluate tools against the seed paper

### Phase 04: Extraction (Next)

- Evaluate extraction tools: pylatexenc, Grobid, TexSoup, pandoc
- Implement LaTeX parser with structure preservation
- Decide math notation handling strategy
- Implement PDF fallback with orchestration logic
- Validate output quality against original paper

### Phase 05: Storage (After Extraction)

- Create `astronomy_rag_corpus` database on pgsql01
- Design schema (papers, chunks, embeddings)
- Evaluate embedding models — see `landscape.md` for current options
- Implement chunking strategy — contextual retrieval and hybrid search are now baseline expectations, not options

## Pending Decisions

| Decision | Context | Phase |
|----------|---------|-------|
| Extraction tooling | pylatexenc vs Grobid vs hybrid — Grobid handles sections/tables/citations natively, PaperQA2 uses it as SOTA parser | 04 |
| Math notation handling | LaTeX preservation vs symbolic normalization vs readable form | 04 |
| Embedding model | Domain-specific vs general-purpose — needs benchmarking on astronomy text | 05 |
| Chunking strategy | Section-boundary + contextual enrichment + hybrid retrieval (dense + sparse) — see `landscape.md` | 05 |
| Reranking approach | LLM-based reranking (RCS pattern from PaperQA2) vs cross-encoder reranker | 05 |

## Blockers

- **None** — ready to begin Phase 04.

## External Dependencies

- NASA ADS API token needed for bibliographic queries (Phase 06+)
- Database creation on pgsql01 needed (Phase 05)
