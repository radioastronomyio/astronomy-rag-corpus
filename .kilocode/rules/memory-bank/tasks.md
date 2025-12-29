# Astronomy RAG Corpus Tasks and Workflows

## Common Workflows

### Paper Ingestion (Future — Phase 03+)

**When to use:** Adding a new paper to the corpus  
**Frequency:** Batch during harvesting, individual during research

**Steps:**
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

---

### Semantic Search (Future — Phase 03+)

**When to use:** Finding relevant papers for a research question  
**Frequency:** Ad-hoc during research sessions

**Steps:**
1. Embed query text using same model as corpus
2. Execute pgvector similarity search
3. Retrieve top-N chunks with bibcodes
4. Optionally expand via citation graph (graph-boosted retrieval)
5. Return results with source attribution

**Expected Outcome:** Ranked list of relevant text chunks with bibcode citations  
**Common Issues:** Poor relevance (check embedding model, chunk size)

---

## Memory Bank Maintenance

### Updating context.md

**When:** After every significant work session  
**What to update:**
1. Move completed items from "Next Steps" to "Recent Accomplishments"
2. Update "Current Phase" if phase changed
3. Update "Next Steps" with new actionable items
4. Document any new decisions in "Active Decisions"
5. Add/resolve blockers as appropriate
6. Update "Last Updated" date

**Quality check:** Does context.md accurately reflect current state?

---

### Phase Completion Checklist

**When:** Completing a development phase  
**Steps:**
1. Update work-log README for the phase (status → Complete)
2. Update work-logs/README.md phase table
3. Update main README.md phase table
4. Update context.md current phase
5. Create next phase directory if needed
6. Commit with message: `docs: complete phase NN`

---

## Session Management

### Session Start Procedure

**Objective:** Load context and confirm understanding

1. **Load memory bank files**
   - Read brief.md (foundational context)
   - Read context.md (current state and next steps)
   - Scan architecture.md and tech.md as needed

2. **Confirm context**
   - Display: `[Memory Bank: Active | Project: astronomy-rag-corpus]`
   - Summarize: Current phase, immediate next steps

3. **Verify currency**
   - Check "Last Updated" in context.md
   - If stale, flag for review

---

### Session End Procedure

**Objective:** Update memory bank with session outcomes

1. **Update context.md**
   - Add accomplishments
   - Update next steps
   - Document decisions
   - Update timestamp

2. **Update other files if needed**
   - architecture.md if design changed
   - tech.md if dependencies changed

3. **Commit changes**
   ```bash
   git add .kilocode/rules/memory-bank/
   git commit -m "chore: update memory bank"
   ```

---

## Quality Checklists

### Code Quality Checklist
- [ ] Follows script header template from documentation-standards
- [ ] Type hints on all function signatures
- [ ] NumPy-style docstrings
- [ ] Error handling for network/database failures
- [ ] Rate limiting for external API calls

### Documentation Quality Checklist
- [ ] YAML frontmatter with appropriate tags
- [ ] Semantic section numbering preserved
- [ ] Links to related documents
- [ ] Updated date in frontmatter

### Ingestion Quality Checklist
- [ ] Bibcode present and valid
- [ ] Text extracted without corruption (spot-check math notation)
- [ ] Citations extracted and inserted into Neo4j
- [ ] Artifact saved with canonical path
- [ ] Embedding generated and stored
