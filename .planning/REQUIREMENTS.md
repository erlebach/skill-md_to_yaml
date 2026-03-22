# Requirements: Slide DSL — YAML-to-HTML Presentation Compiler

**Defined:** 2026-03-21
**Core Value:** The YAML DSL must be simple enough that an LLM generates it reliably with high layout variety, and the Python compiler must produce ADA-compliant HTML indistinguishable in quality from current `/ada-slides-general` output.

## v1 Requirements

### DSL Schema

- [x] **DSL-01**: Hybrid YAML+Markdown format: YAML frontmatter per slide (layout type, metadata, ADA fields) + Markdown content body
- [x] **DSL-02**: ~15 layout primitives derived from analysis of existing HTML decks
- [x] **DSL-03**: Each layout type has a Pydantic model with required/optional fields and validation
- [x] **DSL-04**: Schema enforces structural consistency across layout types (isomorphic where possible to reduce LLM drift)
- [x] **DSL-05**: Deck-level metadata section (title, author, date, theme) defined in schema
- [x] **DSL-06**: JSON Schema generated from Pydantic models for external validation

### Compiler Core

- [x] **COMP-01**: Python compiler reads YAML and produces a single self-contained HTML file
- [x] **COMP-02**: Jinja2 templates render each layout type (one template per layout)
- [x] **COMP-03**: Output is deterministic — same YAML input produces byte-identical HTML
- [x] **COMP-04**: Compiler CLI accepts input YAML path and output HTML path
- [x] **COMP-05**: CSS theme (dark background, amber accents) embedded in output HTML
- [x] **COMP-06**: JavaScript for keyboard navigation (arrow keys, space, Home/End) embedded in output

### ADA Compliance

- [x] **ADA-01**: Alt text is a required field on all image/figure/SVG layout types — compiler errors if missing
- [x] **ADA-02**: ARIA carousel markup on slide container (`aria-roledescription="carousel"`) and each slide (`role="group"`, `aria-label="Slide N of M"`)
- [x] **ADA-03**: Skip navigation link rendered at top of every deck (`<a href="#main-content" class="skip-link">`)
- [x] **ADA-04**: Every slide has a heading (`<h1>` or `<h2>`) tied to `aria-labelledby`
- [x] **ADA-05**: Keyboard navigation follows W3C APG carousel pattern
- [x] **ADA-06**: Color contrast validated against WCAG 2.1 AA (4.5:1 normal text, 3:1 large text) at compile time
- [x] **ADA-07**: Layout variety enforcement — compiler warns if 3+ consecutive slides use identical layout type
- [x] **ADA-08**: Bullet limit validation — compiler warns if any slide has more than 5 bullet points

### Rich Content

- [x] **RICH-01**: KaTeX math rendering via CDN auto-render (supports `$$...$$` and `$...$` blocks)
- [x] **RICH-02**: Code blocks with syntax highlighting (Pygments or Highlight.js, language specified in YAML)
- [x] **RICH-03**: JPEG/PNG images embedded as base64 or referenced by path, with required alt text
- [x] **RICH-04**: SVG direct embedding with ADA wrapper (`<title>`, `<desc>`, `role="img"`, `aria-labelledby`)
- [x] **RICH-05**: Inline Markdown rendering within slide content fields (bold, italic, lists, links)
- [x] **RICH-06**: Mermaid diagrams compiled to static inline SVG with ADA attributes
- [x] **RICH-07**: Tables with accessible markup (`<caption>`, `<th scope="col|row">`, proper header associations)

### LLM Authoring

- [ ] **LLM-01**: `/md_to_yaml` Claude Code skill generates YAML DSL from markdown/JPEG/PDF input
- [x] **LLM-02**: Skill enforces design constraints (layout variety, bullet limits, alt text)
- [x] **LLM-03**: YAML schema validation available (JSON Schema) to catch errors before compilation

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
| DSL-01 | Phase 1 | Complete |
| DSL-02 | Phase 1 | Complete |
| DSL-03 | Phase 1 | Complete |
| DSL-04 | Phase 1 | Complete |
| DSL-05 | Phase 1 | Complete |
| DSL-06 | Phase 1 | Complete |
| COMP-01 | Phase 2 | Complete |
| COMP-02 | Phase 2 | Complete |
| COMP-03 | Phase 2 | Complete |
| COMP-04 | Phase 2 | Complete |
| COMP-05 | Phase 2 | Complete |
| COMP-06 | Phase 2 | Complete |
| ADA-01 | Phase 2 | Complete |
| ADA-02 | Phase 2 | Complete |
| ADA-03 | Phase 2 | Complete |
| ADA-04 | Phase 2 | Complete |
| ADA-05 | Phase 2 | Complete |
| ADA-06 | Phase 2 | Complete |
| ADA-07 | Phase 2 | Complete |
| ADA-08 | Phase 2 | Complete |
| RICH-01 | Phase 3 | Complete |
| RICH-02 | Phase 3 | Complete |
| RICH-03 | Phase 3 | Complete |
| RICH-04 | Phase 3 | Complete |
| RICH-05 | Phase 3 | Complete |
| RICH-06 | Phase 3 | Complete |
| RICH-07 | Phase 3 | Complete |
| LLM-01 | Phase 4 | Pending |
| LLM-02 | Phase 4 | Complete |
| LLM-03 | Phase 4 | Complete |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 30
- Unmapped: 0

---
*Requirements defined: 2026-03-21*
*Last updated: 2026-03-21 after roadmap creation*
