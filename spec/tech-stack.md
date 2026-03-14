# Tech Stack

## Python Dependencies

```
# Core (currently used)
arxiv>=2.0.0           # arXiv paper retrieval
pypdf>=3.0.0           # PDF validation and page count
python-dotenv>=1.0.0   # Environment configuration
filelock>=3.0.0        # Thread-safe file operations

# Extraction (Phase 04)
pylatexenc>=2.10       # LaTeX text extraction
pymupdf>=1.23.0        # PDF fallback extraction

# Storage & Retrieval (Phase 05+)
psycopg2-binary>=2.9   # PostgreSQL connection
neo4j>=5.0.0           # Neo4j driver
sentence-transformers  # Embedding generation

# Agent (Phase 08+)
langchain>=0.1.0       # LLM orchestration base
langgraph>=0.0.20      # Stateful agent workflows

# Future
ads>=0.12.0            # NASA ADS bibliographic data (Phase 06)
astropy>=6.0.0         # FITS header handling (future)
mcp>=0.1.0             # MCP server SDK (Phase 09)
```

## Connection Patterns

All credentials load from `/opt/global-env/research.env`. Never hardcode connection details.

```bash
# Load in shell
set -a && source /opt/global-env/research.env && set +a

# Load in Python
from dotenv import load_dotenv
load_dotenv('/opt/global-env/research.env')
```

### PostgreSQL (Semantic Layer)

- **Host:** radio-pgsql01 (`$PGSQL01_HOST` = 10.25.20.8)
- **Port:** 5432
- **Admin user:** `$PGSQL01_ADMIN_USER`
- **Corpus database:** `astronomy_rag_corpus` (not yet created — Phase 05)

### Neo4j (Topological Layer)

- **Host:** radio-neo4j01 (`$NEO4J_HOST` = 10.25.20.21)
- **Bolt port:** 7687
- **User:** `$NEO4J_USER`

### SMB Storage (Physical Layer)

- **Host:** radio-fs02 (10.25.20.15)
- **Linux mount:** `/mnt/astro_corpus/`
- **Windows UNC:** `\\radio-fs02\AstroCorpus\`
- **Mount command:** `sudo mount -t cifs //radio-fs02/AstroCorpus /mnt/astro_corpus -o credentials=/etc/smb-credentials`

### GPU Processing

- **Host:** radio-gpu01 (`$GPU_HOST` = 10.25.20.10)
- **Working path:** `/mnt/ai-ml/data/rag-corpus`
- **Ollama:** `http://10.25.20.10:11434`
- **Constraint:** Batch embedding jobs to fit GPU memory

### Path Resolution

Artifacts use OS-agnostic canonical paths (`YYYY/MM/Bibcode.pdf`), resolved at runtime:

```python
import os, platform
if platform.system() == 'Windows':
    base = r'\\radio-fs02\AstroCorpus'
else:
    base = '/mnt/astro_corpus'
artifact_path = os.path.join(base, canonical_path)
```

## External Services

### arXiv API

- Rate limited: 3-second delay between requests (enforced in `arxiv_client.py`)
- No authentication required
- Source tarballs not always available — PDF fallback needed

### NASA ADS API

- Requires API token (store in env, not repo)
- Token not yet provisioned — needed for Phase 06+
- Provides: bibliographic metadata, citation lists, abstracts

## Dev Environment Setup

```bash
git clone https://github.com/Proxmox-Astronomy-Lab/astronomy-rag-corpus.git
cd astronomy-rag-corpus

python -m venv venv
source venv/bin/activate        # Linux
# or: .\venv\Scripts\activate   # Windows

pip install -r requirements.txt

# On cluster VMs, load environment
set -a && source /opt/global-env/research.env && set +a
```

## Infrastructure Reference

For full cluster inventory (VM specs, network layout, storage allocation), see `docs/data-science-infrastructure.md`. That document is the reference — don't duplicate hardware details elsewhere.

## Troubleshooting

**PostgreSQL connection refused:** Check VPN/network access, verify firewall rules, confirm env variables loaded with `echo $PGSQL01_HOST`.

**Neo4j auth failed:** Verify password from `research.env`, confirm user exists in Neo4j.

**SMB mount unavailable:** Run mount command above. Check credentials file exists at `/etc/smb-credentials`.

**arXiv rate limiting:** The client enforces 3s delays. If you get 429s, increase the delay or wait.
