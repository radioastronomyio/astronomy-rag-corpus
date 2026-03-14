# Agent Instructions — Astronomy RAG Corpus

A Federated Knowledge Core for astronomical research literature, supporting Retrieval-Augmented Generation for the DESI research portfolio. The system decouples semantic content (PostgreSQL + pgvector), topological relationships (Neo4j), and physical artifacts (SMB storage), unified by NASA ADS Bibcode as the universal identifier.

Primary consumers: [desi-cosmic-void-galaxies](https://github.com/Proxmox-Astronomy-Lab/desi-cosmic-void-galaxies), [desi-qso-anomaly-detection](https://github.com/Proxmox-Astronomy-Lab/desi-qso-anomaly-detection), [desi-quasar-outflows](https://github.com/Proxmox-Astronomy-Lab/desi-quasar-outflows).

Repository: <https://github.com/Proxmox-Astronomy-Lab/astronomy-rag-corpus>

## Spec Directory

Detailed project context lives in `spec/`. Load only what you need for the task at hand.

| File | Contents | Read when... |
|------|----------|--------------|
| [architecture.md](spec/architecture.md) | System design, layer responsibilities, design decisions, data flow | Designing components, making structural decisions, understanding how layers interact |
| [current-state.md](spec/current-state.md) | Where we are, recent work, next steps, blockers | Starting any session — always read this first |
| [phases.md](spec/phases.md) | Milestone plan, task statuses, pending decisions | Planning work, picking up tasks, checking what's ready |
| [tech-stack.md](spec/tech-stack.md) | Dependencies, connection patterns, env setup, external service constraints | Writing code, debugging connectivity, adding dependencies |
| [landscape.md](spec/landscape.md) | RAG/GraphRAG evolution, techniques to consider, prior art | Making design decisions about chunking, retrieval, embedding, or agent architecture |

## Session Pattern

1. Read `spec/current-state.md` to orient
2. Load additional spec files relevant to the task
3. Do work
4. Update `spec/current-state.md` before session ends
5. Update other spec files if relevant changes occurred (architecture shifts, new decisions, dependency changes)

## Key Conventions

- **Commits**: Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- **Branches**: Feature branches off main, PR for merge
- **Code style**: Type hints on all signatures, NumPy-style docstrings, error handling for network/database failures
- **Infrastructure**: Connection details via `/opt/global-env/research.env` — never hardcode credentials. See `docs/data-science-infrastructure.md` for cluster reference.
