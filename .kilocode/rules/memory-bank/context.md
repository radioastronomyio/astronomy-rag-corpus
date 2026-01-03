# Astronomy RAG Corpus Context

## Current State
**Last Updated:** 2026-01-03

### Recent Accomplishments
- Refined milestone structure based on GDR section boundaries
- Defined three implementation milestones: Acquisition, Extraction, Storage
- Broke down milestones into 18 discrete tasks
- Established GitHub label taxonomy (milestone, component, stage)
- Documented Phase 02 worklog

### Current Phase

We are currently in **Phase 02: GitHub Frameout** which is now complete. The project management structure is defined and ready for implementation.

### Active Work

Phase 02 complete. Ready to transition to Phase 03: Acquisition.

## Next Steps

### Immediate (Next Session)
1. Create GitHub labels as defined in Phase 02 worklog
2. Create GitHub issues for Milestone 1 (Acquisition) tasks
3. Select seed paper (DESIVAST VAC — arXiv:2411.00148)
4. Begin Task 1.1: Confirm arXiv ID and LaTeX source availability

### Near-Term (Phase 03: Acquisition)
- Implement `arxiv.py` retrieval client
- Define canonical SMB storage paths
- Download PDF + LaTeX source for seed paper
- Extract and organize LaTeX archive

### Future (Phases 04-09)
- Phase 04: Extraction — LaTeX/PDF text extraction
- Phase 05: Storage — Database, embeddings, retrieval
- Phase 06: Harvester — Bulk acquisition
- Phase 07: Hybrid Engine — Neo4j graph construction
- Phase 08: Agent — LangGraph state machine
- Phase 09: Interface — MCP servers

## Active Decisions

### Pending Decisions
- **Embedding model selection:** Which sentence-transformer model for astronomy domain? (Phase 05)
- **Chunking strategy:** Section-boundary vs fixed-size chunks (Phase 05)

### Recent Decisions

- **2026-01-03 — GDR-aligned milestones:** Structure milestones around GDR section boundaries for tighter, testable units
- **2026-01-03 — Merge Plan Review:** Combined seed paper selection into Acquisition milestone
- **2026-01-03 — Defer retrieval:** Include retrieval function in Storage milestone as validation step
- **2025-12-29 — Dedicated database:** Corpus gets its own `astronomy_rag_corpus` database on pgsql01
- **2025-12-29 — DESIVAST seed focus:** Start with void catalog methodology papers

## Blockers and Dependencies

### Current Blockers
- None

### External Dependencies
- **SMB access:** Need mount point configured for artifact storage (Phase 03)
- **Database creation:** Need to create `astronomy_rag_corpus` database on pgsql01 (Phase 05)
- **NASA ADS token:** Need valid API token for bibliographic queries (Phase 06+)

## Notes and Observations

### Recent Insights
- GDR Section 1.1 (arXiv retrieval) is self-contained and makes a clean first milestone
- Splitting the walking skeleton into Acquisition → Extraction → Storage reduces risk
- Each milestone can be validated independently before integration

### Context for Next Session
- GitHub labels and issues to be created
- Seed paper is DESIVAST VAC (arXiv:2411.00148)
- First coding task: implement arXiv client using `arxiv.py`
