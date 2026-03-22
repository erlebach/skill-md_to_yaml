# Gap Report: Phase 01.1 Real-World DSL Validation

**Generated:** 2026-03-22
**Sprint:** Phase 01.1 — Real-World DSL Validation (Plans 01–03)
**Purpose:** Documents validation results across all 5 real-world decks; input for Phase 2 compiler planning.

---

## Decks Validated

| File | Slides | Status | Notable Patterns |
|------|--------|--------|------------------|
| `real_quantum_transformers_impl.yaml` | 8 | PASS | Heavy code blocks (2 × code), 2 × two-column, 2 × diagram SVGs |
| `real_quixer_implementation.yaml` | 11 | PASS | Dense diagram usage (4 × diagram), 2 × steps, comparison |
| `real_prototype_clustering_tutorial.yaml` | 27 | PASS | Figure raster images (5 ×), 3 × two-column with proportion variants, 2 × comparison |
| `real_density_clustering.yaml` | 16 | PASS | Proportion variant two-column (11 ×, dominant layout), 2 × diagram SVGs |
| `real_clustering_ch8_tutorial.yaml` | 30 | PASS | 9 × figure (heavy raster), formula-block content slides, img-row multi-image slides, comparison table |

**Total slides validated:** 92 across 5 decks
**All 5 decks:** Parse without errors via `parse_deck_file()`

---

## Layout Coverage

| Layout Type | Times Used | Decks Used In |
|-------------|-----------|---------------|
| `content` | 31 | clustering-ch8-tutorial (16), prototype-clustering (12), quixer (1), quantum-transformers (1), density-clustering (1) |
| `two-column` | 17 | density-clustering (11), prototype-clustering (3), quixer (1), quantum-transformers (2) |
| `figure` | 14 | clustering-ch8-tutorial (9), prototype-clustering (5) |
| `diagram` | 11 | quixer (4), quantum-transformers (2), prototype-clustering (2), density-clustering (2), clustering-ch8-tutorial (1) |
| `title` | 5 | All 5 decks (1 each) |
| `summary` | 4 | clustering-ch8-tutorial (1), prototype-clustering (1), quixer (1), density-clustering (1) |
| `steps` | 4 | clustering-ch8-tutorial (1), prototype-clustering (1), quixer (2) |
| `comparison` | 4 | clustering-ch8-tutorial (1), prototype-clustering (2), quixer (1) |
| `code` | 2 | quantum-transformers (2) |
| `hero` | 0 | — (none in real-world decks; reserved for section-opener slides) |
| `divider` | 0 | — (none; visual section breaks not used by LLM author in these decks) |
| `quote` | 0 | — (none; pull-quote layout not triggered by academic content) |

**All 9 used layout types validated across multiple decks. 3 layout types (hero, divider, quote) have zero usage in these 5 academic tutorial decks — this is expected; they are valid DSL types for other content genres.**

---

## Gaps Found

The following HTML patterns required judgment calls during conversion. Each entry documents the pattern, the DSL mapping decision, and any schema change made.

### 1. `formula-block` div elements

- **HTML pattern:** `<div class="formula-block" role="region" aria-label="...">` wrapping MathML or KaTeX math
- **Closest DSL type:** `content`
- **Decision:** Mapped to `layout: content` with the formula expressed as a `$$...$$` KaTeX block in the Markdown body. The `formula-block` is a rendering hint, not a structural type — the DSL body handles math via KaTeX pass-through.
- **Schema change:** None. `ContentSlide` body accepts arbitrary Markdown including `$$...$$` blocks.

### 2. `img-row` multi-image rows

- **HTML pattern:** `<div class="img-row" role="group" aria-label="...">` containing 2–4 `<img>` elements side by side
- **Closest DSL type:** `content` (when images accompany text) or `figure` (when a single image IS the slide)
- **Decision:** When an `img-row` contains 3–4 images serving as supplementary illustrations alongside explanatory text, mapped to `layout: content` with the image set described in prose body and a `notes:` field documenting the original images for compiler reference. When a single raster image IS the primary slide content (image-only slides), used `layout: figure`.
- **Schema change:** None. The notes field absorbs rendering metadata cleanly.

### 3. `chapter-label` / `step-tag` decorative elements

- **HTML pattern:** `<div class="chapter-label">` or `<p class="step-tag">` appearing above slide headings as section labels
- **Closest DSL type:** `notes` field on whichever layout the slide uses
- **Decision:** Dropped chapter labels as non-content decorations, or absorbed them into the slide `notes:` field. Per RESEARCH.md Pitfall 2: chapter labels are not significant content.
- **Schema change:** None.

### 4. `<table class="cluster-table">` accessibility tables

- **HTML pattern:** `<table class="cluster-table">` with `<caption>`, `<th scope="col">`, and multi-row content comparing two categories (e.g., "Helpful" vs "Watch outs")
- **Closest DSL type:** `comparison`
- **Decision:** Mapped to `layout: comparison` with left/right columns separated by `<!-- split -->`. The two-column nature of the table maps naturally to comparison layout. For tables with 3+ columns, `content` with a Markdown table in the body would be appropriate (none encountered in this sprint).
- **Schema change:** None. `ComparisonSlide` body handles `<!-- split -->` split marker correctly.

