# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-21)

**Core value:** YAML DSL simple enough for reliable LLM generation + Python compiler producing ADA-compliant HTML matching current /ada-slides-general quality
**Current focus:** Phase 1 — DSL Schema

## Current Position

Phase: 1 of 4 (DSL Schema)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-03-21 — Roadmap created

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: —
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: —
- Trend: —

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Hybrid YAML+Markdown DSL (YAML frontmatter + Markdown body) chosen to reduce LLM drift
- Python + Jinja2 for deterministic compilation — no LLM in compiler step
- KaTeX CDN preferred over MathJax (already used in existing decks)
- Mermaid strategy: mmdc Python-native package (MEDIUM confidence — prototype in Phase 3 before committing)

### Pending Todos

None yet.

### Blockers/Concerns

- mmdc Python package (Mermaid renderer) is new (Jan 2026) — verify stability before Phase 3 commits to it; client-side script fallback available
- Exact layout primitive list (~15) requires analysis of existing HTML decks in n8n_to_python/output_html_files/ — must happen in Phase 1

## Session Continuity

Last session: 2026-03-21
Stopped at: Roadmap created, ready to plan Phase 1
Resume file: None
