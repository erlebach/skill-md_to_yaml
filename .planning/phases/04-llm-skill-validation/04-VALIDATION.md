---
phase: 4
slug: llm-skill-validation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (already configured) |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `cd /Users/erlebach/src/2026/claude-code/n8n/md_to_yaml && python3 -m pytest tests/ -x -q --tb=short` |
| **Full suite command** | `cd /Users/erlebach/src/2026/claude-code/n8n/md_to_yaml && python3 -m pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/ -x -q --tb=short`
- **After every plan wave:** Run `python3 -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green + E2E manual spot-check on 3 PDFs
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 0 | LLM-01 | unit | `pytest tests/test_skill_output.py -x` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | LLM-01 | integration | `parse_deck_file()` on skill output | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 1 | LLM-02 | unit | `pytest tests/test_skill_output.py::test_layout_variety -x` | ❌ W0 | ⬜ pending |
| 04-02-02 | 02 | 1 | LLM-02 | unit | existing `validate_deck()` + fixture | ✅ | ⬜ pending |
| 04-03-01 | 03 | 1 | LLM-03 | unit | `pytest tests/test_skill_output.py::test_yaml_validates -x` | ❌ W0 | ⬜ pending |
| 04-03-02 | 03 | 1 | LLM-03 | unit | `pytest tests/test_parser.py::test_body_in_frontmatter -x` | ✅ | ⬜ pending |
| 04-E2E | 03 | 2 | E2E | e2e | manual spot-check + axe/WAVE | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_skill_output.py` — stubs for LLM-01, LLM-02, LLM-03 with fixture YAML files
- [ ] `tests/fixtures/skill_output_sample.yaml` — sample LLM-generated YAML for unit tests

*Existing infrastructure covers field-name variant testing (test_body_in_frontmatter) and validate_deck().*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 3 PDFs produce ADA-compliant HTML | E2E (SC-3) | Requires visual inspection + axe/WAVE browser tool | 1. Run skill on each PDF 2. Open output HTML 3. Run axe DevTools 4. Verify no critical violations |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
