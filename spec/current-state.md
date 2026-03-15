# Current State

**Last Updated:** 2026-03-14

## Status

Phase 03 (Acquisition) is **complete**. Phase 04 (Extraction) is **complete**. The project was on hold from January 3, 2026 to March 14, 2026 (~10 weeks).

All acquisition functionality is implemented, tested, and merged. The seed paper (DESIVAST DR1, arXiv:2411.00148) has been downloaded and extracted to `test_output/extracted/2411.00148/`. Extraction pipeline handles both LaTeX source and PDF fallback with automatic method selection.

## What Exists

- `src/acquisition/arxiv_client.py` — LaTeX source and PDF download from arXiv
- `src/acquisition/source_extractor.py` — Tarball extraction with security validation (path traversal, symlink checks)
- `src/extraction/models.py` — Data models for extracted papers
- `src/extraction/latex_parser.py` — LaTeX source extraction with structure preservation
- `src/extraction/bbl_parser.py` — Bibliography parsing from .bbl files
- `src/extraction/pdf_extractor.py` — PDF fallback extraction with pymupdf
- `src/extraction/pipeline.py` — Orchestration layer with LaTeX-first, PDF-fallback logic
- Metadata tracking via `download_metadata.csv`
- Centralized logging in `src/logging_config.py`
- Work logs for Phases 01-03 in `work-logs/`
- Test coverage for extraction in `tests/test_extraction/` (27 tests, all passing)

## Seed Paper Details

- **Paper:** DESIVAST DR1 (arXiv:2411.00148)
- **Location:** `test_output/extracted/2411.00148/`
- **Main tex:** `desi_bgs_voids_y1.tex`
- **Contents:** 52 figures, 1 bib file, aastex631.cls style
- **Extraction output:** `extracted.json` (40 authors, 14 sections, 80 references, LaTeX method)
- **Status:** Full extraction pipeline complete (LaTeX + PDF fallback, validated with 27 tests)

## Next Steps

### Phase 05: Storage (Next)

- Create `astronomy_rag_corpus` database on pgsql01
- Design schema (papers, chunks, embeddings)
- Evaluate embedding models — see `landscape.md` for current options
- Implement chunking strategy — contextual retrieval and hybrid search are now baseline expectations, not options

## Pending Decisions

| Decision | Context | Phase |
|----------|---------|-------|
| Embedding model | Domain-specific vs general-purpose — needs benchmarking on astronomy text | 05 |
| Chunking strategy | Section-boundary + contextual enrichment + hybrid retrieval (dense + sparse) — see `landscape.md` | 05 |
| Reranking approach | LLM-based reranking (RCS pattern from PaperQA2) vs cross-encoder reranker | 05 |

## Known Tech Debt

| Item | Location | Notes |
|------|----------|-------|
| Affiliation assignment is 1:1 sequential | `latex_parser.py:_extract_authors` | AASTeX uses indexed affiliations; multi-affiliation authors only get first one |
| BBL parsed fields contain LaTeX noise | `bbl_parser.py:_parse_bibitem` | `{Sutter}`, `{et~al.}`, `\natexlab` in author/title fields; `raw` field is clean |
| BBL `&` separator drops last author | `bbl_parser.py:~163` | `split("&")[0]` loses the author after `&` in "Smith, Jones & Brown" |
| pylatexenc loaded but unused for parsing | `latex_parser.py` | Walker/nodes created but all extraction is regex-based; works for AASTeX papers |
| Brace counting ignores LaTeX comments | `latex_parser.py:_extract_custom_commands` | A `% }` in a definition could truncate early; no impact on well-formed papers |
| `\email` regex requires no whitespace gap | `latex_parser.py:_extract_authors` | `\author{...}\email{...}` must be adjacent; newlines between them drop the email |
| Escaped braces `\{` `\}` not handled in command extraction | `latex_parser.py:_extract_custom_commands` | Definitions with literal braces (e.g., `\newcommand{\set}{\{#1\}}`) truncate |

## Blockers

- **None** — ready to begin Phase 05.

## External Dependencies

- NASA ADS API token needed for bibliographic queries (Phase 06+)
- Database creation on pgsql01 needed (Phase 05)
