# CSS Controls Reference

The **actively maintained** slide template for the **`md_to_yaml`** compiler is [`.claude/skills/md_to_yaml/compiler/templates/base.html.j2`](.claude/skills/md_to_yaml/compiler/templates/base.html.j2). A mirror may also exist as [`skills/deck-compile/compiler/templates/base.html.j2`](skills/deck-compile/compiler/templates/base.html.j2); if the two differ, treat the **`.claude/skills/md_to_yaml/`** file as source of truth for display-math, YAML-driven knobs, and recent layout fixes.

Most **figure scaling** is plain CSS in the `<style>` block (not only `:root` variables). For **`layout: figure`**, **`section[role="group"].slide-figure`** is clamped to **one** **`100vh`** screen with **`overflow: hidden`** (only the **section** clips to the viewport). **`.slide-content-area`**, **`.figure-container`**, and **`<figure>`** use **`overflow: visible`** so **`zoom`** / **`transform: scale`** on **raster / file SVG** does **not** get **clipped** by intermediate flex wrappers. There is **extra** **`padding-bottom: calc(1in + var(--slide-footer-ui-clearance))`** to keep content out of the **fixed** **`.slide-footer-nav`** band. The **--fill** **panel** has **no** **`max-height: 100%`** on the flex chain (that + **`min(80vh, 100%)`** had **indefinite** **%** bases and caused **left/bottom** **clipping**). **--fill** **media** use **`max-height: 80vh`** (or **85vh** figure-only) plus **`zoom`** or **`transform`**. Color tokens: `:root[data-theme="dark" | "light"]`. A prose mirror (if present) is under `skills/deck-compile/compiler/templates/md/base.html.j2.md`.

---

## Theme selection

Set via the `theme:` key in deck YAML metadata (`dark` or `light`).

```yaml
---
title: My Deck
theme: dark   # or: light
```

---

## CSS Custom Properties

### Color tokens (both themes)

| Variable | Dark default | Light default | Purpose |
|---|---|---|---|
| `--bg` | `#0d1117` | `#ffffff` | Slide background |
| `--bg2` | `#161b22` | `#f6f8fa` | Secondary background (code blocks, etc.) |
| `--text` | `#e6edf3` | `#1f2328` | Body text |
| `--muted` | `#8b949e` | `#656d76` | Subdued text (captions, attribution, hero description) |
| `--accent` | `#f0a500` | `#b06800` | Headings (h2), bold/emphasis, step numbers, table header text |
| `--border` | `#30363d` | `#d1d9e0` | Internal separators **and** the **2px border around each slide** (`section[role="group"]`) |
| `--fig-panel` | `#1e2330` | `#eef1f5` | Panel background behind figures, diagrams, and tables |
| `--fig-panel-border` | `#2d3548` | `#d0d7de` | Border around figure/diagram/table panels |
| `--font-family` | *(set from `font:` metadata)* | | Font stack |

