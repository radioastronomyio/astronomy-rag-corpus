<!--
---
title: "Work Logs"
description: "Milestone-based development history for the astronomy RAG corpus"
author: "VintageDon"
date: "2026-01-03"
version: "1.1"
status: "Active"
tags:
  - type: directory-readme
  - domain: documentation
---
-->

# Work Logs

Milestone-based development history. Each phase directory contains scripts, outputs, and documentation for a discrete unit of work.

---

## 1. Contents

```
work-logs/
├── 01-ideation-and-setup/           # Project initialization and architecture
│   └── README.md
├── 02-github-project-frameout/      # Milestones, tasks, and labels
│   └── README.md
├── 03-arxiv-client-implementation/  # Milestone 1: Acquisition
│   └── README.md
└── README.md                        # This file
```

---

## 2. Phase Overview

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| 01 | [Ideation and Setup](01-ideation-and-setup/README.md) | ✅ Complete | GDR review, repo initialization, documentation standards |
| 02 | [GitHub Frameout](02-github-project-frameout/README.md) | ✅ Complete | Milestones, tasks, GitHub labels |
| 03 | [Acquisition](03-arxiv-client-implementation/README.md) | ✅ Complete | arXiv client, PDF download, source extraction |
| 04 | Extraction | ⬜ Next | LaTeX/PDF text extraction |
| 05 | Storage | ⬜ Planned | Database, embeddings, retrieval |
| 06 | Harvester | ⬜ Planned | Bulk acquisition, seed corpus population |
| 07 | Hybrid Engine | ⬜ Planned | Neo4j graph construction |
| 08 | Agent | ⬜ Planned | LangGraph state machine |
| 09 | Interface | ⬜ Planned | MCP servers, Claude Code integration |

---

## 3. Conventions

Directory naming: `NN-phase-name/` (zero-padded, kebab-case)

Script naming: `NN-descriptive-name.py` — outputs share the prefix (`01-script.py` → `01-output.log`)

Figure naming: `NN-description.png` in `figures/` subdirectory

---

## 4. Related

| Document | Relationship |
|----------|--------------|
| [Repository Root](../README.md) | Parent directory |
| [Documentation](../docs/README.md) | Standards and references |
