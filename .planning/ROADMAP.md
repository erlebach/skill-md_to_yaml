# Roadmap: Slide DSL — YAML-to-HTML Presentation Compiler

## Overview

Build a two-stage pipeline: a YAML DSL schema that an LLM can generate reliably, and a deterministic Python compiler that transforms that YAML into ADA-compliant standalone HTML. The schema is the foundation everything depends on; the compiler delivers the core pipeline with full ADA enforcement; rich content types (math, code, diagrams, images) extend the pipeline; and the Claude Code skill wraps it all into a usable LLM-authoring frontend. Four phases, each delivering a coherent and verifiable capability.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: DSL Schema** - Define the YAML+Markdown DSL with ~15 layout primitives, Pydantic v2 models, and JSON Schema output
- [ ] **Phase 2: Compiler Core + ADA** - Build the Python/Jinja2 compiler pipeline with full ADA compliance enforcement
- [ ] **Phase 3: Rich Content** - Add math, code, SVG, images, Mermaid, tables, and Markdown rendering
- [ ] **Phase 4: LLM Skill + Validation** - Create the `/md_to_yaml` Claude Code skill and validate end-to-end on real decks

## Phase Details

### Phase 1: DSL Schema
**Goal**: A complete, validated YAML DSL schema that defines every layout primitive and enforces structural correctness — the interface contract for all downstream components
**Depends on**: Nothing (first phase)
**Requirements**: DSL-01, DSL-02, DSL-03, DSL-04, DSL-05, DSL-06
**Success Criteria** (what must be TRUE):
  1. A YAML file with all ~15 layout types validates against the Pydantic models with no errors
  2. A YAML file with a missing required field (e.g., missing alt_text on an image slide) produces a clear, actionable Pydantic error
  3. JSON Schema is generated from Pydantic models and validates the same test fixtures
  4. Deck-level metadata (title, author, date, theme) is representable and validated
  5. The layout primitive list is documented with one example slide per type
**Plans:** 2/2 plans executed — COMPLETE

Plans:
- [x] 01-01-PLAN.md — Pydantic v2 models (12 layouts + deck metadata) + JSON Schema export
- [x] 01-02-PLAN.md — Hybrid file parser + test fixtures + integration tests

### Phase 01.1: Real-World DSL Validation (INSERTED)

**Goal:** Validate the Phase 1 DSL schema against 5 real-world HTML presentation decks by converting them to YAML DSL format, fixing any schema/parser issues discovered, and closing DSL-01
**Requirements**: DSL-01
**Depends on:** Phase 1
**Plans:** 3/3 plans complete

Plans:
- [x] 01.1-01-PLAN.md — Test infrastructure + convert Decks 1 and 3 (quantum-transformers, quixer-implementation)
- [x] 01.1-02-PLAN.md — Convert Decks 2 and 4 (prototype-clustering, density-clustering)
- [x] 01.1-03-PLAN.md — Convert Deck 5 (clustering-ch8) + gap report + DSL-01 closure

### Phase 2: Compiler Core + ADA
**Goal**: A working end-to-end pipeline that compiles YAML to a standalone ADA-compliant HTML deck with keyboard navigation, ARIA markup, and design-rule enforcement
**Depends on**: Phase 1
**Requirements**: COMP-01, COMP-02, COMP-03, COMP-04, COMP-05, COMP-06, ADA-01, ADA-02, ADA-03, ADA-04, ADA-05, ADA-06, ADA-07, ADA-08
**Success Criteria** (what must be TRUE):
  1. Running `python -m compiler input.yaml output.html` produces a single self-contained HTML file
  2. The same YAML input produces byte-identical HTML on repeated runs
  3. An HTML deck passes axe-core WCAG 2.1 AA audit with zero violations on structural checks (ARIA carousel, skip link, slide headings)
  4. Keyboard navigation works: arrow keys advance/retreat slides, Home/End go to first/last
  5. Compiler exits with an error message if alt_text is missing on any image/figure/diagram slide
  6. Compiler emits a warning when 3+ consecutive slides use the same layout type
**Plans:** 2/5 plans executed

Plans:
- [ ] 02-01-PLAN.md — Compiler package scaffold + validators + contrast + CLI entry point
- [ ] 02-02-PLAN.md — Base Jinja2 template (CSS themes, ARIA, keyboard JS) + 12 layout templates
- [ ] 02-03-PLAN.md — Compiler engine (validate-then-render) + integration tests
- [ ] 02-04-PLAN.md — Real-fixture integration tests + visual spot-check

### Phase 3: Rich Content
**Goal**: The compiler handles all content types found in real decks — math equations, code blocks, images, SVG diagrams, Mermaid diagrams, tables, and inline Markdown
**Depends on**: Phase 2
**Requirements**: RICH-01, RICH-02, RICH-03, RICH-04, RICH-05, RICH-06, RICH-07
**Success Criteria** (what must be TRUE):
  1. A slide with a LaTeX equation (`$$...$$`) renders correctly via KaTeX CDN auto-render in browser
  2. A slide with a fenced code block renders with syntax highlighting and correct language label
  3. A JPEG/PNG image slide embeds or references the image and renders with its alt text visible to screen readers
  4. A Mermaid diagram slide compiles to inline SVG with ADA title/desc/role attributes
  5. A table slide renders with `<caption>`, `<th scope>`, and correct header associations
**Plans:** 2/3 plans executed

Plans:
- [ ] 03-01-PLAN.md — Renderer modules + schema updates + unit tests
- [ ] 03-02-PLAN.md — Engine integration + template updates + CLI flag
- [ ] 03-03-PLAN.md — Integration test fixtures + visual spot-check

### Phase 4: LLM Skill + Validation
**Goal**: A working `/md_to_yaml` Claude Code skill that generates valid YAML DSL from markdown/PDF/JPEG input, and end-to-end validation on 3+ real existing decks
**Depends on**: Phase 3
**Requirements**: LLM-01, LLM-02, LLM-03
**Success Criteria** (what must be TRUE):
  1. Running the `/md_to_yaml` skill on a markdown document produces YAML that validates against the Pydantic schema with no errors
  2. The skill's output uses a variety of layout types (no 3+ consecutive identical layouts)
  3. Three existing decks from `n8n_to_python/output_html_files/` are reconstructed through the pipeline and produce ADA-compliant HTML
  4. LLM-generated YAML that uses common field-name variants (e.g., `body` instead of `content`) is coerced or caught at parse time with a clear error
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 01.1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. DSL Schema | 2/2 | Complete | 2026-03-22 |
| 01.1. Real-World DSL Validation | 3/3 | Complete    | 2026-03-22 |
| 2. Compiler Core + ADA | 2/5 | In Progress|  |
| 3. Rich Content | 2/3 | In Progress|  |
| 4. LLM Skill + Validation | 0/TBD | Not started | - |
