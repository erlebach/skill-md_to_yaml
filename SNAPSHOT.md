# Project Snapshot

**Last updated:** 2026-05-06 14:18 (local)

## Current Architecture

- **YAML DSL compiler**: `compiler/` — Jinja2-based engine rendering YAML slide decks to self-contained HTML
- **Schema/Parser**: `schema/` — validates hybrid YAML+Markdown deck files
- **Skill definitions**: `docs/transcribe_to_html/`, `docs/md_to_yaml/`; repo skills under **`skills/`** — **`deck-compile`** (bundled compiler), **`deck-author`**, **`figure-spec`** (each has `SKILL.md` + **`USAGE.md`**); **`create_figure_captions`** if present
- **Templates**: `compiler/templates/` — Jinja2 HTML templates per layout type (title, content, figure, table, etc.)
- **Renderers**: `compiler/renderers/` — Python modules for math, code, images, Markdown processing

## Active Features

- **In-page view scale** — **`view_scale`** (default **1.0**, range **0.25–4**) and optional **`remember_view_scale`** on **`DeckMetadata`**; HTML **`#deck-app-root`** applies **`--deck-view-scale`** (**`zoom`**, **`transform`** fallback). **Fixed bottom bar** (slide counter, view-scale, go-to): **`footer_inset`** (default **`0.5in`**) = CSS **`bottom`**; **`footer_scale`** (**0.5–2.5**, default **1.0**) = **`--footer-scale`** on **`<html>`** for larger/smaller control chrome; **`--slide-footer-ui-clearance`** scales with **`footer_scale`**. See **`CSS_CONTROLS.md`** (Fixed footer). Keys **`+`/`=`**, **`−`**, **`0`**, **`?viewScale=`**, **`localStorage`** **`mdToYamlDeckViewScale`** (see **`HANDOFF_ZOOM.md`**).
- **Display math tuning** — deck metadata and per-slide frontmatter: **`math_display_scale`** (**0.75–2.0**, default **1.0**), **`math_display_center`** (default **true**), and optional **`math_display_color`** (e.g. **`cyan`**, hex, **`hsl(...)`**) for **`$$...$$`** block MathML in body, hero, and table cells; HTML sets **`--math-display-scale`**, optional **`--math-display-color`**, and **`math-display-eq-center`** / **`math-display-eq-start`** on each **`<section>`** (under **`.claude/skills/md_to_yaml`**). When centering is on, block MathML also uses **`width: fit-content; max-width: 100%`** with **`margin: auto`** so bare **`<math>`** between paragraphs still centers.
- **Slide `subtitle`** — optional on all layouts that have **`title`**; rendered below the heading with **80%** of the title font size (CSS **`0.8em`** on **`header.slide-heading-stack`**); rich text / inline math like **`title`**
- **`transcribe_to_html`** — transcript decks: dense left-aligned body text via `flavor: transcript`
- **`md_to_yaml`** — pedagogical decks with `explanatory`, `implementation`, `tutorial` flavors (content tone; standard presentation metadata)
- **`create_figure_captions`** — from any slide-deck YAML, propose 3–4 figures and Nano Banana–style image captions → `suggested_figures.md` (no API; prompt-native)
- **Image embedding** — `--embed-images` flag for base64 data URI embedding
- **13 layout types**: title, hero, content, divider, figure, diagram, two-column, quote, comparison, code, steps, summary, table (+ legacy `transcribe`)
- **Math rendering** — **latex2mathml** MathML: **`$$...$$`** block and **`$...$`** inline math
- **ADA compliance** — required `alt_text` on figures/diagrams, contrast validation
- **Declarative bullet animation (md_to_yaml)** — deck **`animation_defaults.bullet_stagger`** (optional partial **`BulletStaggerSettings`**) merges with skill defaults in **`schema/animation_defaults.py`**, then per-slide **`bullet_animation`**: **`true`**, **`stagger`**, or partial **`BulletStaggerSettings`** on **`layout: content`** and **`layout: transcribe`**. Compiler sets **`data-bullet-stagger`** on **`<section>`** and emits one GSAP block when **`has_bullet_animation`**. Optional **`gsap_script_url`** on deck metadata (**https** only).

