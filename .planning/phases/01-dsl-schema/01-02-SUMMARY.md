---
phase: 01-dsl-schema
plan: 02
subsystem: parsing
tags: [pydantic, yaml, parser, fixtures, documentation]

requires:
  - phase: 01-dsl-schema
    plan: 01
    provides: "Pydantic v2 models (DeckMetadata, AnySlide, Deck, all 12 slide types)"

provides:
  - "schema/parser.py — parse_deck_file() reads hybrid YAML+Markdown files into validated Deck objects"
  - "tests/fixtures/ — 5 fixture files covering all 12 layout types, error cases, minimal metadata, two-column variants"
  - "tests/test_parser.py — 18 parser tests, all green"
  - "tests/conftest.py — pytest fixtures for all fixture file paths"
  - "docs/layouts.md — 339-line layout primitive reference with field tables and examples"

affects:
  - 02-compiler
  - 03-rich-content

tech-stack:
  added: []
  patterns:
    - "Hybrid YAML+Markdown parsing: split on ^---$ boundaries, pair frontmatter+body parts using _looks_like_frontmatter() heuristic"
    - "Detect body: in frontmatter YAML and raise ValueError with clear message"
    - "TDD: RED (failing tests) committed before GREEN (implementation)"

key-files:
  created:
    - schema/parser.py
    - tests/fixtures/valid_deck.yaml
    - tests/fixtures/invalid_missing_alt.yaml
    - tests/fixtures/invalid_unknown_field.yaml
    - tests/fixtures/deck_metadata_minimal.yaml
    - tests/fixtures/two_column_variants.yaml
    - tests/conftest.py
    - tests/test_parser.py
    - docs/layouts.md
  modified: []

key-decisions:
  - "Parser uses _looks_like_frontmatter() heuristic (checks for 'layout' key) to distinguish slide body text from the next slide's frontmatter block, avoiding false splits on Markdown containing YAML-like content"
  - "body: in YAML frontmatter raises ValueError with clear message rather than being silently passed to Pydantic (since body is a legitimate field on SlideBase, extra='forbid' alone wouldn't catch it)"
  - "<!-- split --> marker preserved in body by parser; splitting into left/right columns is the compiler's responsibility (Phase 2)"

patterns-established:
  - "Fixture-driven TDD: write fixtures first, then failing tests, then implementation"
  - "Parser splits on FENCE_RE = re.compile(r'^---\\s*$', re.MULTILINE) to avoid false splits on --- inside Markdown bodies"

requirements-completed: [DSL-01]

duration: 3min
completed: 2026-03-22
---

# Phase 01 Plan 02: DSL Schema — Parser and Documentation Summary

**Hybrid YAML+Markdown parser using regex fence splitting and _looks_like_frontmatter() heuristic, with 18 parser tests (TDD) and 339-line layout reference docs covering all 12 slide types**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-22T04:01:32Z
- **Completed:** 2026-03-22T04:05:22Z
- **Tasks:** 3 (Task 1: fixtures, Task 2: parser TDD, Task 3: docs)
- **Files modified:** 9 created, 0 modified

## Accomplishments

- Full test fixture suite: 5 YAML files covering all 12 layouts, error cases (missing alt_text, body in frontmatter), minimal metadata, and all two-column permutations
- Parser correctly handles the hybrid format — 12 slides parsed from valid_deck.yaml, all Pydantic-validated
- 78/78 tests pass across the full suite (models + JSON schema + parser)
- Layout primitive reference with field tables, examples, and two-column conventions

## Task Commits

1. **Task 1: Test fixtures** - `ac3ab7c` (feat)
2. **Task 2: Failing tests (RED)** - `7e1b069` (test)
3. **Task 2: Parser implementation (GREEN)** - `5f4e8e4` (feat)
4. **Task 3: Layout docs** - `ea74ff1` (docs)

## Files Created/Modified

- `schema/parser.py` — parse_deck_file() + _split_into_slides() + _looks_like_frontmatter()
- `tests/fixtures/valid_deck.yaml` — 12-slide happy-path fixture
- `tests/fixtures/invalid_missing_alt.yaml` — figure slide without alt_text
- `tests/fixtures/invalid_unknown_field.yaml` — content slide with body in frontmatter
- `tests/fixtures/deck_metadata_minimal.yaml` — minimal deck with only title
- `tests/fixtures/two_column_variants.yaml` — 4 two-column permutations
- `tests/conftest.py` — pytest path fixtures
- `tests/test_parser.py` — 18 parser tests
- `docs/layouts.md` — 339-line layout reference

## Decisions Made

- Parser uses `_looks_like_frontmatter()` (checks for `layout` key in parsed YAML) to distinguish Markdown body from next slide's frontmatter. This handles the ambiguity in the boundary between slide body and next slide header when splitting on `---`.
- `body:` in YAML frontmatter raises `ValueError` with a message containing `'body'`. Since `body` is a legitimate field on `SlideBase` (excluded from JSON Schema), `extra='forbid'` alone won't catch it — explicit detection is required.
- The `<!-- split -->` marker is preserved verbatim in `body` by the parser. Splitting into left/right columns for two-column slides is the compiler's job (Phase 2), not the parser's.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

- `test_invalid_unknown_field` initially failed: `body` is a declared field on `SlideBase`, not an extra field, so Pydantic's `extra='forbid'` does not trigger on it. Fixed by adding explicit frontmatter key detection in the parser (Rule 1 — bug in the design assumption). Test updated to accept `ValueError` alongside `ValidationError`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- DSL schema complete: models + parser + JSON Schema export all functional and tested
- Phase 2 compiler can import `parse_deck_file` from `schema.parser` to load deck files
- Layout reference in `docs/layouts.md` ready for LLM prompt engineering
- Blocker from STATE.md: mmdc Python package stability should be verified before Phase 3 commits to Mermaid rendering

---
*Phase: 01-dsl-schema*
*Completed: 2026-03-22*
