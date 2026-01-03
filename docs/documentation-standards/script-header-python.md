# Python Script Header Template

> Template Version: 1.0  
> Applies To: All `.py` files in astronomy-rag-corpus  
> Last Updated: 2025-12-29

---

## Template

```python
#!/usr/bin/env python3
"""
Script Name  : script_name.py
Description  : [One-line description of what the script does]
Repository   : astronomy-rag-corpus
Author       : VintageDon (https://github.com/vintagedon)
ORCID        : 0009-0008-7695-4093
Created      : YYYY-MM-DD
Phase        : [Phase NN - Phase Name]
Link         : https://github.com/radioastronomyio/astronomy-rag-corpus

Description
-----------
[2-4 sentences explaining the script's purpose, what it operates on,
and what outputs it produces. Include any important behavioral notes.]

Usage
-----
    python script_name.py [options]

Examples
--------
    python script_name.py
        [Description of what this invocation does]

    python script_name.py --verbose
        [Description of what this invocation does]
"""

# =============================================================================
# Imports
# =============================================================================

from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

# [Configuration constants with inline comments]

# =============================================================================
# Functions
# =============================================================================


def main() -> None:
    """Entry point for script execution."""
    pass


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    main()
```

---

## Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| Script Name | Yes | Filename for reference (snake_case) |
| Description | Yes | Single line, verb-led description |
| Repository | Yes | Repository name |
| Author | Yes | Name with GitHub profile link |
| ORCID | Yes | Author ORCID identifier |
| Created | Yes | Creation date (YYYY-MM-DD) |
| Phase | Yes | Pipeline phase this script belongs to |
| Link | Yes | Full repository URL |
| Description section | Yes | Expanded multi-line explanation |
| Usage section | Yes | Command syntax |
| Examples section | Yes | At least one usage example |

---

## Phase Reference

| Phase | Name |
|-------|------|
| Phase 01 | Foundation |
| Phase 02 | Harvester |
| Phase 03 | Hybrid Engine |
| Phase 04 | Agent |
| Phase 05 | Interface |

---

## Section Comments

Use banner comments to separate logical sections:

```python
# =============================================================================
# Section Name
# =============================================================================
```

Standard sections (in order):

1. **Imports** — Standard library, third-party, local imports (in that order)
2. **Configuration** — Constants, paths, settings
3. **Functions** — Function and class definitions
4. **Entry Point** — `if __name__ == "__main__":` block

---

## Docstring Style

Use NumPy-style docstrings for functions:

```python
def search_corpus(
    query: str,
    max_results: int = 10
) -> list[dict]:
    """
    Search the astronomy corpus for relevant documents.

    Parameters
    ----------
    query : str
        Natural language search query.
    max_results : int, optional
        Maximum number of results to return. Default is 10.

    Returns
    -------
    list[dict]
        Matching documents with keys:
        bibcode, title, abstract, relevance_score, file_path.

    Raises
    ------
    ConnectionError
        If PostgreSQL connection fails.

    Examples
    --------
    >>> results = search_corpus("cosmic void galaxy quenching")
    >>> len(results)
    10
    """
    pass
```

---

## Example: Minimal Script

```python
#!/usr/bin/env python3
"""
Script Name  : ingest_arxiv_paper.py
Description  : Ingests a single arXiv paper into the corpus
Repository   : astronomy-rag-corpus
Author       : VintageDon (https://github.com/vintagedon)
ORCID        : 0009-0008-7695-4093
Created      : 2025-12-29
Phase        : Phase 01 - Foundation
Link         : https://github.com/radioastronomyio/astronomy-rag-corpus

Description
-----------
Downloads an arXiv paper by ID, extracts text from LaTeX source if available,
stores the clean text and bibcode in PostgreSQL, and saves the PDF artifact
to the SMB share.

Usage
-----
    python ingest_arxiv_paper.py <arxiv_id>

Examples
--------
    python ingest_arxiv_paper.py 2401.12345
        Ingests the paper with arXiv ID 2401.12345.
"""

# =============================================================================
# Imports
# =============================================================================

import sys
from pathlib import Path

import arxiv
import psycopg2

# =============================================================================
# Configuration
# =============================================================================

CORPUS_DB = "astronomy_rag_corpus"
SMB_ARTIFACT_PATH = Path("/mnt/astro_corpus/artifacts")

# =============================================================================
# Functions
# =============================================================================


def download_paper(arxiv_id: str) -> tuple[Path, Path]:
    """
    Download PDF and source archive for an arXiv paper.

    Parameters
    ----------
    arxiv_id : str
        arXiv identifier (e.g., "2401.12345").

    Returns
    -------
    tuple[Path, Path]
        Paths to downloaded PDF and source archive.
    """
    pass


def main() -> None:
    """Entry point for script execution."""
    if len(sys.argv) < 2:
        print("Usage: python ingest_arxiv_paper.py <arxiv_id>")
        sys.exit(1)
    
    arxiv_id = sys.argv[1]
    print(f"Ingesting arXiv paper: {arxiv_id}")


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    main()
```

---

## Type Hints

Always use type hints for function signatures:

```python
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


def extract_latex_text(
    source_path: Path,
    output_dir: Optional[Path] = None,
) -> str | None:
    """Extract clean text from LaTeX source archive."""
    pass
```

---

## Notes

- Use `#!/usr/bin/env python3` for portability
- Module docstring goes immediately after shebang
- Keep Description line under 80 characters
- Use present tense, active voice ("Ingests..." not "This script ingests...")
- Use `pathlib.Path` instead of string paths
- Use type hints for all function parameters and return values
- Follow PEP 8 style guide