## Documentation

- **[`.claude/skills/md_to_yaml/FIGURE_WIDE.md`](.claude/skills/md_to_yaml/FIGURE_WIDE.md)** — **`layout: figure-wide`**: flex band, **`figure_scale`** (**`zoom`** / **`transform: scale`**), pitfalls, YAML sketch; cross-linked from **[`CSS_CONTROLS.md`](CSS_CONTROLS.md)** and **`SKILL.md`**.

## File Structure

```text
md_to_yaml/
├── compiler/           # YAML→HTML compilation engine
│   ├── engine.py       # Main compile_deck() and _render()
│   ├── renderers/      # Math, code, image, Markdown renderers
│   ├── templates/      # Jinja2 HTML templates per layout
│   └── validators.py   # Layout, accessibility, bullet-count checks
├── schema/             # Deck YAML parsing and validation
│   └── parser.py       # parse_deck_file()
├── block_encoding/     # Source notes + co-located deck outputs (YAML/HTML)
├── quantum_channels/   # Source notes + co-located deck outputs (YAML/HTML)
├── quantum_shots/      # Shots / accuracy / NISQ notes + co-located deck outputs
├── quantum_transformer/   # Guo quantum transformer notes + co-located deck outputs
├── quantum_transformer_inference/  # Inference-focused outline + seminar decks (YAML/HTML)
├── quantum_measurements/  # Measurement / observables / bases notes + co-located deck outputs
├── realistic_quantum_advantage/  # Honest QML wall-clock notes + co-located deck outputs
├── docs/               # Skill documentation mirrors (md_to_yaml, transcribe_to_html); **plans/** and **tasks/** for agent-authored plans and task files
│   ├── tasks/          # e.g. `split-three-skills-tasks.md` (T1–T5, dependency graph)
│   ├── plans/          # Canonical plan markdown (e.g. split into deck-author / deck-compile / figure-spec); see README inside
│   ├── transcribe_to_html/
│   └── md_to_yaml/
├── skills/             # Repo-local agent skills (symlinked from `.claude/skills/` for deck-*)
│   ├── deck-compile/   # Vendored compiler + schema; USAGE.md, SKILL.md
│   ├── deck-author/    # IR authoring; USAGE.md, SKILL.md
│   ├── figure-spec/    # Figure briefs; USAGE.md, SKILL.md
│   └── create_figure_captions/  # if present
├── conversion_full/    # Full-document transcriptions
├── conversion/         # Partial/page-range conversions
├── conversion_results/ # Survey and other conversion outputs
├── examples/           # Small demo decks (e.g. GSAP bullet animation sample YAML)
└── polylog/            # Polylog scaling notes; matplotlib scripts + SVG figures
```

## Recent Changes

- **2026-05-06**: **Global ADA rule** — added `~/.cursor/rules/ADA.mdc` to codify
  scroll-invariant measurement practices (avoid viewport `bottom/top` for
  offscreen sizing; prefer container-based sizing).
- **2026-05-06**: **Figure Mermaid sizing (offscreen fix)** — figure-slide Mermaid
  sizing no longer depends on `getBoundingClientRect().bottom` (which varies for
  offscreen slides in scroll-snap). This prevents diagrams only sizing correctly
  after a zoom/interaction forces relayout.
- **2026-05-06**: **Sequence diagram sizing** — Mermaid v11 `sequenceDiagram`
  now prefers deterministic **fit-to-panel** scaling (BBox/viewBox), avoiding
  unreliable text-metric-based scaling for this diagram type.
- **2026-05-06**: **Mindmap lab metrics** — `mermaid_mindmap_scaling_lab.html`
  now shows an always-visible Metrics panel including `textTarget` and
  `mermaidFont` values plus computed fit/scale numbers.
- **2026-05-06**: **Mindmap lab re-render** — `mermaid_mindmap_scaling_lab.html`
  now uses `mermaid.render()` with a unique id per run so “Re-render” is always
  a fresh SVG (no sticky `mermaid.run()` behavior).
