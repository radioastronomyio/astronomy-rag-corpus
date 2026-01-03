# Astronomy RAG Corpus Technology Stack

## Technology Stack

### Primary Technologies
- **Python:** 3.11+ — Core implementation language
- **PostgreSQL:** 16 with pgvector — Semantic layer, embeddings, vector search
- **Neo4j:** 5 — Topological layer, citation graphs
- **LangGraph:** Latest — Stateful agent orchestration

### Supporting Technologies
- **arxiv.py:** arXiv API wrapper for paper retrieval
- **ads:** NASA ADS API client for bibliographic data
- **pylatexenc:** LaTeX to Unicode text conversion
- **PyMuPDF:** PDF text extraction (fallback)
- **astropy:** FITS header extraction
- **MCP SDK:** Model Context Protocol server implementation

## Dependencies

### Required Dependencies
```
arxiv>=2.0.0           # arXiv paper retrieval
ads>=0.12.0            # NASA ADS bibliographic data
pylatexenc>=2.10       # LaTeX text extraction
pymupdf>=1.23.0        # PDF fallback extraction
pypdf>=3.0.0           # PDF validation and page count
astropy>=6.0.0         # FITS header handling
psycopg2-binary>=2.9   # PostgreSQL connection
neo4j>=5.0.0           # Neo4j driver
langchain>=0.1.0       # LLM orchestration base
langgraph>=0.0.20      # Stateful agent workflows
sentence-transformers  # Embedding generation
python-dotenv>=1.0.0   # Environment configuration
filelock>=3.0.0        # Thread-safe file operations
```

### Optional Dependencies
```
mcp>=0.1.0             # MCP server SDK (Phase 07)
httpx>=0.25.0          # Async HTTP client
```

## Development Environment

### Prerequisites
- Python 3.11+
- Access to research cluster (`/opt/global-env/research.env`)
- Network access to radio-pgsql01, radio-neo4j01, radio-fs02

### Setup Instructions

```bash
# Clone repository
git clone https://github.com/Proxmox-Astronomy-Lab/astronomy-rag-corpus.git
cd astronomy-rag-corpus

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux
# or: .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Load environment (on cluster VMs)
set -a && source /opt/global-env/research.env && set +a

# Verify database connectivity
python -c "import psycopg2; print('PostgreSQL OK')"
python -c "from neo4j import GraphDatabase; print('Neo4j OK')"
```

### Environment Variables

From `/opt/global-env/research.env`:

```bash
# PostgreSQL (pgsql01)
PGSQL01_HOST=10.25.20.8
PGSQL01_PORT=5432
PGSQL01_ADMIN_USER=clusteradmin_pg01
PGSQL01_ADMIN_PASSWORD=<from env file>

# Neo4j
NEO4J_HOST=10.25.20.21
NEO4J_PORT=7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<from env file>

# GPU Processing
GPU_HOST=10.25.20.10
OLLAMA_ENDPOINT=http://10.25.20.10:11434
```

**Corpus-specific (to be added):**
```bash
CORPUS_DB=astronomy_rag_corpus
CORPUS_SMB_PATH=/mnt/astro_corpus  # Linux mount point
```

## Infrastructure

### Hosting / Runtime Environment
- **Platform:** Proxmox Astronomy Lab cluster
- **Database VM:** radio-pgsql01 (8 vCPU, 32GB RAM)
- **Graph VM:** radio-neo4j01 (6 vCPU, 24GB RAM)
- **Storage VM:** radio-fs02 (Windows Server 2025, SMB)
- **GPU VM:** radio-gpu01 (A4000, 16GB vRAM)

### External Services
- **NASA ADS:** API access via token (store in env, not repo)
- **arXiv:** Public API, rate-limited (3 second delays)

## Technical Constraints

### Performance Requirements
- Embedding generation batched to fit 16GB vRAM
- Vector search <100ms for top-10 retrieval
- Graph traversal <500ms for 2-hop citation expansion

### Security Constraints
- MCP servers connect with read-only database credentials
- No API keys in repository (use environment variables)
- Human approval gate for agent-generated queries

### Compatibility Requirements
- Linux VMs use `/mnt/astro_corpus/` mount point
- Windows uses `\\radio-fs02\AstroCorpus\` UNC path
- Path resolver middleware handles OS detection

## Development Workflow

### Version Control
- **Repository:** https://github.com/Proxmox-Astronomy-Lab/astronomy-rag-corpus
- **Branching Strategy:** Feature branches off main, PR for merge
- **Commit Conventions:** Conventional commits (`feat:`, `fix:`, `docs:`)

### Testing
- **Test Framework:** pytest
- **Running Tests:** `pytest tests/`

### Build and Deployment

```bash
# No build step (Python)

# Run ingestion (example)
python src/harvester/ingest_paper.py <arxiv_id>

# Run retrieval test
python src/retrieval/search.py "cosmic void quenching"
```

## Automation and Tooling

### Available Scripts
- Scripts will be added as phases complete

### Development Tools
- **Kilo Code:** AI-assisted development
- **Claude Code:** MCP integration target
- **CodeRabbit:** PR review

## Troubleshooting

### Common Issues

#### PostgreSQL Connection Refused
**Problem:** Cannot connect to radio-pgsql01  
**Solution:** Verify VPN/network access, check firewall rules, confirm env variables loaded

#### Neo4j Authentication Failed
**Problem:** Neo4j rejects credentials  
**Solution:** Verify NEO4J_PASSWORD from research.env, check user exists in Neo4j

#### SMB Mount Not Available
**Problem:** `/mnt/astro_corpus/` not accessible  
**Solution:** Mount SMB share: `sudo mount -t cifs //radio-fs02/AstroCorpus /mnt/astro_corpus -o credentials=/etc/smb-credentials`

### Debug Commands

```bash
# Test PostgreSQL
psql -h $PGSQL01_HOST -U $PGSQL01_ADMIN_USER -d postgres -c "SELECT 1"

# Test Neo4j
cypher-shell -a bolt://$NEO4J_HOST:$NEO4J_PORT -u $NEO4J_USER -p $NEO4J_PASSWORD "RETURN 1"

# Test SMB mount
ls /mnt/astro_corpus/
```

## Technical Documentation

- **pgvector:** https://github.com/pgvector/pgvector
- **Neo4j Python Driver:** https://neo4j.com/docs/python-manual/current/
- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **arxiv.py:** https://lukasschwab.me/arxiv.py/
- **NASA ADS API:** https://ui.adsabs.harvard.edu/help/api/
- **MCP:** https://modelcontextprotocol.io/
