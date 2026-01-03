# Astronomy RAG Corpus Tasks

> **Source of Truth:** [GitHub Project Board](https://github.com/CrainBramp/astronomy-rag-corpus/projects)
> **Last Synced:** 2025-01-03

## Project Structure

Three milestones covering the core pipeline: Acquisition → Extraction → Storage.

### Milestone 1: Acquisition

Paper discovery and artifact retrieval from arXiv/ADS.

| Task | Issue | Status |
|------|-------|--------|
| 1.1 Select Seed Paper | #1 | ✅ Done |
| 1.2 Define Storage Paths | #2 | ✅ Done |
| 1.3 Implement arXiv Client | #3 | 🔄 In Progress |
| 1.4 Download Artifacts | #4 | ⏳ Ready |
| 1.5 Extract and Organize Source | #5 | 📋 Backlog |

### Milestone 2: Extraction

LaTeX parsing, text cleaning, and structure preservation.

| Task | Issue | Status |
|------|-------|--------|
| 2.1 Evaluate Extraction Tools | #6 | 📋 Backlog |
| 2.2 Implement LaTeX Parser | #7 | 📋 Backlog |
| 2.3 Preserve Document Structure | #8 | 📋 Backlog |
| 2.4 Handle Math Notation | #9 | 📋 Backlog |
| 2.5 Implement PDF Fallback | #10 | 📋 Backlog |
| 2.6 Validate Output Quality | #11 | 📋 Backlog |

### Milestone 3: Storage

Database provisioning, embedding pipeline, and retrieval.

| Task | Issue | Status |
|------|-------|--------|
| 3.1 Provision Database | #12 | 📋 Backlog |
| 3.2 Design Schema | #13 | 📋 Backlog |
| 3.3 Evaluate Embedding Models | #14 | 📋 Backlog |
| 3.4 Implement Chunking | #15 | 📋 Backlog |
| 3.5 Generate and Store Embeddings | #16 | 📋 Backlog |
| 3.6 Build Retrieval Function | #17 | 📋 Backlog |
| 3.7 Validate End-to-End | #18 | 📋 Backlog |

---

## Status Legend

| Icon | Status | Meaning |
|------|--------|---------|
| ✅ | Done | Completed and closed |
| 🔄 | In Progress | Actively being worked |
| ⏳ | Ready | Dependencies met, ready to start |
| 📋 | Backlog | Not yet started |

---

## Workflows

### Paper Ingestion (Milestone 1-3 Combined)

**When to use:** Adding a new paper to the corpus
**Frequency:** Batch during harvesting, individual during research

1. Obtain arXiv ID or bibcode
2. Query ADS for bibliographic metadata
3. Download LaTeX source from arXiv (fall back to PDF if unavailable)
4. Extract clean text using pylatexenc (or PyMuPDF fallback)
5. Generate embeddings for text chunks
6. Insert into PostgreSQL (text, embeddings, metadata)
7. Extract citations from ADS, insert relationships into Neo4j
8. Copy artifact (PDF) to SMB with canonical path

**Expected Outcome:** Paper searchable via semantic query, citations traversable in graph
**Common Issues:** LaTeX source unavailable (use PDF fallback), rate limiting (add delays)

### Semantic Search (Post-Milestone 3)

**When to use:** Finding relevant papers for a research question
**Frequency:** Ad-hoc during research sessions

1. Embed query text using same model as corpus
2. Execute pgvector similarity search
3. Retrieve top-N chunks with bibcodes
4. Optionally expand via citation graph (graph-boosted retrieval)
5. Return results with source attribution

**Expected Outcome:** Ranked list of relevant text chunks with bibcode citations
**Common Issues:** Poor relevance (check embedding model, chunk size)

---

## Memory Bank Maintenance

### Updating tasks.md

**When:** After planning changes or task status changes
**Principle:** Planning isn't complete until tasks.md reflects the plan

1. Update task statuses to match GitHub project board
2. Update "Last Synced" date
3. Add/remove tasks if milestone structure changes
4. Commit with message: `chore: sync tasks.md with GitHub`

### Updating context.md

**When:** After every significant work session

1. Move completed items from "Next Steps" to "Recent Accomplishments"
2. Update "Current Phase" if phase changed
3. Update "Next Steps" with new actionable items
4. Document any new decisions in "Active Decisions"
5. Add/resolve blockers as appropriate
6. Update "Last Updated" date

**Quality check:** Does context.md accurately reflect current state?

---

## Quality Checklists

### Code Quality
- [ ] Follows script header template from documentation-standards
- [ ] Type hints on all function signatures
- [ ] NumPy-style docstrings
- [ ] Error handling for network/database failures
- [ ] Rate limiting for external API calls

### Documentation Quality
- [ ] YAML frontmatter with appropriate tags
- [ ] Semantic section numbering preserved
- [ ] Links to related documents
- [ ] Updated date in frontmatter

### Ingestion Quality
- [ ] Bibcode present and valid
- [ ] Text extracted without corruption (spot-check math notation)
- [ ] Citations extracted and inserted into Neo4j
- [ ] Artifact saved with canonical path
- [ ] Embedding generated and stored