- **2026-05-06**: **Mindmap sizing** — Mermaid mindmaps now prefer deterministic
  **fit-to-panel** geometry scaling by default (BBox/viewBox), avoiding reliance
  on Mermaid’s `fontSize` control which appears inconsistent in v11 for mindmap.
- **2026-05-06**: **Mermaid mindmap scaling lab** — added
  `mermaid_mindmap_scaling_lab.html` to isolate Mermaid v11 mindmap rendering in
  a fixed panel and compare sizing modes before porting the winner into the
  compiler template.
- **2026-05-06**: **Mermaid sizing: no flash + late diagrams** — compiled decks
  hide Mermaid output until it has been sized (no “tiny then snap” flash), and
  they wait (bounded attempts) for all Mermaid SVGs to exist before the first
  sizing pass so some Mermaid 11 diagram types don’t miss resizing.
- **2026-05-06**: **Mermaid sizing + view-scale** — compiled decks now re-run
  Mermaid SVG sizing when **view scale** changes (Shift+`+` / footer controls),
  preventing diagrams from starting tiny until the user zooms.
- **2026-05-06**: **Mermaid YAML overrides** — added `mermaid_scale` (multiplier)
  and `mermaid_scale_mode` (`measured`|`fit`) on slides/columns; compiler emits
  `data-scale-mult`/`data-scale-mode` on `.diagram-container` and the Mermaid
  sizing JS now honors them.
- **2026-05-06**: **Mermaid sizing** — added a CSS fallback in the compiled
  template so Mermaid SVGs don’t render at their tiny intrinsic size when
  Mermaid v11+ markup/ID schemes cause the JS post-processor to miss a diagram.
