# Memory Bank

Persistent context files for AI agent sessions. Loaded at session start to establish project understanding.

## Files

| File | Purpose | Update Frequency |
|------|---------|------------------|
| [brief.md](brief.md) | Foundational 2-3 paragraph context | Rarely |
| [product.md](product.md) | Problems solved, goals, outcomes | Occasionally |
| [architecture.md](architecture.md) | System design, patterns, decisions | When design changes |
| [tech.md](tech.md) | Stack, setup, constraints | When stack changes |
| [context.md](context.md) | Current state, next steps | Every session |
| [tasks.md](tasks.md) | Repetitive workflows | As patterns emerge |

## Usage

**Session start:** Agent loads these files to understand project state.

**Session end:** Update context.md with accomplishments and next steps.

## Reference

- [Kilo Code Memory Bank Docs](https://kilocode.ai/docs/advanced-usage/memory-bank)
