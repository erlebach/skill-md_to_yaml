---
phase: 02-compiler-core-ada
plan: 00
subsystem: tests
tags: [wave-0, tdd, stubs, xfail, ada, compiler]
dependency_graph:
  requires: []
  provides: [tests/test_compiler.py, tests/test_validators.py, tests/fixtures/minimal_deck.yaml]
  affects: [02-01, 02-02, 02-03, 02-04]
tech_stack:
  added: []
  patterns: [xfail stubs, Wave 0 Nyquist pattern]
key_files:
  created:
    - tests/test_compiler.py
    - tests/test_validators.py
    - tests/fixtures/minimal_deck.yaml
  modified: []
decisions: []
metrics:
  duration: 5min
  completed: 2026-03-22
  tasks_completed: 1
  files_changed: 3
---

# Phase 02 Plan 00: Wave 0 Test Stubs Summary

**One-liner:** 20 xfail pytest stubs for COMP-01 to COMP-06 and ADA-01 to ADA-08 with a minimal deck fixture, satisfying the Wave 0 Nyquist requirement.

## What Was Built

Two test stub files and one YAML fixture were created so that all Phase 2 plans have target test files available before Wave 1 implementation begins.

- `tests/test_compiler.py`: 10 xfail stubs covering compiler correctness (COMP-01 to COMP-06) and ADA markup requirements (ADA-02 to ADA-05), plus a CLI error path test.
- `tests/test_validators.py`: 10 xfail stubs covering ADA validators (ADA-01, ADA-06, ADA-07, ADA-08) including positive and negative variants.
- `tests/fixtures/minimal_deck.yaml`: Minimal valid deck (title + one content slide) for compiler integration tests.

## Verification Results

```
20 xfailed in 0.04s
```

All 20 tests collected and all marked xfail — no production imports, stubs importable before compiler/ package exists.

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create test stubs and minimal fixture | 1bffb7b | tests/test_compiler.py, tests/test_validators.py, tests/fixtures/minimal_deck.yaml |

## Self-Check: PASSED

- tests/test_compiler.py: FOUND
- tests/test_validators.py: FOUND
- tests/fixtures/minimal_deck.yaml: FOUND
- Commit 1bffb7b: FOUND