### 5. SVG inline diagrams

- **HTML pattern:** `<div class="svg-wrap"><svg role="img" aria-labelledby="...">` containing programmatically generated diagrams
- **Closest DSL type:** `diagram`
- **Decision:** Mapped to `layout: diagram` with comprehensive `alt_text` describing the SVG content semantically. Raw SVG excluded per RESEARCH.md Pitfall 3 — DSL bodies are Markdown; SVG is a compiler-rendered output. For Phase 2, the compiler will render Mermaid/programmatic SVGs from the diagram body or alt_text.
- **Schema change:** None. `DiagramSlide` was specifically designed for this pattern in Phase 01.

### 6. Multi-figure slides with `<figure>` + `figcaption`

- **HTML pattern:** Single `<figure class="slide-figure">` with `<img>` and `<figcaption>` as the entire slide content (no other body text)
- **Closest DSL type:** `figure`
- **Decision:** Mapped to `layout: figure` with `src` = image filename basename, `alt_text` from `<div class="sr-only">` description (preferred) or HTML `alt` attribute. Figcaption text placed in the Markdown body of the figure slide.
- **Schema change:** None. `FigureSlide` fields (`src`, `alt_text`, optional body) cover this pattern fully.

### 7. `caption:` field consideration

- **HTML pattern:** `<figcaption>` text below slide images
- **Closest DSL type:** Markdown body on `FigureSlide`
- **Decision:** Placed figcaption text in the `FigureSlide` Markdown body (after the frontmatter block). An optional `caption:` field was considered but not added — the body field serves the same purpose without schema proliferation.
- **Schema change:** None added. If the compiler needs to distinguish caption from body prose, a `caption:` field could be added to `FigureSlide` in Phase 2 (low priority).

---

## Schema Changes Made

**No schema changes were required across Plans 01–03.** All 12 layout types and their existing fields were sufficient to represent all HTML patterns encountered in the 5 real-world academic tutorial decks.

Summary of what was validated as sufficient without modification:

| Model | Fields Validated | Notes |
|-------|-----------------|-------|
| `FigureSlide` | `src`, `alt_text`, body | Covers single-image figure slides and figcaption text |
| `DiagramSlide` | `alt_text`, body | Covers inline SVG, programmatic diagrams |
| `TwoColumnSlide` | `proportion` (50/50, 40/60, 60/40) | All 3 proportion variants exercised |
| `ComparisonSlide` | body with `<!-- split -->` | Covers 2-column tables and pros/cons layouts |
| `ContentSlide` | body | Covers formula-block, img-row, textual content |
| `StepsSlide` | body | Covers ordered algorithm steps |
| `CodeSlide` | `language` | Covers syntax-highlighted code blocks |
| `SummarySlide` | body | Covers wrap-up slides with body content |

---

## DSL-01 Closure

- [x] All 5 real-world decks parse without errors via `parse_deck_file()`
- [x] 9 of 12 layout types exercised across the 5 fixtures (hero, divider, quote unused — expected for academic content)
- [x] FigureSlide exercises `alt_text` requirement (ADA field validated)
- [x] DiagramSlide exercises `alt_text` requirement (ADA field validated)
- [x] TwoColumnSlide exercises all 3 proportion variants (50/50, 40/60, 60/40)
- [x] All 5 decks pass `python3 -m pytest tests/test_real_world_decks.py -v` (10 tests)
- [x] Full test suite passes `python3 -m pytest tests/ -v`
- [x] REQUIREMENTS.md DSL-01 marked complete

**DSL-01 is CLOSED.** Phase 01.1 validation sprint complete.

---

## Phase 2 Planning Input

The following observations from validation are relevant to Phase 2 compiler design:

1. **Image path handling:** `src` fields use asset directory basenames (e.g., `deck-assets/_page_1_Figure_15.jpeg`). The compiler needs a configurable asset root or path resolution strategy.

2. **KaTeX pass-through:** 9 slides across 3 decks use `$$...$$` or `$...$` math. Compiler must emit KaTeX CDN auto-render script (confirmed preference from PROJECT.md decisions).

3. **Multi-image slides:** `img-row` patterns (3–4 images per slide) are currently mapped to `content` layout. Phase 2 could add a `gallery` layout type for grid rendering if needed — not required for v1.

4. **Caption vs. body distinction:** `FigureSlide` body currently holds figcaption text. If the compiler template needs to style captions distinctly from body prose, a `caption:` field on `FigureSlide` could be added (low priority, Phase 2 decision).

5. **`hero` and `divider` layouts:** Zero usage in 5 academic decks — compiler templates still required for completeness. These layouts will appear in general presentation decks.

6. **`quote` layout:** Zero usage in academic content — compiler template required. Expected to appear in keynote/opinion-style decks.
