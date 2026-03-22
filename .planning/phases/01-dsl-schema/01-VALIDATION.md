---
phase: 1
slug: dsl-schema
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | pyproject.toml |
| **Quick run command** | `uv run pytest tests/ -x -q` |
| **Full suite command** | `uv run pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -x -q`
- **After every plan wave:** Run `uv run pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | DSL-01 | unit | `uv run pytest tests/test_models.py -x -q` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | DSL-02 | unit | `uv run pytest tests/test_models.py -x -q` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | DSL-03 | unit | `uv run pytest tests/test_validation.py -x -q` | ❌ W0 | ⬜ pending |
| 01-01-04 | 01 | 1 | DSL-04 | unit | `uv run pytest tests/test_schema_gen.py -x -q` | ❌ W0 | ⬜ pending |
| 01-01-05 | 01 | 1 | DSL-05 | unit | `uv run pytest tests/test_models.py -x -q` | ❌ W0 | ⬜ pending |
| 01-01-06 | 01 | 1 | DSL-06 | unit | `uv run pytest tests/test_fixtures.py -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_models.py` — stubs for DSL-01, DSL-02, DSL-05
- [ ] `tests/test_validation.py` — stubs for DSL-03
- [ ] `tests/test_schema_gen.py` — stubs for DSL-04
- [ ] `tests/test_fixtures.py` — stubs for DSL-06
- [ ] `tests/conftest.py` — shared fixtures
- [ ] pytest + pydantic install via `uv add --dev pytest`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Error messages are "clear and actionable" | DSL-03 | Subjective quality | Review error output for missing `alt_text` — should name field, model, and location |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
