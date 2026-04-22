# CSS Controls Reference

The **actively maintained** slide template for the **`md_to_yaml`** compiler is [`.claude/skills/md_to_yaml/compiler/templates/base.html.j2`](.claude/skills/md_to_yaml/compiler/templates/base.html.j2). A mirror may also exist as [`skills/deck-compile/compiler/templates/base.html.j2`](skills/deck-compile/compiler/templates/base.html.j2); if the two differ, treat the **`.claude/skills/md_to_yaml/`** file as source of truth for display-math, YAML-driven knobs, and recent layout fixes.

Most **figure scaling** is plain CSS in the `<style>` block (not only `:root` variables). Color tokens are defined in `:root[data-theme="dark" | "light"]`. A prose mirror (if present) is under `skills/deck-compile/compiler/templates/md/base.html.j2.md`; keep it in sync when you edit the template.

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

All font sizes use `clamp(min, fluid, max)`. Edit in the canonical `base.html.j2` (path at top of this doc):

| Selector | Size range | Used for |
|---|---|---|
| `h1` | `clamp(48px, 10vw, 96px)` | Title slide main heading |
| `h2` | `clamp(32px, 5vw, 52px)` | Content slide heading |
| `h3` | `clamp(22px, 2.8vw, 34px)` | Sub-heading |
| `.divider-slide h2` | `clamp(48px, 8vw, 80px)` | Section divider heading |
| `.slide-body` | `clamp(20px, 2.2vw, 28px)` | Bullet text / body |
| `.hero-description` | `clamp(22px, 2.8vw, 34px)` | Hero slide subtitle |
| `.hero-body` | `clamp(20px, 2.4vw, 30px)` | Hero slide body hook |
| `figcaption` | `clamp(18px, 1.8vw, 24px)` | Figure caption |
| `.table-scroll-wrapper th/td` | `clamp(18px, 1.9vw, 26px)` | Table cell text |
| `blockquote` | `clamp(28px, 3.5vw, 44px)` | Quote text |
| `pre`, `code` | `clamp(15px, 1.6vw, 20px)` | Code block text |

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

The deck template does not expose a single “`--figure-scale`” variable. **Scale** is **layout-specific**: the browser combines **`max-width` / `max-height`**, **`object-fit: contain`**, and (for Mermaid) **JavaScript** that fits SVG to an available box. You control it by **editing the relevant rules in `base.html.j2`**, or by adding a **downstream** `<style>` block in a post-processing step. Below is what is **controllable** in the stock template, grouped by slide layout.

### Common ideas

- **`vh` and `%`**: Values like `max-height: 62vh` tie the figure to the **viewport**; values like `max-height: 100%` tie it to a **parent** that already has a definite height (used inside flex or grid regions).
- **`object-fit: contain`**: When both width and height are capped, the image keeps **aspect ratio**; if the box is **short**, the content becomes **narrower** (it does not stay “full width” and overflow vertically).
- **Mermaid** (`mermaid` in a diagram container): after render, a script in `base.html.j2` **rewrites** SVG `width` / `height` / `style` using constants **`SLIDE_PAD`**, **`PANEL_INSET`**, and (for `layout: figure-wide`) **`FW_INSET`**, plus geometry from **`getBoundingClientRect()`**. To change Mermaid “fit” behavior, search that template file for `mermaid.run`, `sizeSvg`, and the `querySelectorAll` lines that end with `svg[id^="mermaid"]`.
- **Per-slide CSS**: Compiled slides use `<section id="...">` with a stable `id` per slide. You can target one slide in an override file with `#<slide_id> .figure-container img { ... }` (or the appropriate wrapper for that layout) without changing the global template.

### `layout: figure` (image / SVG in `.figure-container`)

| Control | Default (typical) | What to change |
|--------:|------------------|------------------|
| Image max width / height | `max-width: 80%`, `max-height: 62vh` on `.figure-container img` | Tighten or relax caps; or use `max-width: 100%` to favor width until height wins. |
| **Figure-only** (no `body` on the slide) | `.figure-only .figure-container img` uses **`90%` / `68vh`**; figure padding is larger | Edit `.figure-only` rules. |
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
| **Display math** scale / center / color (YAML) | deck or slide `.yaml` | `math_display_scale`, `math_display_center`, `math_display_color` |
| **Display math** (CSS / HTML) | `.claude/skills/md_to_yaml/compiler/templates/base.html.j2` | `Display equations ($$...$$)`, `--math-display-scale`, `--math-display-color`, `math-display-eq-center`, `math[display="block"]` |
| Slide frame (color) | `base.html.j2` | `--border` on `section[role="group"]` |
| Frame thickness | same | `section[role="group"] { border: ...` |
| Accent color (per-deck) | deck `.yaml` metadata | `accent_color:` |
| Theme (dark/light) | deck `.yaml` metadata | `theme:` |
| Font | deck `.yaml` metadata | `font:` |
| Figure panel **colors** | same | `--fig-panel`, `--fig-panel-border` |
| Body font size | same | `.slide-body` clamp |
| Slide padding (incl. bottom **1in** “margin”) | same | `section[role="group"] { padding` |
| **Figure / image / SVG scale** | same | [Figure scale adjustments](#figure-scale-adjustments), or search: `.figure-container img`, `figure-wide`, `.two-col img`, `diagram-container`, `mermaid.run` |
| Two-column **column widths** | same | `two-col-50-50` / `40-60` / `60-40` and YAML `proportion:` |
| Two-column **image height** caps | same | `.two-col img`, `.two-col-both img` (currently **`60vh` / `55vh`**) |
| **Figure-wide** flex and panel | same | `slide-figure-wide`, `figure-wide-figure-wrap`, `figure-wide-below` |
| **Mermaid** fit insets (script) | same | `SLIDE_PAD`, `PANEL_INSET`, `FW_INSET` |
