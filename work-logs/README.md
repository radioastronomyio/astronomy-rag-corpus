<!--
---
title: "Work Logs"
description: "Milestone-based development history for the astronomy RAG corpus"
author: "VintageDon"
date: "2025-12-29"
version: "1.0"
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
├── 01-ideation-and-setup/      # Project initialization and architecture
│   └── README.md
└── README.md                   # This file
```

---

## 2. Phase Overview

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| 01 | [Ideation and Setup](01-ideation-and-setup/README.md) | ✅ Complete | GDR review, repo initialization, documentation standards |
| 02 | Plan Review | ⬜ Next | Validate seed corpus against 2026 research priorities |
| 03 | Foundation | ⬜ Planned | Walking skeleton: single paper ingestion → retrieval |
| 04 | Harvester | ⬜ Planned | ADS/arXiv acquisition, seed corpus population |
| 05 | Hybrid Engine | ⬜ Planned | Neo4j graph construction, hybrid retrieval |
| 06 | Agent | ⬜ Planned | LangGraph state machine, multi-step research |
| 07 | Interface | ⬜ Planned | MCP servers, Claude Code integration |

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
