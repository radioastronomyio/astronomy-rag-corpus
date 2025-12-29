<!--
---
title: "Documentation Standards"
description: "Templates and guidelines for project documentation"
author: "VintageDon"
date: "2025-12-29"
version: "1.0"
status: "Active"
tags:
  - type: directory-readme
  - domain: documentation
---
-->

# Documentation Standards

Templates for RAG-optimized documentation. Start lean, expand as needed.

---

## 1. Contents

```
documentation-standards/
├── interior-readme-template.md     # For any directory README
├── general-kb-template.md          # For standalone documents
├── worklog-readme-template.md      # For milestone/work-log directories
├── tagging-strategy.md             # Controlled vocabulary for tags
├── script-header-python.md         # Python script header template
├── script-header-shell.md          # Bash script header template
├── script-header-powershell.md     # PowerShell script header template
└── README.md                       # This file
```

---

## 2. Templates

### Document Templates

| Template | Use For |
|----------|---------|
| [interior-readme-template.md](interior-readme-template.md) | Any directory that needs a README |
| [general-kb-template.md](general-kb-template.md) | Standalone documents (guides, specs, reports) |
| [worklog-readme-template.md](worklog-readme-template.md) | Milestone directories in `work-logs/` |

### Script Header Templates

| Template | Use For |
|----------|---------|
| [script-header-python.md](script-header-python.md) | All `.py` files |
| [script-header-shell.md](script-header-shell.md) | All `.sh` files |
| [script-header-powershell.md](script-header-powershell.md) | All `.ps1` files |

### Classification

| Document | Use For |
|----------|---------|
| [tagging-strategy.md](tagging-strategy.md) | Controlled vocabulary for YAML frontmatter tags |

---

## 3. Core Principles

### RAG Infrastructure (Always Keep)

- YAML frontmatter — enables retrieval and filtering
- Semantic numbering — predictable section structure
- Preserved gaps — if you omit section 4, keep numbering as 1, 2, 3, 5 (never renumber)

### Bottom-Up Approach

- Start with minimal template
- Add sections as content requires
- Don't fill sections for completeness
- Wrapper is thin; content is the point

---

## 4. Template Selection

### Documents

```
Is it a directory README?
├─ Yes: Is it a work-logs milestone?
│       ├─ Yes → worklog-readme-template.md
│       └─ No  → interior-readme-template.md
└─ No: Is it a standalone document?
        └─ Yes → general-kb-template.md
```

### Scripts

```
What language?
├─ Python (.py)     → script-header-python.md
├─ Bash (.sh)       → script-header-shell.md
└─ PowerShell (.ps1)→ script-header-powershell.md
```

---

## 5. Related

| Document | Relationship |
|----------|--------------|
| [docs/](../README.md) | Parent directory |
