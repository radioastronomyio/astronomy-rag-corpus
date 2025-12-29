# Astronomy RAG Corpus Context

## Current State
**Last Updated:** 2025-12-29

### Recent Accomplishments
- Reviewed GDR documents (Astronomy RAG Data Ingestion Plan, Building Astronomy RAG Corpus)
- Established repository structure with documentation standards
- Created interior READMEs for all directories
- Wrote Phase 01 worklog documenting ideation and setup
- Completed primary README with architecture diagrams
- Updated memory bank files with project context

### Current Phase

We are currently in **Phase 01: Ideation and Setup** which is now complete. The repository is framed, documented, and ready for initial commit.

### Active Work

Phase 01 complete. Ready to transition to Phase 02.

## Next Steps

### Immediate (Next Session)
1. Clean up `README-pending.md` placeholder files (PowerShell one-liner provided)
2. Initial commit to repository
3. Begin Phase 02: Plan Review

### Near-Term (Phase 02: Plan Review)
- Review 2026 research priorities across DESI portfolio
- Validate DESIVAST as seed corpus focus
- Identify specific arXiv IDs for initial harvesting
- Confirm paper selection covers all three downstream projects
- Document seed corpus specification

### Future (Phase 03+)
- Phase 03: Foundation — Walking skeleton (single paper → retrieval)
- Phase 04: Harvester — Bulk ADS/arXiv acquisition
- Phase 05: Hybrid Engine — Neo4j graph construction
- Phase 06: Agent — LangGraph state machine
- Phase 07: Interface — MCP servers

## Active Decisions

### Pending Decisions
- **Seed corpus size:** How many papers for initial walking skeleton? (Likely 1 for Phase 03, expand in Phase 04)
- **Embedding model selection:** Which sentence-transformer model for astronomy domain?

### Recent Decisions

- **2025-12-29 — Dedicated database:** Corpus gets its own `astronomy_rag_corpus` database on pgsql01 (not sharing with existing DESI data)
- **2025-12-29 — DESIVAST seed focus:** Start with void catalog methodology papers as they're central to all downstream projects
- **2025-12-29 — Walking skeleton scope:** Phase 03 proves the minimal loop (arXiv → LaTeX → Postgres → retrieval) before adding complexity

## Blockers and Dependencies

### Current Blockers
- None

### External Dependencies
- **Database creation:** Need to create `astronomy_rag_corpus` database on pgsql01 (Phase 03 prerequisite)
- **NASA ADS token:** Need valid API token for bibliographic queries (store in research.env)

## Notes and Observations

### Recent Insights
- GDR documents from several months ago remain architecturally sound; no major revisions needed
- Infrastructure already exists — this project slots into existing Proxmox cluster stack
- Documentation standards from desi-cosmic-void-galaxies transfer cleanly with domain/phase tag updates

### Context for Next Session
- Repository ready for initial commit after placeholder cleanup
- Phase 02 focuses on research alignment, not implementation
- Actual coding begins in Phase 03 (Foundation)