- **2026-04-25**: **`figure_crop` slide dev server** — injected crop overlay: **`renderBox`** uses viewport mapping consistent with **`imgRel`** (fixes wrong crop file corner/size under **`--figure-scale`** / view scale); handle/box drags use **`clientDeltaToLayout`**. See **`figure_crop/slidedev.py`**.
- **2026-04-24 (d)**: **Bullet stagger** — schema + compiler + **`base.html.j2`**: deck **`animation_defaults`**, slide **`bullet_animation`**, skill defaults in **`schema/animation_defaults.py`**; **[`examples/mycontent.yaml`](examples/mycontent.yaml)** updated (no inline scripts). Regenerated **`deck.schema.json`**.
- **2026-04-24 (b)**: **Two-column / comparison** column headers (**`h3`**) — **`font-size`** multiplied by **1.2** (same **`clamp(22px, 2.8vw, 34px) * var(--title-font-mul)`** base as global **`h3`**). Template: **`.claude/skills/md_to_yaml/compiler/templates/base.html.j2`**; **`final_talk1.html`** recompiled.
- **2026-04-24 (a)**: **Two-column / comparison** — column **`.slide-body`** is **`display: flex; flex-direction: column`** so **`gap`** spaces **`<h3>`** vs **`<ul>`**; **`gap`** set to **`calc(1.35rem * 1.5 * 1.5)`** (50% more than the previous **`calc(1.35rem * 1.5)`** target). Fixes slides like **Spectral Mapping** (markdown **`<!-- split -->`**). Template: **`.claude/skills/md_to_yaml/compiler/templates/base.html.j2`**.
- **2026-04-23 (e)**: **`conversion/.../PRESENTER_NOTES.md`** — full presenter script outline for **`final_talk1`** (40 slides): on-screen cues, detailed **Say** bullets, **Transition** lines between slides, GUO / four-factor / summary closings, timing tips.
- **2026-04-23 (d)**: **`conversion/.../final_talk1.yaml`** — last **five** slides (four operation-count **`content`** slides + **Transformer FLOPS** **`figure-wide`**) moved from **after** **`summary`** to **Part 7** between **Classical vs Quantum Attention at a Glance** and **GUO Quantum Transformer Pipeline**; **`final_talk1.html`** recompiled from that folder.
- **2026-04-23 (c)**: **`four_slides.yaml`** — four **`layout: content`** slides decomposing **$O(\sqrt{N} \cdot d_{\text{poly}} \cdot \log^2 N \cdot \log(1/\epsilon))$** (norm/amplitude, QSVT calls, gates per call, T-gate overhead); each slide **`subtitle`** states scaling; compiles with **`.claude/skills/md_to_yaml`** (consecutive-content warning only).
- **2026-04-24 (a)**: **Fixed slide footer** — deck keys **`footer_inset`** (CSS **`bottom`**, default **`0.5in`**, was **`1in`** in template only) and **`footer_scale`** (**0.5–2.5**); **`<html>`** sets **`--footer-scale`**, **`--slide-footer-inset`**; **`--slide-footer-ui-clearance`** scales with **`footer_scale`**. See [`CSS_CONTROLS.md`](CSS_CONTROLS.md) section **Fixed footer**.
- **2026-04-23 (m)**: **[`FIGURE_WIDE.md`](.claude/skills/md_to_yaml/FIGURE_WIDE.md)** — full **`layout: figure-wide`** reference; links from [`CSS_CONTROLS.md`](CSS_CONTROLS.md) and [`.claude/skills/md_to_yaml/SKILL.md`](.claude/skills/md_to_yaml/SKILL.md).
- **2026-04-23 (l)**: **`layout: figure-wide` / `figure_scale`** — apply scale with **`zoom` / `transform: scale`**, like **figure** **`--fill`**, not **`calc(100% * --figure-scale)`** on **img** **`max-height`** (unreliable when **%** height is indefinite).
- **2026-04-23 (k)**: (superseded) **`calc(100% * scale)`** attempt on **figure-wide** **img** **max** bounds.
- **2026-04-23 (j)**: **`layout: figure-wide`** — **taller** default **`.figure-wide-figure-wrap`** (**`min-height: clamp(12rem, 36vh, 62vh)`**); rasters / SVG use **`min(100%, 58vh×scale)`**-style caps so the graphic can **fill** a **tall** panel.
- **2026-04-23 (i)**: **`layout: figure-wide`** — optional **`figure_scale`** in slide frontmatter (same range as **`layout: figure`**); compiler sets **`--figure-scale`** on the section; **img** / **SVG** in **`.figure-wide-media`** use **vh**-based caps scaled like **`layout: figure`**. See **`CSS_CONTROLS.md`** and **`SKILL.md`**.
- **2026-04-23 (h)**: **`layout: figure-wide`** — **`.figure-wide-figure-wrap`**: **`min-height: clamp(10rem, 28vh, 50vh)`**, **`flex-shrink: 0`**, so the **infographic** / **raster** band does not **collapse to 0** when **summary** + **two-column** **markdown** use most of the **viewport**; **`final_talk1.html`** recompiled.
- **2026-04-23 (g)**: **`layout: figure`** **--fill** **panel** is **1** **in** **wider** than the **content** **column** (**`calc(100% + 1in)`**, **`margin: 0 -0.5in`**) — **½in** into each **slide** **side** **padding** — for **raster** / **file** **SVG** **slides** **(not** **Mermaid**).
- **2026-04-23 (f)**: **--fill** file **SVG**: template uses **`width: auto; max-width: 100%`** (not full column width) for horizontal centering; **`quantum_circuit_ancilla.svg`** **`viewBox`** tightened to **`100 0 780 500`** to balance art in user space. See [CSS_CONTROLS.md](CSS_CONTROLS.md) **figure** / **`viewBox` note.
- **2026-04-23 (e)**: **layout: figure (`--fill`)** — **Wrappers** **`overflow: visible`** (not **`hidden`**) so **`zoom` / `transform: scale`** is not **clipped**; **removed** **`max-height: 100%`** on the **slide-figure** **asset-wrap / figure** chain; **media** **`80vh` / `85vh`** only (no **`min(..., 100%)`**). **`section.slide-figure`** still **`overflow: hidden`** + **extra** **bottom** **padding** for **`.slide-footer-nav`**. **Refs:** `final_talk1.yaml` **Polylog** PNG, **Embedding** SVG.
- **2026-04-23 (d)**: **layout: figure** — **`section.slide-figure`**: one **`100vh`** **screen**, **flex** **`min-height: 0`** chain, **`padding-bottom: calc(1in + var(--slide-footer-ui-clearance))`** so content stays out of the **fixed** **bottom** **nav** band. **`:root`**: `--slide-footer-ui-clearance: 2.75rem` (tunable).
- **2026-04-23 (b)**: **`conversion/.../final_talk1.yaml`** — **GUO Quantum Transformer Pipeline** diagram: **Mermaid** **`flowchart TB`** with two **`subgraph`** rows (**`direction LR`**, three nodes each), **`C --> D`** between rows; **`%%{init}%%`** padding/node spacing; **alt_text** updated for accessibility.
- **2026-04-23 (c)**: **layout: figure (`.figure-asset-wrap--fill`)** — Browsers with **`@supports (zoom: 1)`** use **`zoom: var(--figure-scale)`** on rasters and file **`<svg>`** (replacing **`transform: scale`**) so the **laid-out** size tracks **`figure_scale`**; **Firefox** / no-zoom: keep **`transform`** + **flex** centering. Fixes **vertical centering** for **file SVG** at e.g. **`0.8`**; JPEGs already appeared acceptable.
- **2026-04-24 (b)**: **layout: figure (raster)** — **`.figure-asset-wrap--fill`**: panel **`max-width: 100%`**; **`img` / `svg`**: base **`max-height: 80vh|85vh`** and **`transform: scale(var(--figure-scale))`** so **landscape** images respond to per-slide **`figure_scale`** (e.g. **`4.0`** in **`final_talk1.yaml`**) without width saturating at scale 1. **Mermaid** unchanged.
- **2026-04-24**: **Mermaid (layout: figure)**: **`sizeSvgFit`**, rasters: **`--fill`**, Mermaid: no **`--fill`**.
- **2026-04-23**: **layout: figure** — **`.claude/skills/md_to_yaml`**: templates **`figure-asset-wrap`** / **`figure-asset`**, panel **`width: fit-content`**, **`figure_layout_debug`** on wrap vs media.
- **2026-04-22**: **View scale in compiled decks** — **`base.html.j2`**: **`#deck-app-root`**, footer zoom cluster at **1in** bottom margin, keyboard shortcuts, URL/localStorage per **`HANDOFF_ZOOM.md`**; **`schema/models.py`** + **`deck.schema.json`** for **`view_scale`** / **`remember_view_scale`**.

