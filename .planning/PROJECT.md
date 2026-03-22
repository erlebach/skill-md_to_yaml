# Slide DSL: YAML-to-HTML Presentation Compiler

## What This Is

A system that replaces direct LLM-generated HTML slide decks with a two-stage pipeline: (1) a Claude Code skill (`/md_to_yaml`) that converts markdown/JPEG/PDF input into a compact YAML slide DSL using ~15 layout primitives, and (2) a deterministic Python compiler that transforms that YAML into ADA-compliant HTML. This is the "Beamer for HTML" — high-level layout functions that compile to correct, accessible presentations.

## Core Value

The YAML DSL must be simple enough that an LLM generates it reliably with high layout variety, and the Python compiler must produce ADA-compliant HTML indistinguishable in quality from the current `/ada-slides-general` output.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Analyze ~20 existing HTML decks to derive the definitive set of layout primitives
- [ ] Define the YAML DSL schema (layout types, fields, sections, metadata)
- [ ] Build Python compiler: YAML DSL → standalone ADA-compliant HTML
- [ ] Handle LaTeX equations (compile to KaTeX/MathML in HTML)
- [ ] Handle Mermaid diagrams (compile to inline SVG)
- [ ] Handle SVG diagrams (embed directly)
- [ ] Handle images (JPEG/PNG — embed or reference)
- [ ] Enforce design rules in compiler (layout variety, bullet limits, alt text)
- [ ] Create Claude Code skill `/md_to_yaml` that generates YAML DSL from input content
- [ ] Skill follows design constraints (no 3 consecutive same layouts, visual rhythm, etc.)
- [ ] Support code blocks with syntax highlighting
- [ ] Support tables

### Out of Scope

- PowerPoint/PPTX export — HTML-only output
- Fine-tuning a local model on the DSL — future work
- Hook-based auto-compilation — future enhancement after core works
- Real-time preview/hot-reload — not needed for v1

## Context

- Existing working system: `/ada-slides-general` skill built on `/visual-explainer` produces good HTML decks but is token-expensive (generates full HTML) and occasionally has ADA violations
- ~20 existing HTML decks in `../n8n_to_python/output_html_files/` covering quantum transformers, quixer, clustering topics — these serve as ground truth for deriving primitives
- Current decks use: KaTeX for math, inline SVG for diagrams, dark theme with amber accents, scroll-snap navigation, ARIA labels, skip links
- Slide classes observed: `slide--title`, `slide--content`, `slide--diagram`, `slide--figure`, `slide--divider`
- Typical deck size: 25-55 slides, 30-90KB HTML
- The YAML DSL should be an order of magnitude smaller in tokens than equivalent HTML

## Constraints

- **ADA Compliance**: Output HTML must satisfy WCAG 2.1 AA — alt text, ARIA labels, color contrast, keyboard navigation, skip links
- **Deterministic Rendering**: Once YAML is produced, Python compiler output is fully deterministic — no LLM in the compilation step (v1)
- **Self-Contained HTML**: Output is a single HTML file with embedded CSS/JS (KaTeX loaded from CDN is acceptable)
- **Existing Quality Bar**: Output must match the visual quality and accessibility of current `/ada-slides-general` decks

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| YAML as DSL format | Easy to parse, familiar syntax, minimal nesting, LLM-friendly | — Pending |
| ~15 layout primitives | Balance expressiveness vs. LLM cognitive load; derive from existing deck analysis | — Pending |
| Python + Jinja2 for compiler | Deterministic, maintainable, handles MathML/SVG/Mermaid processing | — Pending |
| KaTeX over MathJax | Already used in existing decks, faster rendering | — Pending |
| No PPTX support | Simplifies architecture significantly; HTML-only covers the use case | — Pending |

---
*Last updated: 2026-03-21 after initialization*
