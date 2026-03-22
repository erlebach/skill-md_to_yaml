---
phase: 2
slug: compiler-core-ada
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest >= 9.0 |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `pytest tests/test_compiler.py tests/test_validators.py -x` |
| **Full suite command** | `pytest tests/ -x` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_compiler.py tests/test_validators.py -x`
- **After every plan wave:** Run `pytest tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 0 | COMP-01 | integration | `pytest tests/test_compiler.py::test_compile_produces_html -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 0 | COMP-02 | integration | `pytest tests/test_compiler.py::test_all_layout_types_render -x` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 0 | COMP-03 | integration | `pytest tests/test_compiler.py::test_deterministic_output -x` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 0 | COMP-04 | integration | `pytest tests/test_compiler.py::test_cli_invocation -x` | ❌ W0 | ⬜ pending |
| 02-01-05 | 01 | 0 | COMP-05 | unit | `pytest tests/test_compiler.py::test_css_vars_embedded -x` | ❌ W0 | ⬜ pending |
| 02-01-06 | 01 | 0 | COMP-06 | unit | `pytest tests/test_compiler.py::test_keyboard_js_embedded -x` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 0 | ADA-01 | unit | `pytest tests/test_validators.py::test_missing_alt_text_error -x` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 0 | ADA-02 | unit | `pytest tests/test_compiler.py::test_aria_carousel_markup -x` | ❌ W0 | ⬜ pending |
| 02-02-03 | 02 | 0 | ADA-03 | unit | `pytest tests/test_compiler.py::test_skip_link_present -x` | ❌ W0 | ⬜ pending |
| 02-02-04 | 02 | 0 | ADA-04 | unit | `pytest tests/test_compiler.py::test_aria_labelledby -x` | ❌ W0 | ⬜ pending |
| 02-02-05 | 02 | 0 | ADA-05 | unit | `pytest tests/test_compiler.py::test_keyboard_js_embedded -x` | ❌ W0 | ⬜ pending |
| 02-02-06 | 02 | 0 | ADA-06 | unit | `pytest tests/test_validators.py::test_invalid_contrast_error -x` | ❌ W0 | ⬜ pending |
| 02-02-07 | 02 | 0 | ADA-07 | unit | `pytest tests/test_validators.py::test_layout_variety_warning -x` | ❌ W0 | ⬜ pending |
| 02-02-08 | 02 | 0 | ADA-08 | unit | `pytest tests/test_validators.py::test_bullet_limit_warning -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_compiler.py` — stubs for COMP-01 through COMP-06, ADA-02 through ADA-05
- [ ] `tests/test_validators.py` — stubs for ADA-01, ADA-06, ADA-07, ADA-08
- [ ] `tests/fixtures/minimal_deck.yaml` — minimal valid deck for compiler tests

*Existing `tests/conftest.py` and pytest config in `pyproject.toml` carry forward from Phase 1.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual keyboard focus ring | ADA-05 | CSS visual check | Open output.html, Tab to slides, verify visible focus indicator |
| Screen reader announcement | ADA-02 | Requires AT | Open in VoiceOver, verify "carousel" role announced |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
