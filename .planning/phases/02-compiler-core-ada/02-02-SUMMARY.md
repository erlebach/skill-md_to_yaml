---
phase: 02-compiler-core-ada
plan: 02
subsystem: compiler/templates
tags: [jinja2, templates, aria, accessibility, css-themes, keyboard-nav]
dependency_graph:
  requires: [02-00, schema/models.py]
  provides: [compiler/templates/*.html.j2]
  affects: [02-03-engine]
tech_stack:
  added: [Jinja2 templates]
  patterns: [W3C APG carousel ARIA pattern, CSS custom properties theming, scroll-snap layout]
key_files:
  created:
    - compiler/templates/base.html.j2
    - compiler/templates/title.html.j2
    - compiler/templates/hero.html.j2
    - compiler/templates/content.html.j2
    - compiler/templates/divider.html.j2
    - compiler/templates/figure.html.j2
    - compiler/templates/diagram.html.j2
    - compiler/templates/two-column.html.j2
    - compiler/templates/quote.html.j2
    - compiler/templates/comparison.html.j2
    - compiler/templates/code.html.j2
    - compiler/templates/steps.html.j2
    - compiler/templates/summary.html.j2
  modified: []
decisions:
  - "code.html.j2 uses | e (not | safe) to prevent XSS in literal code blocks"
  - "quote.html.j2 uses visually-hidden h2 for aria-labelledby while blockquote renders the visible quote text"
  - "two-column proportion rendered via Jinja2 replace filter: '50/50' -> 'two-col-50-50'"
metrics:
  duration: 8min
  completed: "2026-03-22"
  tasks: 2
  files: 13
---

# Phase 02 Plan 02: Jinja2 Template Set Summary

**One-liner:** 13 Jinja2 templates providing W3C APG carousel ARIA structure, dark/light CSS custom-property themes, embedded keyboard navigation JS, and 12 slide layout snippets.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Base template with CSS themes, ARIA, keyboard JS | a36b097 | compiler/templates/base.html.j2 |
| 2 | 12 layout snippet templates | 5ca2411 | compiler/templates/{title,hero,content,divider,figure,diagram,two-column,quote,comparison,code,steps,summary}.html.j2 |

## What Was Built

**Base template (`base.html.j2`):**
- HTML5 shell with `data-theme` attribute for dark/light switching
- Embedded CSS: CSS reset, `:root[data-theme="dark"]` and `:root[data-theme="light"]` with `--bg`, `--text`, `--accent`, `--muted`, `--border`, `--font-family` custom properties
- Skip link (`<a href="#main-content" class="skip-link">`) shown on focus
- Slide counter `<div id="slide-counter" aria-live="polite">` fixed bottom-right
- ARIA carousel: `<main role="region" aria-roledescription="carousel">` containing `<section role="group" aria-roledescription="slide">` per slide
- Each section has `aria-labelledby="slide-N-heading"` linking to heading in the included snippet
- Keyboard JS: ArrowRight/Down/Space (next), ArrowLeft/Up (prev), Home, End — all with `e.preventDefault()`
- Scroll-snap layout: `scroll-snap-type: y mandatory` on main

**Layout snippets (12 files):**
- Every template starts with heading carrying `id="slide-{{ loop.index }}-heading"` for ARIA linkage
- `figure.html.j2`: `<img alt="{{ slide.alt_text | e }}">` for ADA compliance
- `diagram.html.j2`: wrapper `<div role="img" aria-label="{{ slide.alt_text | e }}">` for ADA compliance
- `two-column.html.j2`: CSS grid class derived from `slide.proportion | replace('/', '-')`
- `comparison.html.j2`: splits `slide.body` on `<!-- split -->` for two-column render
- `code.html.j2`: uses `| e` (HTML-escaped) for code content — not `| safe`
- All other body-rendering templates use `| safe` (Phase 3 will render Markdown before passing HTML)

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

All 13 template files verified present:
- compiler/templates/base.html.j2 — FOUND
- All 12 layout templates — FOUND (13 total confirmed by wc -l)
- Commits a36b097 and 5ca2411 — FOUND in git log
