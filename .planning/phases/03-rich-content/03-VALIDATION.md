---
phase: 3
slug: rich-content
status: draft
nyquist_compliant: true
wave_0_complete: true
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

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 03-01-01 | 01 | 1 | RICH-01 | unit | `pytest tests/test_rich_content.py::test_math_display tests/test_rich_content.py::test_math_inline tests/test_rich_content.py::test_math_extraction_before_markdown -x` | ⬜ pending |
| 03-01-02 | 01 | 1 | RICH-02 | unit | `pytest tests/test_rich_content.py::test_code_highlight tests/test_rich_content.py::test_code_unknown_lang tests/test_rich_content.py::test_code_line_numbers tests/test_rich_content.py::test_pygments_css -x` | ⬜ pending |
| 03-01-03 | 01 | 1 | RICH-03 | unit | `pytest tests/test_rich_content.py::test_image_path_ref tests/test_rich_content.py::test_image_embed tests/test_rich_content.py::test_image_missing_warning -x` | ⬜ pending |
| 03-01-04 | 01 | 1 | RICH-04 | unit | `pytest tests/test_rich_content.py::test_mermaid_render_mock tests/test_rich_content.py::test_mermaid_no_mmdc -x` | ⬜ pending |
| 03-01-05 | 01 | 1 | RICH-05 | unit | `pytest tests/test_rich_content.py::test_table_model -x` | ⬜ pending |
| 03-01-06 | 01 | 1 | RICH-06 | unit | `pytest tests/test_rich_content.py::test_markdown_inline tests/test_rich_content.py::test_markdown_list -x` | ⬜ pending |
| 03-01-07 | 01 | 1 | RICH-07 | unit | `pytest tests/test_rich_content.py::test_svg_sanitize tests/test_rich_content.py::test_svg_sanitize_onclick tests/test_rich_content.py::test_svg_embed_ada tests/test_rich_content.py::test_svg_dimensions -x` | ⬜ pending |
| 03-01-08 | 01 | 1 | RICH-01..07 | unit | `pytest tests/test_rich_content.py::test_render_body_orchestration -x` | ⬜ pending |
| 03-02-01 | 02 | 2 | RICH-01..07 | unit | `pytest tests/ -x -q` | ⬜ pending |
| 03-03-01 | 03 | 3 | RICH-01..07 | integration | `pytest tests/test_rich_integration.py -x -q` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Plan 03-01 Task 2 creates `tests/test_rich_content.py` with all unit tests. Plan 03-03 Task 1 creates `tests/test_rich_integration.py`. No separate stub files needed — tests are created inline with implementation (TDD pattern in Plan 01).

- [ ] `tests/test_rich_content.py` — unit tests for all renderers (RICH-01 through RICH-07)
- [ ] `tests/test_rich_integration.py` — integration tests compiling YAML to HTML (Plan 03)
- [ ] `latex2mathml`, `Pygments`, `Markdown`, `defusedxml`, `bleach` added to pyproject.toml

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MathML renders in browser | RICH-01 | Requires browser rendering | Open generated HTML, verify equation displays |
| Mermaid SVG renders in browser | RICH-04 | Requires browser rendering | Open generated HTML, verify diagram displays |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
