# PowerShell Script Header Template

> Template Version: 1.0  
> Applies To: All `.ps1` files in astronomy-rag-corpus  
> Last Updated: 2025-12-29

---

## Template

```powershell
<#
.SYNOPSIS
    [One-line description of what the script does]

.DESCRIPTION
    [2-4 sentences explaining the script's purpose, what it operates on,
    and what outputs it produces. Include any important behavioral notes.]

.NOTES
    Repository  : astronomy-rag-corpus
    Author      : VintageDon (https://github.com/vintagedon)
    ORCID       : 0009-0008-7695-4093
    Created     : YYYY-MM-DD
    Phase       : [Phase NN - Phase Name]

.EXAMPLE
    .\script-name.ps1

    [Description of what this invocation does]

.EXAMPLE
    .\script-name.ps1 -Parameter Value

    [Description of what this invocation does]

.LINK
    https://github.com/radioastronomyio/astronomy-rag-corpus
#>

# =============================================================================
# Configuration
# =============================================================================

# [Configuration variables with inline comments]

# =============================================================================
# Functions
# =============================================================================

# [Function definitions if needed]

# =============================================================================
# Execution
# =============================================================================

# [Main script logic]
```

---

## Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `.SYNOPSIS` | Yes | Single line, verb-led description |
| `.DESCRIPTION` | Yes | Expanded explanation of purpose and behavior |
| `.NOTES` | Yes | Static metadata (repository, author, ORCID, dates, phase) |
| `.EXAMPLE` | Yes | At least one usage example with description |
| `.LINK` | Yes | Repository URL |
| `.PARAMETER` | If applicable | Document any script parameters |

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

```powershell
# =============================================================================
# Section Name
# =============================================================================
```

Standard sections (in order):

1. **Configuration** — Variables, paths, settings
2. **Functions** — Helper function definitions (if any)
3. **Execution** — Main script logic

---

## Example: Minimal Script

```powershell
<#
.SYNOPSIS
    Validates corpus database connectivity.

.DESCRIPTION
    Tests connections to PostgreSQL (pgvector) and Neo4j databases used by the
    corpus system. Reports connection status and basic health metrics for each
    database.

.NOTES
    Repository  : astronomy-rag-corpus
    Author      : VintageDon (https://github.com/vintagedon)
    ORCID       : 0009-0008-7695-4093
    Created     : 2025-12-29
    Phase       : Phase 01 - Foundation

.EXAMPLE
    .\test-corpus-connections.ps1

    Tests all corpus database connections and reports status.

.LINK
    https://github.com/radioastronomyio/astronomy-rag-corpus
#>

# =============================================================================
# Configuration
# =============================================================================

$pgHost = "10.25.20.8"
$neo4jHost = "10.25.20.21"

# =============================================================================
# Execution
# =============================================================================

Write-Host "Testing PostgreSQL connection to $pgHost..."
# Connection test logic here

Write-Host "Testing Neo4j connection to $neo4jHost..."
# Connection test logic here
```

---

## Notes

- PowerShell comment-based help (`.SYNOPSIS`, `.DESCRIPTION`, etc.) enables `Get-Help script-name.ps1`
- Keep `.SYNOPSIS` under 80 characters
- Use present tense, active voice ("Validates..." not "This script validates...")
- Phase field should match work-log phase names exactly
