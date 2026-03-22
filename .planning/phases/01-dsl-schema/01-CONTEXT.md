# Phase 1: DSL Schema - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Define the YAML+Markdown DSL with ~12 layout primitives, Pydantic v2 models, and JSON Schema output. This phase delivers the interface contract for all downstream components — the schema that the LLM generates and the compiler consumes. No compiler, no rendering, no skill — just the schema and its validation.

</domain>

<decisions>
## Implementation Decisions

### Layout primitive list
- 12 layout types: title, hero, content, divider, figure, diagram, two-column, quote, comparison, code, steps, summary
- `title` = deck opener (big title + subtitle + author). `hero` = section opener within deck (section title + short description). Separate types with different visual treatment
- `figure` = raster images (JPEG/PNG) with src, alt_text. `diagram` = SVG/Mermaid with source code, alt_text. Separate types due to different required fields and rendering pipelines
- `summary` layout type is at Claude's discretion (whether to include and how to differentiate from content)
- Table layout deferred to Phase 3 (Rich Content)
- List is extensible — new types can be added in later phases without schema redesign

### Slide document format
- Hybrid format: YAML frontmatter (between `---` markers) for structured fields + free Markdown body for content
- Each slide has its own frontmatter block; slides separated by `---`
- First frontmatter block is deck-level metadata
- File extension: `.yaml`
- Custom parser needed (split on `---`, parse YAML frontmatter, treat remainder as Markdown body)

### Two-column convention
- Whichever column has structured content (image, diagram, Mermaid) goes in frontmatter as `left:` or `right:` with type/fields
- The Markdown body fills the other column (the "free content" side)
- If both columns are structured (two images, two diagrams), both go in frontmatter — body is empty/unused
- If both columns are free text, body uses `<!-- split -->` marker to separate left and right
- This rule covers all combinations consistently

### Mermaid diagram handling
- Full-width diagram slide: Mermaid code goes in the Markdown body as a fenced code block
- Two-column with diagram: Mermaid goes in frontmatter under `left.source:` or `right.source:` as the structured column
- Consistent with the image convention — structured content always in frontmatter when in a two-column

### Field naming & consistency
- Isomorphic field names across all layout types: same field names everywhere possible
- Shared fields on every layout: `layout` (required), `title` (required), `notes` (optional — speaker notes, rendered as hidden `<aside>`)
- `title` is required on ALL layouts including divider — but compiler may render it in different positions/styles per layout type
- `alt_text` required on all visual types (figure, diagram)
- Strict validation — unknown fields produce clear error messages (e.g., "Unknown field 'body' — did you mean 'content'?"). No silent alias coercion
- Layout-specific fields use natural names (e.g., `attribution` on quote, `language` on code, `src` on figure)

### Speaker notes
- Optional `notes` field on every slide (part of base model)
- Rendered as hidden `<aside>` in HTML — ready for presenter mode even though ENH-01 is v2

### Deck metadata & theming
- First frontmatter block contains deck-level metadata
- `title` is the only required field
- Optional fields: `author`, `date`, `theme`, `accent_color`, `font`
- Defaults: no author, today's date, dark theme, amber accent, IBM Plex Sans
- Theme: v1 ships with two themes — dark and light
- `accent_color`: overrides default accent; compiler validates contrast ratio (Phase 2)
- `font`: validated set of presets (e.g., IBM Plex Sans, Inter, Fira Sans) — not arbitrary fonts

### Claude's Discretion
- Whether `summary` layout is distinct from `content` or just a styled variant
- Exact Pydantic model inheritance hierarchy (base model, mixins, per-layout models)
- JSON Schema generation approach (Pydantic's built-in `.model_json_schema()` or custom)
- Validation error message formatting
- Which font presets to include in the validated set

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project context
- `.planning/PROJECT.md` — Core value, key decisions (hybrid YAML+Markdown format, Pydantic v2, KaTeX, deterministic compiler)
- `.planning/REQUIREMENTS.md` — DSL-01 through DSL-06 define Phase 1 requirements
- `.planning/ROADMAP.md` — Phase 1 success criteria (5 items)

### Existing decks (ground truth for layout primitives)
- `../n8n_to_python/output_html_files/*.html` — ~20 existing HTML decks to analyze for layout patterns, CSS variables, slide classes, ADA markup

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- No existing Python code or Pydantic models — greenfield for this phase

### Established Patterns
- Existing HTML decks use CSS custom properties (`--bg`, `--accent`, `--text`, etc.) for theming
- Slide classes found across decks: `slide-hero`, `slide--content`, `slide--diagram`, `slide--divider`, `slide--figure`, `slide--title`
- Decks include: sidebar navigation, slide numbering, skip links, ARIA carousel markup, `sr-only` class, `prefers-reduced-motion` support
- Font: IBM Plex Sans loaded from Google Fonts CDN
- Color scheme: dark background (#0d1117), blue accent (#58a6ff), with green/orange variants

### Integration Points
- Schema output (Pydantic models + JSON Schema) will be consumed by Phase 2 compiler
- Layout type enum must match Jinja2 template names in Phase 2
- Field names in schema become the template variable names

</code_context>

<specifics>
## Specific Ideas

- Two-column layout must support flexible content: text+image, image+text, text+text, image+image, diagram+text, etc. — not just a fixed left-text/right-image pattern
- The hybrid format should feel natural for LLM generation — Markdown body at zero indentation, YAML frontmatter only for structured metadata
- Existing decks use amber accents but user wants accent_color to be configurable with contrast validation

</specifics>

<deferred>
## Deferred Ideas

- Table layout type — deferred to Phase 3 (Rich Content)

</deferred>

---

*Phase: 01-dsl-schema*
*Context gathered: 2026-03-21*
