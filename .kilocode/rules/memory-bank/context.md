# Astronomy RAG Corpus Context

## Current State
**Last Updated:** 2026-01-03

### Recent Accomplishments
- Completed Milestone 1: Acquisition (Tasks 1.3, 1.4, 1.5)
- Implemented arXiv client for LaTeX source and PDF downloads
- Implemented source tarball extraction with security validation
- Added metadata tracking via CSV during downloads
- Established dual-audience commenting standard (AI NOTEs)
- Created interior READMEs for src/ and src/acquisition/
- Fixed security issues (path traversal, symlink validation) via code review
- Added pypdf dependency for PDF validation

### Current Phase

We are currently in **Phase 03: Acquisition** which is now **complete**. Milestone 1 delivered a functional acquisition module that can download and extract arXiv papers.

### Active Work

Phase 03 complete. Ready to transition to Phase 04: Extraction.

## Next Steps

### Immediate (Next Session)
1. Create work-logs/04-text-extraction/ directory
2. Begin Task 2.1: Evaluate extraction tools (pylatexenc, TexSoup, pandoc)
3. Test pylatexenc against extracted DESIVAST source files
4. Document extraction quality findings

### Near-Term (Phase 04: Extraction)
- Task 2.1: Evaluate extraction tools
- Task 2.2: Implement LaTeX parser
- Task 2.3: Preserve document structure (sections, paragraphs)
- Task 2.4: Handle math notation (strategy TBD)
- Task 2.5: Implement PDF fallback with orchestration logic
- Task 2.6: Validate output quality against original

### Future (Phases 05-09)
- Phase 05: Storage — Database provisioning, embeddings, retrieval
- Phase 06: Harvester — Bulk acquisition, seed corpus population
- Phase 07: Hybrid Engine — Neo4j graph construction
- Phase 08: Agent — LangGraph state machine
- Phase 09: Interface — MCP servers, Claude Code integration

## Active Decisions

### Pending Decisions
- **Embedding model selection:** Which sentence-transformer model for astronomy domain? (Phase 05)
- **Chunking strategy:** Section-boundary vs fixed-size chunks (Phase 05)
- **Math notation handling:** LaTeX preservation vs symbolic normalization vs readable form (Phase 04)

### Recent Decisions

- **2026-01-03 — Security validation:** Use Path.resolve() + relative_to() for tarball path traversal checks, add symlink validation
- **2026-01-03 — Metadata tracking:** Log all downloads to CSV during development for batch analysis
- **2026-01-03 — PDF validation:** Two-layer validation (magic bytes + pypdf structural parse)
- **2026-01-03 — Parallel artifacts:** download_source() and download_pdf() are independent; fallback orchestration in Task 2.5
- **2026-01-03 — GLM via KiloCode:** Use GLM 4.7 for implementation, Claude for code review
- **2025-12-29 — Dedicated database:** Corpus gets its own `astronomy_rag_corpus` database on pgsql01
- **2025-12-29 — DESIVAST seed focus:** Start with void catalog methodology papers

## Blockers and Dependencies

### Current Blockers
- None

### External Dependencies
- **Database creation:** Need to create `astronomy_rag_corpus` database on pgsql01 (Phase 05)
- **NASA ADS token:** Need valid API token for bibliographic queries (Phase 06+)

## Notes and Observations

### Recent Insights
- GLM produces solid first-pass code but requires review for edge cases and security
- Detailed prompts about environment prevent wasted iterations with KiloCode
- KiloCode shell mode has Windows path issues; use integrated terminal
- Claude.ai code review catches issues KiloCode misses (deprecated APIs, import scoping, security)
- Dual-audience commenting (AI NOTEs) should be added during review, not left to implementation agent

### Context for Next Session
- Seed paper extracted to test_output/extracted/2411.00148/
- Main tex file: desi_bgs_voids_y1.tex
- 52 figures, 1 bib file, standard aastex631.cls style
- Ready for LaTeX extraction testing with pylatexenc
