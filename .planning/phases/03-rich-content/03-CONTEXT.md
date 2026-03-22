# Phase 3: Rich Content - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Add rendering support for all rich content types to the existing compiler pipeline: math equations (LaTeX to MathML), code blocks with syntax highlighting, JPEG/PNG images, SVG diagrams, Mermaid diagrams, tables, and inline Markdown. Each content type integrates into the existing Jinja2 template system. The `/md_to_yaml` Claude Code skill is Phase 4 — this phase only handles compiler-side rendering.

</domain>

<decisions>
## Implementation Decisions

### Math rendering
- LaTeX expressions (`$$...$$` display, `$...$` inline) are converted to MathML at compile time
- Use `latex2mathml` Python library (pure Python, no external dependencies)
- Output contains native `<math>` elements — browsers render natively, no JS/CDN needed
- Fully self-contained, excellent ADA compliance (screen readers can interpret MathML)
- Architecture should allow swapping in KaTeX or MathJax backends later — keep math rendering modular

### Code blocks & syntax highlighting
- Pygments at compile time — generates styled `<span>` elements with CSS classes
- No CDN dependency, consistent with compile-time MathML decision
- Line numbers: off by default, opt-in via `line_numbers: true` field on CodeSlide model
- Pygments color theme auto-matches slide theme (dark theme → Monokai-style, light theme → light code theme)

### Image handling
- File path references by default (`<img src="images/fig1.png">`)
- CLI flag `--embed-images` to base64-encode images as data URIs for self-contained output
- Compiler warns on stderr if a referenced image file doesn't exist at compile time (HTML still produced)
- Alt text already required by schema (ADA-01) — no change needed

### SVG embedding
- SVGs embedded directly in HTML with ADA wrapper (`<title>`, `<desc>`, `role="img"`, `aria-labelledby`)
- Compiler sanitizes SVGs before embedding — strips `<script>`, `onclick`, event handlers, etc.
- Alt text required (enforced by existing schema validation)

### Mermaid diagrams
- Compiled to SVG at compile time using `mmdc` (Mermaid CLI, requires Node)
- Output SVG embedded inline with ADA attributes (`<title>`, `<desc>`, `role="img"`)
- Node is a build dependency for Mermaid support

### Tables
- Accessible markup: `<caption>`, `<th scope="col|row">`, proper header associations
- Wide tables wrapped in a horizontally scrollable container
- Table styling consistent with slide theme via CSS custom properties

### Inline Markdown
- Python-Markdown library for rendering body content (bold, italic, lists, links)
- Supports GFM-style extensions
- Replaces the placeholder rendering from Phase 2

### Claude's Discretion
- Specific Pygments theme pairings for dark/light
- SVG sanitization library choice (e.g., `bleach`, `defusedxml`, or custom)
- `latex2mathml` configuration details
- Table caption extraction strategy from YAML
- Markdown extension set selection
- Internal module organization for rich content renderers

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Schema (input contract)
- `schema/models.py` — Pydantic models including `DiagramSlide` (Mermaid source field), `CodeSlide` (language field), `FigureSlide`/`ImageSlide` (image paths, alt_text)
- `schema/parser.py` — Parser that populates `body` field from Markdown content sections
- `docs/layouts.md` — Layout primitives reference with field tables

### Compiler (integration point)
- `compiler/engine.py` — Validate-then-render pipeline; rich content renderers plug in here
- `compiler/templates/` — Jinja2 templates per layout type; templates need updating for rich content
- `compiler/validators.py` — Pre-render validation; may need extension for new content types

### Requirements
- `.planning/REQUIREMENTS.md` — RICH-01 through RICH-07 (the 7 requirements for this phase)
- `.planning/ROADMAP.md` — Phase 3 success criteria (5 items)

### Prior phase decisions
- `.planning/phases/02-compiler-core-ada/02-CONTEXT.md` — Template architecture (one .j2 per layout), CSS custom properties, validation error/warning distinction

### Existing decks (reference)
- `../n8n_to_python/output_html_files/*.html` — Existing HTML decks showing KaTeX math, inline SVG, code blocks
- `tests/fixtures/real_*.yaml` — 5 validated real-world YAML fixtures (may contain math/code/diagram slides)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `compiler/engine.py:compile()` — Main pipeline; rich content rendering hooks into `_render()`
- `compiler/templates/base.html.j2` — HTML shell with embedded CSS/JS; needs Pygments CSS and MathML styles
- `compiler/validators.py` — Error/warning framework; extend for image path validation
- `schema/models.py:DiagramSlide` — Already has `source` field for Mermaid diagram code
- `schema/models.py:CodeSlide` — Already has `language` field; needs `line_numbers` field added

### Established Patterns
- One Jinja2 template per layout type — new rich content extends existing templates, doesn't create new ones
- CSS custom properties for theming — Pygments theme and table styles should use the same pattern
- Validation split: errors (halt) vs warnings (stderr) — image path checks are warnings
- `body` field populated by parser, excluded from JSON Schema — Markdown rendering applies to this field

### Integration Points
- `compiler/engine.py:_render()` — Markdown body rendering, MathML conversion, and Pygments highlighting happen before or during template rendering
- `compiler/templates/*.html.j2` — Templates for `diagram`, `code`, `figure`, `comparison`, `table` layouts need rich content markup
- `schema/models.py:CodeSlide` — Add `line_numbers: bool = False` field
- CLI argument parser — Add `--embed-images` flag

</code_context>

<specifics>
## Specific Ideas

- Math rendering should be modular enough to swap MathML for KaTeX or MathJax later, or offer all three as options for testing
- The modular architecture of the existing compiler (one template per layout, CSS vars for theming) should make rich content additions straightforward

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-rich-content*
*Context gathered: 2026-03-22*
