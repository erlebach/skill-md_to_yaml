# Requirements: Slide DSL — YAML-to-HTML Presentation Compiler

**Defined:** 2026-03-21
**Core Value:** The YAML DSL must be simple enough that an LLM generates it reliably with high layout variety, and the Python compiler must produce ADA-compliant HTML indistinguishable in quality from current `/ada-slides-general` output.

## v1 Requirements

### DSL Schema

- [ ] **DSL-01**: Hybrid YAML+Markdown format: YAML frontmatter per slide (layout type, metadata, ADA fields) + Markdown content body
- [ ] **DSL-02**: ~15 layout primitives derived from analysis of existing HTML decks
- [ ] **DSL-03**: Each layout type has a Pydantic model with required/optional fields and validation
- [ ] **DSL-04**: Schema enforces structural consistency across layout types (isomorphic where possible to reduce LLM drift)
- [ ] **DSL-05**: Deck-level metadata section (title, author, date, theme) defined in schema
- [ ] **DSL-06**: JSON Schema generated from Pydantic models for external validation

### Compiler Core

- [ ] **COMP-01**: Python compiler reads YAML and produces a single self-contained HTML file
- [ ] **COMP-02**: Jinja2 templates render each layout type (one template per layout)
- [ ] **COMP-03**: Output is deterministic — same YAML input produces byte-identical HTML
- [ ] **COMP-04**: Compiler CLI accepts input YAML path and output HTML path
- [ ] **COMP-05**: CSS theme (dark background, amber accents) embedded in output HTML
- [ ] **COMP-06**: JavaScript for keyboard navigation (arrow keys, space, Home/End) embedded in output

### ADA Compliance

- [ ] **ADA-01**: Alt text is a required field on all image/figure/SVG layout types — compiler errors if missing
- [ ] **ADA-02**: ARIA carousel markup on slide container (`aria-roledescription="carousel"`) and each slide (`role="group"`, `aria-label="Slide N of M"`)
- [ ] **ADA-03**: Skip navigation link rendered at top of every deck (`<a href="#main-content" class="skip-link">`)
- [ ] **ADA-04**: Every slide has a heading (`<h1>` or `<h2>`) tied to `aria-labelledby`
- [ ] **ADA-05**: Keyboard navigation follows W3C APG carousel pattern
- [ ] **ADA-06**: Color contrast validated against WCAG 2.1 AA (4.5:1 normal text, 3:1 large text) at compile time
- [ ] **ADA-07**: Layout variety enforcement — compiler warns if 3+ consecutive slides use identical layout type
- [ ] **ADA-08**: Bullet limit validation — compiler warns if any slide has more than 5 bullet points

### Rich Content

- [ ] **RICH-01**: KaTeX math rendering via CDN auto-render (supports `$$...$$` and `$...$` blocks)
- [ ] **RICH-02**: Code blocks with syntax highlighting (Pygments or Highlight.js, language specified in YAML)
- [ ] **RICH-03**: JPEG/PNG images embedded as base64 or referenced by path, with required alt text
- [ ] **RICH-04**: SVG direct embedding with ADA wrapper (`<title>`, `<desc>`, `role="img"`, `aria-labelledby`)
- [ ] **RICH-05**: Inline Markdown rendering within slide content fields (bold, italic, lists, links)
- [ ] **RICH-06**: Mermaid diagrams compiled to static inline SVG with ADA attributes
- [ ] **RICH-07**: Tables with accessible markup (`<caption>`, `<th scope="col|row">`, proper header associations)

### LLM Authoring

- [ ] **LLM-01**: `/md_to_yaml` Claude Code skill generates YAML DSL from markdown/JPEG/PDF input
- [ ] **LLM-02**: Skill enforces design constraints (layout variety, bullet limits, alt text)
- [ ] **LLM-03**: YAML schema validation available (JSON Schema) to catch errors before compilation

## v2 Requirements

### Enhancements

- **ENH-01**: Speaker notes field (hidden `<aside>` with presenter mode)
- **ENH-02**: Configurable accent color within validated contrast range
- **ENH-03**: Fine-tuned local model on YAML DSL
- **ENH-04**: Hook-based auto-compilation (file watcher triggers compiler)

## Out of Scope

| Feature | Reason |
|---------|--------|
| PowerPoint/PPTX export | Cannot replicate CSS layouts, KaTeX, SVG faithfully; second rendering pipeline |
| PDF export | Headless Chrome dependency; tagged PDF accessibility is a separate WCAG domain |
| Real-time preview / hot reload | Dev server + WebSocket multiplies architecture; <1s compile is fast enough |
| Custom CSS per deck | Breaks ADA guarantees — custom CSS can violate contrast ratios |
| Interactive/animated slides | Fragment animations confuse screen readers; CSS scroll-snap only |
| LLM in compilation step | Destroys determinism — compiler must be pure Python |
| Slide deck editor UI | Separate product; maintenance burden exceeds compiler itself |
| Multi-language / i18n | Not in current use case; UTF-8 handles special characters |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DSL-01 | — | Pending |
| DSL-02 | — | Pending |
| DSL-03 | — | Pending |
| DSL-04 | — | Pending |
| DSL-05 | — | Pending |
| DSL-06 | — | Pending |
| COMP-01 | — | Pending |
| COMP-02 | — | Pending |
| COMP-03 | — | Pending |
| COMP-04 | — | Pending |
| COMP-05 | — | Pending |
| COMP-06 | — | Pending |
| ADA-01 | — | Pending |
| ADA-02 | — | Pending |
| ADA-03 | — | Pending |
| ADA-04 | — | Pending |
| ADA-05 | — | Pending |
| ADA-06 | — | Pending |
| ADA-07 | — | Pending |
| ADA-08 | — | Pending |
| RICH-01 | — | Pending |
| RICH-02 | — | Pending |
| RICH-03 | — | Pending |
| RICH-04 | — | Pending |
| RICH-05 | — | Pending |
| RICH-06 | — | Pending |
| RICH-07 | — | Pending |
| LLM-01 | — | Pending |
| LLM-02 | — | Pending |
| LLM-03 | — | Pending |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 0
- Unmapped: 30 ⚠️

---
*Requirements defined: 2026-03-21*
*Last updated: 2026-03-21 after initial definition*
