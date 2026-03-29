-- =============================================================================
-- Schema: astronomy_rag_corpus
-- Description: Semantic layer for the Astronomy RAG Corpus
-- Created: 2026-03-14
-- Repository: astronomy-rag-corpus
--
-- Run against the astronomy_rag_corpus database after creation:
--   psql -h 10.25.20.8 -U clusteradmin_pg01 -d astronomy_rag_corpus -f schema.sql
--
-- Prerequisites:
--   CREATE DATABASE astronomy_rag_corpus;
-- =============================================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS vector;

-- -----------------------------------------------------------------------------
-- papers — one row per extracted paper
-- -----------------------------------------------------------------------------
CREATE TABLE papers (
    id              SERIAL PRIMARY KEY,
    arxiv_id        VARCHAR(20) UNIQUE NOT NULL,
    bibcode         VARCHAR(19) UNIQUE,          -- NULL until Phase 06 (ADS integration)
    title           TEXT NOT NULL,
    abstract        TEXT,
    authors         JSONB NOT NULL DEFAULT '[]',  -- Structured: [{name, orcid, affiliations, email}]
    sections        JSONB NOT NULL DEFAULT '[]',  -- Full extraction output for re-chunking
    paper_references JSONB NOT NULL DEFAULT '{}', -- {cite_key: {authors, title, year, journal, raw}}
    extraction_method VARCHAR(20) NOT NULL,       -- "latex" or "pdf_fallback"
    source_file     TEXT,
    extracted_at    TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- chunks — text chunks derived from papers, with embeddings
-- -----------------------------------------------------------------------------
CREATE TABLE chunks (
    id                SERIAL PRIMARY KEY,
    paper_id          INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    chunk_index       INTEGER NOT NULL,            -- Order within paper
    content           TEXT NOT NULL,                -- The chunk text
    context_preamble  TEXT,                         -- Contextual enrichment prefix
    section_path      TEXT,                         -- e.g., "Methods > Void-Finding Algorithm"
    section_level     INTEGER,                      -- 1=section, 2=subsection, 3=subsubsection
    embedding         vector(768),                  -- nomic-embed-text (768d)
    search_vector     tsvector,                     -- BM25 sparse search
    metadata          JSONB DEFAULT '{}',           -- token_count, char_count, overlap_tokens, etc.
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(paper_id, chunk_index)
);

-- -----------------------------------------------------------------------------
-- Indexes
-- -----------------------------------------------------------------------------

-- Paper lookups
CREATE INDEX idx_papers_arxiv_id ON papers (arxiv_id);
CREATE INDEX idx_papers_bibcode ON papers (bibcode) WHERE bibcode IS NOT NULL;

-- Chunk retrieval
CREATE INDEX idx_chunks_paper_id ON chunks (paper_id);

-- Vector similarity search (HNSW — cosine distance for normalized embeddings)
CREATE INDEX idx_chunks_embedding ON chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Full-text sparse search
CREATE INDEX idx_chunks_search_vector ON chunks USING gin (search_vector);

-- -----------------------------------------------------------------------------
-- Trigger: auto-update papers.updated_at on modification
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER papers_updated_at
    BEFORE UPDATE ON papers
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- -----------------------------------------------------------------------------
-- Trigger: auto-populate chunks.search_vector on insert/update
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector = to_tsvector('english', COALESCE(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER chunks_search_vector_update
    BEFORE INSERT OR UPDATE OF content ON chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();