- **2026-04-22**: **[`HANDOFF_ZOOM.md`](HANDOFF_ZOOM.md)** — resume handoff: in-page view scale, browser zoom limits, **`.claude/skills/md_to_yaml/`** compiler path, `DeckMetadata` vs `engine.py`, `macros`, YAML escaped-LaTeX gotchas.

- **2026-04-22**: **Deck HTML** — slide chrome (centered counter + **`G`** / **`#`** go-to) lives in **`.claude/skills/md_to_yaml/compiler/templates/base.html.j2`** for decks built from that skill. (**`skills/deck-compile/`** is a separate vendored copy and may not be what you compile.)

- **2026-04-22**: **`polylog/`** — matplotlib scripts **`plot_scaling_families.py`** / **`plot_attention_contrast.py`** (Agg) with **`--format svg|png`**, **`--dpi`** for PNG, default output name picks the extension; helper **`plot_export.py`**; optional deps **`polylog/requirements-plots.txt`**; illustrates **`polylog.md`** scalings.

- **2026-04-22**: **[`CSS_CONTROLS.md`](CSS_CONTROLS.md)** — new **Display math (block `$$...$$`)** section (YAML + **`--math-display-scale` / `--math-display-color`**, center/start classes, template search); intro clarifies **`.claude/skills/md_to_yaml/compiler/templates/base.html.j2`** as the maintained template; summary table updated.

- **2026-04-22**: **`math_display_color`** (optional) on **`DeckMetadata`** and **`SlideBase`**; **`--math-display-color`** on **`<section>`**; block **`math`** and table-cell block math use **`color: var(--math-display-color, inherit)`**. Validated with **`tests/test_models.py`**. Regenerate **`deck.schema.json`** with **`python -m schema.json_schema`** from the skill tree.