*Note: Figure **size** (max width/height) is not one of these tokens — it is set by layout-specific rules in the same `base.html.j2` `<style>` block. See [Figure scale adjustments](#figure-scale-adjustments) below.*

### Override accent color from YAML

You can override `--accent` per-deck without editing the template:

```yaml
---
title: My Deck
theme: dark
accent_color: "#3b82f6"   # any CSS color
```

---

## Title vs content typography (`title_scale` / `content_scale`)

Split **heading-band** text from **body-band** text without editing CSS. **Deck defaults** live in the **first** YAML metadata block; optional **per-slide** keys **replace** the deck value on that slide only (they do **not** multiply together).

### YAML (deck metadata — defaults)

| Key | Default | What it does |
|-----|--------|--------------|
| `title_scale` | `1.0` | `float` **0.75–4.0** — multiplier for titles, heading stacks, `h2`/`h3`, quote-block heading scale, comparison column headings, transcribe/transcript **headings**, and **hero** text (`.hero-description`, `.hero-body`). Combined with baseline `--font-scale` in the template. |
| `content_scale` | `1.0` | `float` **0.75–4.0** — multiplier for body prose, title-slide **author** line, `figcaption`, `blockquote`, `pre`/`code`, table panel text, figure-wide **summary**, transcribe/transcript **body**, and transcript-flavor table text. Combined with `--font-scale`. |

### YAML (slide frontmatter — optional overrides)

| Key | Default | What it does |
|-----|--------|--------------|
| `title_scale` | *(omit)* | If set, **replaces** deck `title_scale` for this slide only. |
| `content_scale` | *(omit)* | If set, **replaces** deck `content_scale` for this slide only. |

Use **top-level** keys (same indent as `layout:` / `title:`).

```yaml
---
title: My Deck
theme: dark
title_scale: 1.2
content_scale: 1.1
---
```

```yaml
---
layout: content
title: "Dense slide"
content_scale: 0.95
---
```

### CSS (`base.html.j2`)

| Variable | Source | Purpose |
|----------|--------|---------|
| `--font-scale` | Hard-coded in `:root` (`1.35`) | Global baseline for slide typography. |
| `--title-scale` / `--content-scale` | Inline on each **`<section>`** (compiler: effective deck-or-slide value) | Per-slide resolved multipliers. |
| `--title-font-mul` | On **`section[role="group"]`**: `calc(var(--font-scale) * var(--title-scale))` | Applied to **title** selectors. |
| `--content-font-mul` | On **`section[role="group"]`**: `calc(var(--font-scale) * var(--content-scale))` | Applied to **content** selectors. |

Typography rules use `font-size: calc(<clamp> * var(--title-font-mul))` or `var(--content-font-mul)`.

### Interaction with display math

Block `$$...$$` uses `font-size: calc(1em * var(--math-display-scale, 1))` relative to the parent. Body math therefore tracks **`content_scale`** (via `.slide-body` / table cell `em`). Hero math tracks **`title_scale`** when it sits under `.hero-body` / `.hero-description`. Tune **`math_display_scale`** if the combined effect is too large or small.

---

## Figure slide scale (`figure_scale`)

For **`layout: figure`** only. The compiler sets **`--figure-scale`** on the slide **`<section>`** (deck default **0.25–4.0**, optional per-slide override). **Behavior depends on media type** (see below). Does **not** apply to **`layout: figure-wide`**, two-column figures, or bare **`layout: diagram`** (edit CSS for those).

### YAML

| Where | Key | Default | What it does |
|-------|-----|--------|--------------|
| Deck metadata | `figure_scale` | `1.0` | `float` **0.25–4.0** — default for figure layout. |
| `layout: figure` frontmatter | `figure_scale` | *(omit)* | If set, **replaces** deck `figure_scale` for that slide. |

### Non-Mermaid rasters and file SVG (`figure-asset-wrap--fill`)

When the slide is **not** rendered as Mermaid (e.g. **`.jpeg`**, **`.png`**, **`.svg`** file), [`figure.html.j2`](.claude/skills/md_to_yaml/compiler/templates/figure.html.j2) adds **`figure-asset-wrap--fill`** on **`.figure-asset-wrap`**. The **panel** uses the same **`--fig-panel`** / **`--fig-panel-border`** tokens. On **`section.slide-figure`**, the **--fill** **panel** is **widened** by **½** **in** on **each** **side**: **`width: calc(100% + 1in); margin-left: -0.5in; margin-right: -0.5in;`** (extends into the slide’s **1in** **padding**), so the **white/panel** **box** is **1** **in** **wider** than the main **content** **column** **(no** Mermaid; **Mermaid** keeps **shrink-wrapped** **fit** **width** **)**.

**`<img>`** and file **`.diagram-container svg`** under **`--fill`** use **`max-height: 80vh`** (or **85vh** on **figure-only**), **`object-fit: contain`**, and **`zoom: var(--figure-scale, 1)`** when supported, else **`transform: scale`**. **File** **SVGs** also use **`width: auto; max-width: 100%`** (not **`width: 100%`**) with **`display: block; margin: 0 auto`**, so the **replaced** element can **shrink to aspect** and **center** in the **panel**; if the art still **looks** **shifted** **inside** the **bitmap**, **tighten** the **`viewBox`** in the **.svg** so **ink** is **balanced** in user space. The **`.figure-asset-wrap--fill`** **panel** uses **`overflow: visible`**; **`section.slide-figure`** has **`padding-bottom: calc(1in + var(--slide-footer-ui-clearance, 2.75rem))`**. In Firefox, **`transform: scale`** + **flex**-center the **image** and **`.diagram-container`**.

### Mermaid and inline non-file SVG (no `figure-asset-wrap--fill`)

**Mermaid** slides use **`width: fit-content`** (and **max-width** `min(100%, calc(88% * var(--figure-scale, 1)))` on **`.figure-asset-wrap`**) so the **panel** hugs the diagram. **`.diagram-container svg`** (and generic img rules **without** **`--fill`**) still use **`calc(72vh * var(--figure-scale, 1))`** (or **`78vh`** for **figure-only** when the **`img`** is **not** under **`--fill`**). After **`mermaid.run()`**, a script in **`base.html.j2`** calls **`sizeSvgFit`** (not the font-clamped **`sizeSvg`**) for **`layout: figure`**, using **viewport**-derived **width/height** and **`--figure-scale`**, not a near-zero **`.figure-asset`** box.

### CSS variable

**`--figure-scale`** is set on **`<section>`** only for **`layout: figure`**. All **`var(--figure-scale, 1))`** fallbacks in the stylesheet are for safety on other layouts.

### Debug: panel vs graphic box model

Set **`figure_layout_debug: true`** in **deck** metadata (first YAML block). The compiled HTML sets **`data-deck-figure-layout-debug="true"`** on **`<html>`** and adds CSS only in that mode:

| Outline | Element | Notes |
|--------|---------|--------|
| **Outer red border** | **`section.slide-figure .figure-asset-wrap`** | **Panel** (same element that carries **`--fig-panel`** background); **`margin: 14px`**, **`box-sizing: border-box`**. |
| **Inner red border** | **`.figure-asset > img`**, or **`.figure-asset .diagram-container`** (Mermaid / SVG) | The **graphic** (raster or diagram box). |

Turn debug off for normal output: remove **`figure_layout_debug`** from YAML (or set **`false`**) **and** do not pass **`--figure-layout-debug`** on the compiler CLI.

**CLI (no YAML edit):** `python3 -m compiler deck.yaml out.html --figure-layout-debug` — same red borders; combines with OR against YAML (`true` if either is on).

---

## Display math (block `$$...$$`)

Block display equations use **MathML** from the `latex2mathml` pipeline (not KaTeX). The compiler can inject **per-deck and per-slide** options from YAML; each **`<section>`** then carries **inline** custom properties and alignment classes. Template: **`.claude/skills/md_to_yaml/compiler/templates/base.html.j2`** (search: **`Display equations`**, **`math-display-eq-`**, **`--math-display-`**).

### YAML (deck metadata and slide frontmatter)

| Key | Default | What it does |
|-----|--------|--------------|
| `math_display_scale` | `1.0` (deck) | `float` in ~**0.75–2.0** — multiplier for `$$...$$` font size vs slide body `em`. |
| `math_display_center` | `true` (deck) | If **true**, block math is centered (with **`.math-display-eq-center`** on the section). If **false**, **`.math-display-eq-start`** (aligned with body text). |
| `math_display_color` | *(omit)* | Optional CSS `color` for block `$$...$$` only (e.g. `cyan`, `#6cf`, `hsl(180, 80%, 60%)`). Omitted = no extra tint (**`inherit`** body). Validated: no `;`, `url()`, braces, or angle brackets in the value. |

Use **top-level** keys in each slide’s frontmatter (same indent as `layout:` / `title:`). **Omit** or **`null`** on a slide to inherit the deck; deck **omit** for color means “no `--math-display-color` on the section.”

```yaml
# Deck-wide (first frontmatter block)
title: My Deck
math_display_scale: 1.1
math_display_center: true
math_display_color: cyan
```

```yaml
# Per slide (optional)
---
layout: content
title: "Derivation"
math_display_scale: 1.2
math_display_color: "#9cf"
---
```

### CSS on each slide (`<section>`)

| Mechanism | Set by | Purpose |
|----------|--------|---------|
| `style="--math-display-scale: <float>; …"` | Compiler (always) | Drives `font-size: calc(1em * var(--math-display-scale, 1))` on block `math[display="block"]` in **`.slide-body`**, **`.hero-body`**, **`.hero-description`**. |
| `style="… --math-display-color: <color>;"` | Compiler (when `math_display_color` is set) | Drives `color: var(--math-display-color, inherit)` on block math in **body / hero** and in **`section.slide-table` `td` / `th`**. |
| Class **`math-display-eq-center`** or **`math-display-eq-start`** | Compiler from `math_display_center` | Centering uses `width: fit-content`, `max-width: 100%`, and `margin: auto` on block math, plus flex on **`p`** that wrap only a block `math` when the parser emits that pattern. **Table** slides: extra rules for **`td` / `th`**. |

To change **how** centering or color apply (e.g. only centered mode), edit the **Display equations** comment block in **`base.html.j2`**. There is no separate YAML key for `$$` **inline** math color (that follows body / emphasis rules).

---

## Slide frame

In the current template, the frame uses **`--border`**. It is applied to every `section[role="group"]`:

```css
section[role="group"] {
  border: 2px solid var(--border);
}
```

To change **thickness**, edit that `border` line in the canonical `base.html.j2` (see the first paragraph of this document). To make the **frame** stand out from inner borders, you can introduce a dedicated token (e.g. `--slide-frame`) in `:root` and point `section[role="group"]` at it.

---

## Typography scale (clamp values)

All slide font sizes use `clamp(min, fluid, max)` **multiplied** by **`var(--title-font-mul)`** or **`var(--content-font-mul)`** (see [Title vs content typography](#title-vs-content-typography-title_scale--content_scale)). The table below is the **base clamp** before those multipliers. Edit the clamps and the `--font-scale` baseline in the canonical `base.html.j2` (path at top of this doc).

| Selector | Size range | Used for | Band |
|---|---|---|---|
| `h1` | `clamp(48px, 10vw, 96px)` | Title slide main heading | title |
| `h2` | `clamp(32px, 5vw, 52px)` | Content slide heading | title |
| `h3` | `clamp(22px, 2.8vw, 34px)` | Sub-heading | title |
| `.divider-slide h2` (via stack) | `clamp(48px, 8vw, 80px)` | Section divider heading | title |
| `.slide-body` | `clamp(20px, 2.2vw, 28px)` | Bullet text / body | content |
| `.hero-description` | `clamp(22px, 2.8vw, 34px)` | Hero band (grouped with titles) | title |
| `.hero-body` | `clamp(20px, 2.4vw, 30px)` | Hero band (grouped with titles) | title |
| `figcaption` | `clamp(18px, 1.8vw, 24px)` | Figure caption | content |
| `.table-scroll-wrapper th/td` | `clamp(18px, 1.9vw, 26px)` | Table cell text | content |
| `blockquote` | `clamp(28px, 3.5vw, 44px)` | Quote text | content |
| `pre`, `code` | `clamp(15px, 1.6vw, 20px)` | Code block text | content |

Heading stacks (`.slide-heading-stack--title` / `--standard` / `--divider`), quote block chrome, comparison **strong** headings, transcribe/transcript modes, and figure-wide summary use the same pattern; search **`base.html.j2`** for **`--title-font-mul`** and **`--content-font-mul`**.

---

## Slide padding

```css
section[role="group"] {
  padding: 1in;   /* edit here to tighten or loosen the slide margin */
}
```

---

## Figure / diagram panels (chrome only)

Panels (the rounded box behind figures and diagrams) use **color** tokens. **Edge radii and padding** are hard‑coded in `base.html.j2` (varies by layout — e.g. `layout: figure` vs `layout: figure-wide` vs diagram columns). Search the template for `figure-container`, `figure-wide-figure-wrap`, and `slide-diagram`.

For **how large the graphic is drawn** (scaling), read [Figure scale adjustments](#figure-scale-adjustments) — that is separate from panel colors.

---

## Figure scale adjustments

**`layout: figure`** exposes YAML **`figure_scale`** (deck default + optional per-slide override), which sets **`--figure-scale`** on the slide **`<section>`** and scales the **max-width** / **max-height** caps for raster images and for **SVG** inside that layout’s `.figure-container` (see [Figure slide scale](#figure-slide-scale-figure_scale)). Other layouts remain **layout-specific**: the browser combines **`max-width` / `max-height`**, **`object-fit: contain`**, and (for Mermaid) **JavaScript** that fits SVG to an available box. You can still edit **`base.html.j2`** or add a downstream `<style>` block. Below is what is **controllable** in the stock template, grouped by slide layout.

### Common ideas

- **`vh` and `%`**: Values like `max-height: 62vh` tie the figure to the **viewport**; values like `max-height: 100%` tie it to a **parent** that already has a definite height (used inside flex or grid regions).
- **`object-fit: contain`**: When both width and height are capped, the image keeps **aspect ratio**; if the box is **short**, the content becomes **narrower** (it does not stay “full width” and overflow vertically).
- **Mermaid** (`mermaid` in a diagram container): after render, a script in `base.html.j2` **rewrites** SVG `width` / `height` / `style` using constants **`SLIDE_PAD`**, **`PANEL_INSET`**, and (for `layout: figure-wide`) **`FW_INSET`**, plus geometry from **`getBoundingClientRect()`**. To change Mermaid “fit” behavior, search that template file for `mermaid.run`, `sizeSvg`, and the `querySelectorAll` lines that end with `svg[id^="mermaid"]`.
- **Per-slide CSS**: Compiled slides use `<section id="...">` with a stable `id` per slide. You can target one slide in an override file with `#<slide_id> .figure-container img { ... }` (or the appropriate wrapper for that layout) without changing the global template.

### `layout: figure` (image / SVG in `.figure-container`)

| Control | Default (typical) | What to change |
|--------:|------------------|------------------|
| **YAML `figure_scale`** | `1.0` at deck; optional per-slide override | Scales the **effective** `%` / `vh` caps via **`--figure-scale`** (see [Figure slide scale](#figure-slide-scale-figure_scale)). |
| Image max width / height | `max-width: 80%`, `max-height: 62vh` × scale on `.slide-figure .figure-container img` | Edit base percentages in `base.html.j2` or tune YAML `figure_scale`. |
| **Figure-only** (no `body` on the slide) | `.figure-only` uses **`90%` / `68vh`** × scale | Edit `.slide-figure.figure-only` rules or YAML. |
| Diagram **SVG** in figure | `max-height: 52vh` × scale under `.slide-figure .figure-container .diagram-container svg` | Same. |
| Inline `figure` box | `figure` has `display: inline-block` and `max-width: 100%` | Affects how the light panel shrinks; rarely needs tuning. |

### `layout: figure-wide` (summary + panel + bottom columns, smart flex)

This layout is designed so the **figure area shrinks** when **title, optional top summary, and footer (`.figure-wide-below`)** need more vertical space, while the slide stays within **`100vh`** and the slide **`padding: 1in`**.

| Mechanism | Role |
|----------|------|
| `section.slide-figure-wide` | **`height` / `max-height: 100vh`**, **`overflow: hidden`** — one screen; no unbounded growth. |
| `.figure-wide-layout` + `.figure-wide-figure-wrap` | **Column flex** with **`min-height: 0`**; the **wrap** (`flex: 1`) is the only region that **competes** for leftover height between summary and footer. |
| `.figure-wide-below` | **`flex: 0 0 auto`** — footer **does not shrink**; the figure region yields space first. |
| `.figure-wide-media` + `img` / `svg` | **`max-width: 100%`**, **`max-height: 100%`**, **`object-fit: contain`** — when the panel is **short**, the graphic **scales down**; width is **not** held at 100% if height is the limit. |
| Mermaid in this layout | **Extra** `forEach` after `mermaid.run` sizes SVG to **`.figure-wide-figure-wrap`** bounds (minus padding and **figcaption** if present), using `FW_INSET` (~`40` px) in the script. |

**What you can turn without redesign**

- **Gap** between blocks: `.figure-wide-layout { gap: 1rem; }`
- **Panel padding** around the figure: `.figure-wide-figure-wrap { padding: ... }` (smaller padding slightly increases the drawable area).
- **Mermaid inset**: constant **`FW_INSET`** in the `figure-wide` mermaid `forEach` (smaller = slightly more usable width/height for the graph).
- **Cap the panel width** (e.g. center a narrower diagram): e.g. ` .figure-wide-figure-wrap { max-width: 70%; margin-left: auto; margin-right: auto; }` — the flex height logic still applies.

There is **no** YAML key for `figure_scale`; behavior is **template CSS + optional slide-level overrides**.

### `layout: diagram` and two-column diagram columns

- **Global** fallbacks: `.diagram-container` has `max-height: 75vh`; **generic** `.diagram-container svg` uses **`max-height: 52vh`** unless a more specific rule wins.
- **`.diagram-only`**: larger caps (`80vh` / `75vh` for container / svg) when the diagram is alone on the slide.
- **`.slide-two-column .diagram-container`**: panel styling and flex; Mermaid is sized in JS to the **column** `getBoundingClientRect().width` and a viewport-derived height.
- Tweak **`52vh` / `75vh`** in `base.html.j2` if standalone diagrams should feel larger or smaller **without** using the figure-wide flex stack.

### Two-column slides (raster images in `.two-col img`)

| Rule | Default | Notes |
|------|---------|--------|
| Single image in a column | `max-width: 100%`, `max-height: 60vh`, `object-fit: contain` | Static viewport cap, not a CSS variable. |
| `.two-col-both img` (both columns are figures) | `max-height: 55vh` | Slightly shorter when two images compete. |

To change “how big” two-column images are, **edit these `max-height` values** in `base.html.j2` (or override with a per-deck style).

---

## Table panels

```css
.table-scroll-wrapper {
  background: var(--fig-panel);
  border: 1px solid var(--fig-panel-border);
  border-radius: 10px;
  padding: 1rem 1.5rem;
}
```

---

## Mermaid (fonts and diagram-type sizing)

**SVG pixel size** (how large the graph appears) is a combination of the CSS rules in [Figure scale adjustments](#figure-scale-adjustments) and the **post-`mermaid.run()`** JavaScript (slide diagram, two-column, or figure-wide), which call `sizeSvg` / `sizeSvgFit` / `sizeSvgFillWidth` with measured boxes.

**Label font size** in the Mermaid config is set in the embedded script (`mermaid.initialize({...})` — e.g. `fontSize: '22pt'`), with an internal min/max **scale** band (`NATURAL_PT`, `MIN_PT`, `MAX_PT` in the same script) so cell labels stay readable when the SVG is fitted.

---

## Code blocks

```css
pre {
  max-height: 70vh;   /* scroll kicks in beyond this */
  font-size: clamp(15px, 1.6vw, 20px);
}
.slide-code { max-height: 75vh; }
```

---

## Two-column proportions

Set via `proportion:` in YAML slide frontmatter:

```yaml
proportion: 60/40   # left 60%, right 40%
proportion: 40/60
proportion: 50/50   # default
```

CSS grid templates in `base.html.j2`:

```css
.two-col-50-50 { grid-template-columns: 1fr 1fr; }
.two-col-40-60 { grid-template-columns: 2fr 3fr; }
.two-col-60-40 { grid-template-columns: 3fr 2fr; }
```

**Image scale** in two-column slides is not proportional to the column split; it is controlled by **`max-height` on `.two-col img`** and **`.two-col-both img`** (see [Figure scale adjustments](#figure-scale-adjustments) → *Two-column*). Wider/narrower columns only change the **width** available before the `max-height` cap kicks in.

---

## Print output

Print styles force landscape layout with each slide on its own page. Controlled by `@media print` in `base.html.j2`. No user-facing knobs; edit the block directly if needed.

---

## Summary: where to edit

| What you want to change | File | What to search for |
|---|---|---|
| **Title / content** typography (YAML) | deck metadata + optional slide frontmatter | `title_scale`, `content_scale` (slide values **replace** deck) |
| **Title / content** (CSS) | `base.html.j2` | `--title-scale`, `--content-scale` on `<section>`; `--title-font-mul`, `--content-font-mul` |
| **`layout: figure` scale (YAML)** | deck metadata + optional `layout: figure` slide | `figure_scale` (slide value **replaces** deck) |
| **`layout: figure` scale (CSS)** | `base.html.j2` | `--figure-scale`, `.slide-figure .figure-container` |
| **Figure panel vs graphic debug borders** | deck `.yaml` metadata | `figure_layout_debug: true` → `data-deck-figure-layout-debug` on `<html>` |
| **Display math** scale / center / color (YAML) | deck or slide `.yaml` | `math_display_scale`, `math_display_center`, `math_display_color` |
| **Display math** (CSS / HTML) | `.claude/skills/md_to_yaml/compiler/templates/base.html.j2` | `Display equations ($$...$$)`, `--math-display-scale`, `--math-display-color`, `math-display-eq-center`, `math[display="block"]` |
| Slide frame (color) | `base.html.j2` | `--border` on `section[role="group"]` |
| Frame thickness | same | `section[role="group"] { border: ...` |
| Accent color (per-deck) | deck `.yaml` metadata | `accent_color:` |
| Theme (dark/light) | deck `.yaml` metadata | `theme:` |
| Font | deck `.yaml` metadata | `font:` |
| Figure panel **colors** | same | `--fig-panel`, `--fig-panel-border` |
| Body font size | same | `.slide-body` clamp × `--content-font-mul`; YAML `content_scale` |
| Heading / hero band size | same | `h1`–`h3`, stacks, hero × `--title-font-mul`; YAML `title_scale` |
| Slide padding (incl. bottom **1in** “margin”) | same | `section[role="group"] { padding` |
| **Figure / image / SVG scale** | same | [Figure scale adjustments](#figure-scale-adjustments), or search: `.figure-container img`, `figure-wide`, `.two-col img`, `diagram-container`, `mermaid.run` |
| Two-column **column widths** | same | `two-col-50-50` / `40-60` / `60-40` and YAML `proportion:` |
| Two-column **image height** caps | same | `.two-col img`, `.two-col-both img` (currently **`60vh` / `55vh`**) |
| **Figure-wide** flex and panel | same | `slide-figure-wide`, `figure-wide-figure-wrap`, `figure-wide-below` |
| **Mermaid** fit insets (script) | same | `SLIDE_PAD`, `PANEL_INSET`, `FW_INSET` |
