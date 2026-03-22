---
phase: 3
slug: rich-content
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | pyproject.toml |
| **Quick run command** | `pytest tests/ -x -q --tb=short` |
| **Full suite command** | `pytest tests/ -v --tb=long` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q --tb=short`
- **After every plan wave:** Run `pytest tests/ -v --tb=long`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | RICH-01 | unit | `pytest tests/test_math_renderer.py -v` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | RICH-02 | unit | `pytest tests/test_code_renderer.py -v` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | RICH-03 | unit | `pytest tests/test_image_renderer.py -v` | ❌ W0 | ⬜ pending |
| 03-01-04 | 01 | 1 | RICH-04 | unit | `pytest tests/test_mermaid_renderer.py -v` | ❌ W0 | ⬜ pending |
| 03-01-05 | 01 | 1 | RICH-05 | unit | `pytest tests/test_table_renderer.py -v` | ❌ W0 | ⬜ pending |
| 03-01-06 | 01 | 1 | RICH-06 | unit | `pytest tests/test_markdown_renderer.py -v` | ❌ W0 | ⬜ pending |
| 03-01-07 | 01 | 1 | RICH-07 | unit | `pytest tests/test_table_renderer.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_math_renderer.py` — stubs for RICH-01
- [ ] `tests/test_code_renderer.py` — stubs for RICH-02
- [ ] `tests/test_image_renderer.py` — stubs for RICH-03
- [ ] `tests/test_mermaid_renderer.py` — stubs for RICH-04
- [ ] `tests/test_table_renderer.py` — stubs for RICH-05, RICH-07
- [ ] `tests/test_markdown_renderer.py` — stubs for RICH-06
- [ ] `latex2mathml`, `Pygments`, `Markdown`, `defusedxml`, `bleach` added to pyproject.toml

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| KaTeX renders in browser | RICH-01 | Requires browser rendering | Open generated HTML, verify equation displays |
| Mermaid SVG renders in browser | RICH-04 | Requires browser rendering | Open generated HTML, verify diagram displays |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