- **2026-04-22**: **Display-math centering (md_to_yaml skill)** — **`base.html.j2`**: for **`math-display-eq-center`**, block **`<math>`** in body / table cells includes **`width: fit-content; max-width: 100%`** with **`margin: auto`** so standalone **`$$...$$`** lines center (Markdown often omits a wrapping **`<p>`**). **`HANDOFF_CENTER.md`** updated. Tests: **70** passed (**`test_compiler`**, **`test_models`** with **`PYTHONPATH=.claude/skills/md_to_yaml`**).

- **2026-04-22**: **Optional `subtitle`** on every slide layout — **`SlideBase.subtitle`** in **`skills/deck-compile/schema/models.py`**, shared heading templates + **`0.8em`** subtitle in **`base.html.j2`**; **`engine.py`** renders subtitle for all slides; **`deck.schema.json`** regenerated.

- **2026-04-22**: **[`CSS_CONTROLS.md`](CSS_CONTROLS.md)** — **Figure scale adjustments** section (per-layout, Mermaid/JS, two-column `vh` caps); template path **`skills/deck-compile/compiler/templates/base.html.j2`**.

- **2026-04-22**: **`figure-wide`** layout — flex-based “smart figure” in **`figure-wide.html.j2`** + **`base.html.j2`**: figure area grows/shrinks between title, optional summary, and **`figure-wide-below`** content so the slide stays within **100vh** and **1in** padding; images/SVG/**Mermaid** scale down inside the panel when vertical space is tight. Implemented in **`skills/deck-compile`** and mirrored under **`.claude/skills/md_to_yaml`**.

- **2026-04-19**: **`quantum_shots/quantum_shots-mathematical-20260419.{yaml,html}`** — **mathematical** flavor, **standard** detail, for graduate **scientific computing** (shots vs **$\\epsilon$**, bias–variance **$A/N+B$**, large-**$n$** covariance / bias ceilings, mitigation **$\\gamma^2$**, FTQC **$O(1/\\epsilon^2)$** sampling layer); compiled from **`skills/deck-compile`** with **`--warnings-as-errors`**.
- **2026-04-19**: **`skills/{deck-compile,deck-author,figure-spec}/USAGE.md`** — new-user usage guides (install, first compile, flags, workflows, symlinks).
- **2026-04-19**: **`docs/tasks/split-three-skills-tasks.md`** — task file for the three-skill split (T1–T5: vendor tooling, deck-compile, deck-author, figure-spec, optional `--warnings-as-errors`); Mermaid dependency graph; links to [`docs/plans/split-md-to-yaml-three-skills.plan.md`](docs/plans/split-md-to-yaml-three-skills.plan.md).
- **2026-04-19**: **`docs/plans/`** — in-repo location for agent plans when `~/.cursor/plans/` is not writable from the sandbox; includes **`split-md-to-yaml-three-skills.plan.md`** (three-skill split: deck-author, deck-compile, figure-spec) and **`README.md`** explaining the policy.
- **2026-04-05** (later): Built **`quantum_transformer_inference-implementation-20260405_2134.{yaml,html}`** (31 slides, **implementation**, **rich**) from **`quantum_transformer_inference/quantum_transformer_inference.md`** — block-encoding math, LCU/Hadamard/QSVT implementation path, complexity table, pseudocode API, frameworks; validated; **`python3 -m compiler`** with **`--embed-images`** from repo root; co-located under **`quantum_transformer_inference/`**.
- **2026-04-05**: Built **`quantum_transformer_inference-explanatory-20260405_2119.{yaml,html}`** (35 slides, **explanatory**, **rich**) from **`quantum_transformer_inference/quantum_transformer_inference.md`** — fault-tolerant “matrix API” narrative for CS/ML grads (I/O, block encoding, element-wise polynomials, attention/FFN scaling, assumptions, frameworks); validated; **`python3 -m compiler`** with **`--embed-images`** from repo root; co-located under **`quantum_transformer_inference/`**.
- **2026-04-04**: **`base.html.j2`** — **`--heading-h1`**, **`--heading-h2`**, **`--slide-emphasis`** on **`:root[data-theme]`** for global recolor of title slide **h1**, slide **h2**/**h3**, body **bold**/emphasis math, steps/summary markers; documented in CSS comment at top of embedded **`style`**.
- **2026-04-04**: **`equations.md` + skill** — bullet **subheaders** must use **one** `**...**` run (include headline **inline math** inside it when needed) so accent color is consistent; **`SKILL.md`** Critical Rule + **`quantum_transformer-explanatory-20260404_2233`** bullets updated.
- **2026-04-04**: **`.slide-body strong`** — accent color for all Markdown bold in standard slide bodies (e.g. **`**Encoder**`** without math). **Transcript** / **transcribe** decks override **`strong`** back to **`var(--text)`** for readability.
- **2026-04-04**: **`postprocess_emphasized_mathml`** — wraps **`<strong>…</strong>`** whenever it contains inline MathML (fixes **`**text $\alpha$**`** where Markdown emits **`text <math>`** inside strong). **`.deck-math-emphasis`** now sets **`color: var(--accent)`** and **`font-weight: 700`** on the span so label text and math are both gold.
- **2026-04-04**: **`equations.md`** — **Bold Markdown: labels before the colon only** (bullets: bold the label up to the colon; no bold around math or the rest of the sentence; avoid scattered bold after the colon). Sync skill copies from repo when updating **`~/.claude/skills`**.
- **2026-04-04** (evening, `2233`): Built **`quantum_transformer-explanatory-20260404_2233.{yaml,html}`** (29 slides, **explanatory**, **rich**) from **`quantum_transformer/quantum_transformer.md`** — classical vs quantum transformer (architecture, masking, residuals, LayerNorm, FFN, **$\tilde{O}(d^{3/2}\sqrt{N})$** vs classical regimes, tomography, caveats); validated; **`python3 -m compiler`** with **`--embed-images`** from repo root; co-located under **`quantum_transformer/`**.
- **2026-04-04**: **Emphasized inline math** — YAML stays **`**$...$**`**; after Markdown, **`postprocess_emphasized_mathml()`** replaces **`<strong><math>`** with **`<span class="deck-math-emphasis">`** so math uses **`var(--accent)`** (same as **`h2`** / title gold). Implemented in **`compiler/renderers/math.py`**, called from **`render_body`** / **`render_rich_text`**; CSS in **`base.html.j2`**; tests in **`tests/test_rich_content.py`**.
- **2026-04-04** (evening): Built **`quantum_transformer-explanatory-20260404_2145.{yaml,html}`** (29 slides, **explanatory**, **rich**) from **`quantum_transformer/quantum_transformer.md`** — classical vs quantum transformer (architecture flows, masked attention, residuals, LayerNorm, FFN, **$\tilde{O}(d^{3/2}\sqrt{N})$** vs classical regimes, tomography); **`parse_deck_file`** + **`validate_deck`** clean; **`python3 -m compiler`** with **`--embed-images`** from repo root; co-located under **`quantum_transformer/`**.
- **2026-04-04** (late): Built **`quantum_transformer-implementation-20260404_2133.{yaml,html}`** (24 slides, **implementation**, **rich**) from **`quantum_transformer/quantum_transformer.md`** — classical vs quantum transformer (masking, residuals, LayerNorm, FFN, asymptotics in **$N$** and **$d$**); validated; **`python3 -m compiler`** with **`--embed-images`** from repo root; co-located under **`quantum_transformer/`**.
- **2026-04-04**: Documented **YAML quoting vs LaTeX** (single vs double quotes, **`\\`** pitfall in single-quoted **`table`** cells) in **`equations.md`** and **`.claude/skills/md_to_yaml/SKILL.md`**; skill **`equations.md`** synced from repo root.
- **2026-04-04**: Built **`quantum_transformer-implementation-20260404_2058.{yaml,html}`** (27 slides, **implementation** flavor, **rich** detail) from **`quantum_transformer/quantum_transformer.md`** — classical vs quantum transformer with FFN pseudocode, LCU/QSVT mapping, masking, scaling table, tomography readout; validated with no layout warnings; **`python3 -m compiler`** with **`--embed-images`** from repo root.
- **2026-04-04**: Built **`quantum_transformer-explanatory-20260404_2052.{yaml,html}`** (36 slides, **rich** detail) from **`quantum_transformer/quantum_transformer.md`** — classical vs quantum transformer (block encodings, QSVT, masking, residuals, norms, FFN), scaling **$\tilde{O}(d^{3/2}\sqrt{N})$** vs dense classical attention; **`python3 -m compiler`** with **`--embed-images`** from repo root.
- **2026-04-04**: Built **`quantum_measurements-explanatory-20260404_1331.{yaml,html}`** (33 slides, **rich** detail) from **`quantum_measurements/quantum_measurements.md`** — narrative on probability, observables, projectors, $\alpha|0\rangle+\beta|1\rangle$, Z vs X measurement circuits, X-basis math, and shot statistics; **`uv run python -m compiler`** with **`--embed-images`** from repo root.
- **2026-04-04**: Built **`quantum_measurements-explanatory-20260404_1240.{yaml,html}`** from **`quantum_measurements/quantum_measurements.md`** (explanatory) using the bundled skill compiler; YAML and HTML stored next to the source markdown.
- **2026-03-26**: Updated **`quantum_shots/suggested_figures.md`** to apply the new literal text quoting rules from the `create_figure_captions` skill.
- **2026-03-26**: Added **Literal text and math (Critical)** examples to **`skills/create_figure_captions/SKILL.md`**, teaching the agent to explicitly quote exact strings (`reading exactly "..."`) for image prompts. Added a new checklist item to enforce it.
- **2026-03-26**: Generated **`quantum_shots/suggested_figures.md`** via **create_figure_captions** using the newly updated, clearly-labeled caption template.
- **2026-03-26**: Modified **`skills/create_figure_captions/SKILL.md`** to enforce clearer caption marking. Captions now use a `### 🖼️ FIGURE N CAPTION (Copy-paste)` header and blockquotes in the `suggested_figures.md` output.
- **2026-03-26**: Generated **`realistic_quantum_advantage/suggested_figures.md`** from **`realistic_quantum_advantage-explanatory-20260326_1425.yaml`** via **create_figure_captions** (four Nano Banana–style captions; requested `realistic_quantum_advantage.yaml` not in tree)
- **2026-03-26**: **`skills/create_figure_captions/SKILL.md`** — mandatory Nano Banana 2 caption structure (ordered clauses, one sentence); 3–4 figures from schema-agnostic YAML → `suggested_figures.md`
- **2026-03-26**: Built `realistic_quantum_advantage-explanatory-20260326_1425.{yaml,html}` from `realistic_quantum_advantage/realistic_quantum_advantage.md` (explanatory) via the bundled compiler; YAML and HTML co-located with the source folder
- **2026-03-26**: Built `quantum_shots-explanatory-20260326_0739.{yaml,html}` from `quantum_shots/quantum_shots.md` (explanatory flavor) via the repo-root bundled compiler; outputs co-located with the source folder
- **2026-03-25**: Documented squared-norm fix: **`$\left\|…\right\|^2$`** instead of **`$\lVert…\rVert^2$`** (latex2mathml); block-encoding Cost bullet updated
- **2026-03-25**: Documented latex2mathml quirk: use **`$\left\|…\right\|$`** instead of **`$\big\lVert…\big\rVert$`** for norms; updated block-encoding deck and `equations.md`
- **2026-03-25**: Documented YAML **single-quote** rule for slide `title:` / frontmatter LaTeX (avoids `\a`/`\e` mangling in double-quoted strings); patched `block_encoding-explanatory-20260325_1528` titles and recompiled
- **2026-03-25**: Built `block_encoding-explanatory-20260325_1528.{yaml,html}` from `block_encoding/block_encoding.md` (explanatory flavor) via the bundled compiler; YAML and HTML co-located with the source folder
- **2026-03-25**: Built `quantum_channels-explanatory-20260325_1336.{yaml,html}` from `quantum_channels/quantum_channels.md` using the repo compiler; outputs stored next to the source markdown
- **2026-03-24**: Transcribed full `migratedoc.md` → 96-slide YAML transcript → HTML with embedded images
