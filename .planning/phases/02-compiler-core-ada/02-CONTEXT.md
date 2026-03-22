# Phase 2: Compiler Core + ADA - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a Python/Jinja2 compiler pipeline that reads validated YAML DSL (via the Phase 1 parser) and produces a single self-contained ADA-compliant HTML file. Includes keyboard navigation, ARIA carousel markup, skip links, design-rule enforcement (layout variety, bullet limits), and contrast validation. Rich content rendering (math, code highlighting, Mermaid, images) is Phase 3 — this phase handles structural HTML, CSS theming, and navigation JS.

</domain>

<decisions>
## Implementation Decisions

### Navigation & chrome
- Minimal chrome: slide counter ("3 / 25") in corner, keyboard navigation only
- No sidebar, no progress bar — clean full-bleed slides
- Keyboard: arrow keys advance/retreat, Home/End jump to first/last, Space advances
- No wrap-around: stop at first/last slide (standard W3C APG carousel behavior)
- Skip link at top of deck (`<a href="#main-content" class="skip-link">Skip to content</a>`)
- ARIA carousel markup: container has `aria-roledescription="carousel"`, each slide has `role="group"` + `aria-label="Slide N of M"`
- Every slide has a heading tied to `aria-labelledby`

### Theme & styling
- CSS custom properties for all colors, fonts, spacing (--bg, --text, --accent, --font-family, etc.)
- Dark and light themes swap CSS var values; easy to add new themes later
- Default accent: amber (#f0a500) — validated for WCAG 2.1 AA contrast (4.5:1 normal text, 3:1 large text)
- When user provides `accent_color` in metadata, compiler validates contrast ratio against theme background at compile time; error if it fails
- Font loaded from Google Fonts CDN (IBM Plex Sans default)
- Typography and spacing at Claude's discretion — keep it clean and readable

### Validation & warnings
- **Errors** (halt compilation, exit 1, no HTML produced): missing alt_text on image/figure/diagram, invalid accent_color contrast
- **Warnings** (printed to stderr, HTML still produced): 3+ consecutive identical layout types, 5+ bullet points on a slide
- Message format: plain text lines to stderr, markdown-friendly for copy/paste (e.g., `**WARNING** slide 4: 6 bullet points exceeds recommended maximum of 5`)
- Exit code 0 on success (even with warnings), exit code 1 on errors

### Template architecture
- One Jinja2 template file per layout type: `title.html.j2`, `content.html.j2`, `diagram.html.j2`, etc. (12 files)
- Base template `base.html.j2` provides HTML shell, embedded CSS, embedded JS, slide container
- Each layout template is a snippet included inside the slide wrapper
- `compiler/` package as sibling to `schema/`: `compiler/__init__.py`, `compiler/engine.py`, `compiler/templates/`
- CLI entry point: `python -m compiler input.yaml output.html`

### Design principle
- Minimize options, maximize extensibility — new layout types or themes should be addable without restructuring
- v1 ships with dark + light themes; adding a theme = adding a CSS var block
- v1 ships with 12 layout templates; adding a layout = adding one .j2 file

### Claude's Discretion
- Typography scale and spacing system
- Exact slide counter positioning and styling
- CSS reset / normalize approach
- How `notes` field renders as `<aside>` (hidden by default)
- Internal compiler architecture (visitor pattern, simple loop, etc.)
- Markdown rendering approach for slide bodies (placeholder in Phase 2, full rendering in Phase 3)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Schema (input contract)
- `schema/models.py` — 12 Pydantic layout models, DeckMetadata, Deck container, AnySlide union
- `schema/parser.py` — `parse_deck_file()` parser that produces validated Deck objects
- `docs/layouts.md` — Layout primitives reference with field tables and examples per type

### Requirements
- `.planning/REQUIREMENTS.md` — COMP-01 through COMP-06 (compiler core), ADA-01 through ADA-08 (accessibility)
- `.planning/ROADMAP.md` — Phase 2 success criteria (6 items)

### Prior phase decisions
- `.planning/phases/01-dsl-schema/01-CONTEXT.md` — Layout types, field naming, two-column conventions, theme defaults
- `.planning/phases/01.1-real-world-dsl-validation/01.1-CONTEXT.md` — Real-world validation results, no schema changes needed

### Existing decks (visual reference)
- `../n8n_to_python/output_html_files/*.html` — ~20 existing HTML decks showing target visual quality, CSS patterns, ARIA markup
- `tests/fixtures/real_*.yaml` — 5 validated real-world YAML deck fixtures

### ADA standards
- W3C APG Carousel Pattern — keyboard interaction model for slide navigation

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `schema/parser.py:parse_deck_file()` — Returns validated `Deck` object with `metadata` + `slides[]`; compiler's input
- `schema/models.py:AnySlide` — Discriminated union; `slide.layout` field determines which template to render
- `schema/models.py:DeckMetadata` — `theme`, `accent_color`, `font` fields drive CSS var selection
- `schema/models.py:TwoColumnSlide.proportion` — Maps to CSS grid column widths
- 5 real-world YAML fixtures in `tests/fixtures/real_*.yaml` — ready-made integration test inputs

### Established Patterns
- `extra='forbid'` on all models — no unknown fields leak through
- `body` field excluded from JSON Schema but populated by parser — templates access `slide.body`
- `_looks_like_frontmatter()` heuristic in parser — robust across 92 real-world slides
- Existing HTML decks use CSS custom properties (`--bg`, `--accent`, `--text`) — compiler should match this pattern

### Integration Points
- Compiler reads `Deck` objects from `schema.parser.parse_deck_file()`
- Layout type enum values (`slide.layout`) must match Jinja2 template filenames
- `DeckMetadata.theme` selects CSS var block; `DeckMetadata.accent_color` overrides `--accent`
- `DeckMetadata.font` selects Google Fonts import URL

</code_context>

<specifics>
## Specific Ideas

- User favors minimizing options but allowing easy extensions — architecture should make adding layouts/themes trivial
- Compiler warnings should be markdown-friendly (copy/pasteable into markdown viewers)
- Existing HTML decks in `../n8n_to_python/output_html_files/` are the visual quality bar — output should be indistinguishable

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-compiler-core-ada*
*Context gathered: 2026-03-22*
