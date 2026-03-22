# Architecture Research

**Domain:** YAML-to-HTML presentation DSL compiler (Python, offline batch tool)
**Researched:** 2026-03-21
**Confidence:** HIGH (architecture is well-understood; specific library integrations MEDIUM)

## Standard Architecture

### System Overview

```
┌────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                             │
│  ┌──────────────┐   ┌───────────────┐   ┌──────────────────┐  │
│  │  YAML file   │   │  Image assets │   │  External refs   │  │
│  │  (DSL input) │   │  (jpg/png/svg)│   │  (CDN: KaTeX)    │  │
│  └──────┬───────┘   └───────┬───────┘   └────────┬─────────┘  │
└─────────┼───────────────────┼────────────────────┼────────────┘
          │                   │                    │
┌─────────▼───────────────────▼────────────────────▼────────────┐
│                       PARSE & VALIDATE LAYER                   │
│  ┌────────────────────┐   ┌──────────────────────────────────┐ │
│  │  YAML Parser       │   │  Schema Validator (Pydantic)     │ │
│  │  (PyYAML/ruamel)   │──▶│  Slide → typed Python models    │ │
│  └────────────────────┘   └──────────────┬───────────────────┘ │
└──────────────────────────────────────────┼─────────────────────┘
                                           │
┌──────────────────────────────────────────▼─────────────────────┐
│                      ASSET PROCESSING LAYER                     │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │  Math Processor │  │  Mermaid     │  │  Image Handler     │ │
│  │  (KaTeX via CDN │  │  Renderer    │  │  (base64 embed or  │ │
│  │   or Node call) │  │  (mmdc / CLI)│  │   relative path)   │ │
│  └────────┬────────┘  └──────┬───────┘  └────────┬───────────┘ │
└───────────┼──────────────────┼───────────────────┼─────────────┘
            │                  │                   │
┌───────────▼──────────────────▼───────────────────▼─────────────┐
│                       RENDER LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Layout Engine (Python + Jinja2)             │   │
│  │  Slide model ──▶ layout_type ──▶ Jinja2 template ──▶ HTML│   │
│  │  One template per layout primitive (~15 templates)       │   │
│  └──────────────────────────┬───────────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      ASSEMBLY LAYER                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  HTML Assembler                                           │  │
│  │  - Injects rendered slides into shell template           │  │
│  │  - Embeds CSS (dark theme, layout, ADA rules)            │  │
│  │  - Embeds JS (scroll-snap nav, sidebar, dots, progress)  │  │
│  │  - Injects KaTeX CDN link + auto-render config           │  │
│  │  - Builds sidebar TOC from slide titles                  │  │
│  │  - Inserts skip link, ARIA landmarks                     │  │
│  └──────────────────────────┬────────────────────────────────┘  │
└─────────────────────────────┼────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  Standalone .html │
                    │  (self-contained) │
                    └───────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| YAML Parser | Load DSL file into Python dicts | `ruamel.yaml` (preserves comments) or `PyYAML` |
| Schema Validator | Convert raw dicts to typed models, reject invalid DSL | `pydantic` v2 with discriminated union on `layout` field |
| Math Processor | Render LaTeX to HTML/MathML or pass raw to KaTeX CDN | KaTeX CDN auto-render (simplest); Node.js `katex.renderToString` for offline |
| Mermaid Renderer | Convert Mermaid source strings to inline SVG | `mmdc` Python package (no Node/browser required) or mermaid-cli |
| Image Handler | Embed images as base64 data URIs for self-contained output | `base64.b64encode` + `data:image/...` URI |
| Layout Engine | Dispatch each slide to its Jinja2 template by `layout_type` | `jinja2.Environment` with one template per layout primitive |
| HTML Assembler | Combine rendered slides into shell, inject CSS/JS/nav chrome | Top-level Jinja2 shell template; sidebar TOC built from slide titles |
| ADA Enforcer | Validate output for WCAG 2.1 AA compliance rules | Post-render lint pass: check alt text, ARIA, skip link presence |

## Recommended Project Structure

```
md_to_yaml/
├── compiler/
│   ├── __init__.py
│   ├── cli.py              # Entry point: parse args, invoke pipeline
│   ├── parser.py           # YAML load + Pydantic model construction
│   ├── models.py           # Pydantic DSL schema (Slide, Deck, layout unions)
│   ├── assets.py           # Image embedding, Mermaid rendering, math handling
│   ├── renderer.py         # Layout dispatch → Jinja2 template rendering
│   ├── assembler.py        # Combine slides into final HTML document
│   └── ada_check.py        # Post-render ADA validation lint pass
├── templates/
│   ├── shell.html.j2       # Outer document: CSS, JS, sidebar, nav chrome
│   ├── slide_title.html.j2
│   ├── slide_content.html.j2
│   ├── slide_two_col.html.j2
│   ├── slide_diagram.html.j2
│   ├── slide_figure.html.j2
│   ├── slide_divider.html.j2
│   ├── slide_code.html.j2
│   ├── slide_table.html.j2
│   └── ...                 # one file per layout primitive
├── static/
│   ├── base.css            # Dark theme, CSS custom properties, shared rules
│   └── deck.js             # Scroll-snap nav, sidebar active state, dots, progress
├── schema/
│   └── slide-dsl.yaml      # JSON Schema or YAML schema spec for DSL validation
├── tests/
│   ├── fixtures/           # Sample .yaml DSL inputs
│   ├── test_parser.py
│   ├── test_renderer.py
│   └── test_ada.py
├── examples/
│   └── sample_deck.yaml    # Reference example covering all layout types
└── skill/
    └── md_to_yaml.md       # Claude Code skill: generates YAML from content
```

### Structure Rationale

- **compiler/**: Pure Python pipeline — each module maps to one pipeline stage, making stages independently testable.
- **templates/**: One Jinja2 template per layout primitive. Adding a new layout type requires only a new template file and a model entry — no renderer code changes.
- **static/**: CSS and JS are stored as source files, inlined into the shell template at compile time (not served). Editing them doesn't require touching Python.
- **schema/**: Authoritative DSL specification lives here — used by both the Pydantic models and as documentation for the LLM skill.
- **skill/**: The Claude Code skill that generates YAML from markdown/PDF input. Kept here to colocate the DSL definition with its consumer.

## Architectural Patterns

### Pattern 1: Discriminated Union for Layout Dispatch

**What:** The Pydantic model uses `layout` as a discriminator field. Each layout type is a separate typed model. The renderer dispatches to the matching Jinja2 template by `layout` value — no `if/elif` chains.

**When to use:** Always, for the slide model. This is the core dispatch mechanism.

**Trade-offs:** Requires defining a model per layout type (low cost), but makes adding types safe and explicit. Avoids a brittle `isinstance` chain.

**Example:**
```python
from pydantic import BaseModel, Discriminator
from typing import Literal, Union

class TitleSlide(BaseModel):
    layout: Literal["title"]
    title: str
    subtitle: str | None = None
    speaker: str | None = None

class ContentSlide(BaseModel):
    layout: Literal["content"]
    title: str
    bullets: list[str]
    callout: str | None = None

SlideModel = Annotated[
    Union[TitleSlide, ContentSlide, TwoColSlide, DiagramSlide, ...],
    Field(discriminator="layout")
]
```

### Pattern 2: Template-per-Layout with Shared Macros

**What:** Each layout type has its own Jinja2 template. Shared elements (bullet list, callout box, code block, formula block) are Jinja2 macros in a `macros.html.j2` file, imported by each layout template.

**When to use:** Always. Prevents HTML duplication across templates.

**Trade-offs:** Requires discipline to keep macros DRY. The payoff is that changing a callout style updates all layouts that use it.

**Example:**
```jinja2
{# templates/macros.html.j2 #}
{% macro callout(text, color="blue") %}
<div class="hl-{{ color }}" role="note">{{ text }}</div>
{% endmacro %}

{# templates/slide_content.html.j2 #}
{% from "macros.html.j2" import callout %}
<section class="slide slide--content" ...>
  <h2 class="slide-title">{{ slide.title }}</h2>
  <ul>{% for b in slide.bullets %}<li>{{ b }}</li>{% endfor %}</ul>
  {% if slide.callout %}{{ callout(slide.callout) }}{% endif %}
</section>
```

### Pattern 3: Asset Pre-Processing Before Render

**What:** All asset transformations (Mermaid SVG rendering, image base64 encoding, math pre-processing decisions) happen in a dedicated `assets.py` stage _before_ templates are rendered. Templates receive clean, ready-to-embed strings — they never call external tools.

**When to use:** Always. Separates side-effectful work (subprocess calls, file I/O) from pure template rendering.

**Trade-offs:** Requires passing enriched models (or an asset context dict) into the renderer. Simplifies testing: renderer tests use pre-baked assets, asset tests run without templates.

## Data Flow

### Compilation Flow

```
Input: deck.yaml
    │
    ▼
[1] YAML Load (PyYAML)
    │  raw dict: {meta: {...}, slides: [...]}
    ▼
[2] Pydantic Validation
    │  DeckModel with typed SlideModel list
    │  Raises ValidationError with field path on bad DSL
    ▼
[3] Asset Processing (per slide)
    │  Mermaid blocks → inline SVG strings
    │  Images → base64 data URIs
    │  Math → decision: CDN auto-render (preferred) or pre-render
    ▼
[4] Slide Rendering (Jinja2, per slide)
    │  slide.layout → template lookup → rendered HTML fragment
    ▼
[5] Document Assembly
    │  Shell template + [slide fragments] + sidebar TOC
    │  CSS inlined from static/base.css
    │  JS inlined from static/deck.js
    ▼
[6] ADA Lint Pass
    │  Check: all <img> have alt, ARIA landmarks present,
    │  skip link exists, dot buttons have aria-label
    ▼
Output: deck.html (standalone, self-contained)
```

### Key Data Flows

1. **YAML → Pydantic model:** The `layout` field in each slide YAML node is the discriminator. Pydantic validates every field against the specific layout model — typos in field names produce precise error messages immediately.

2. **Mermaid string → SVG:** `assets.py` calls `mmdc` (or mermaid-cli) as a subprocess, receives SVG text, strips `<?xml ...?>` header, stores the clean SVG string in the slide model for the template to embed directly as `{{ slide.diagram_svg | safe }}`.

3. **Math rendering decision:** KaTeX CDN auto-render is the default (simplest, zero build dependency). The shell template includes the KaTeX CDN script and auto-render configuration. LaTeX strings pass through as-is, wrapped in `\(...\)` or `\[...\]` delimiters. Pre-rendering via Node.js `katex.renderToString` is an optional upgrade for offline or faster-loading decks.

4. **Sidebar TOC:** Assembler collects `(slide_index, slide.title)` pairs from the validated model, renders them into `<a href="#slide-N">` links in the shell template. No second parse pass needed.

## Scaling Considerations

This is a local batch CLI tool, not a service. "Scaling" means handling large decks and many decks efficiently.

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1–60 slides (typical) | Sequential pipeline as described — no optimizations needed |
| 60–200 slides | Mermaid rendering is the bottleneck (subprocess per diagram); batch or parallelize with `concurrent.futures` |
| Many decks (CI batch) | Jinja2 Environment template cache is already in-memory; reuse a single `Compiler` instance across deck compilations |

### Scaling Priorities

1. **First bottleneck:** Mermaid subprocess calls (one per diagram). If a deck has 10+ diagrams, render them in parallel using `ThreadPoolExecutor`.
2. **Second bottleneck:** Jinja2 template loading. Use a module-level `jinja2.Environment` instance so templates are parsed once and cached across all slides.

## Anti-Patterns

### Anti-Pattern 1: Rendering Logic in Templates

**What people do:** Put `if/elif` chains in Jinja2 templates to handle layout variations — e.g., `{% if slide.type == 'two_col' %}...{% elif slide.type == 'content' %}...{% endif %}` in a single monolithic template.

**Why it's wrong:** Templates become impossible to maintain. Adding a layout type requires editing a large template. Template errors have no type context. This is how LLM-generated slide compilers typically start and then fail to scale.

**Do this instead:** One template file per layout type. Let Python dispatch; let templates be dumb presenters.

### Anti-Pattern 2: Calling External Tools from Templates

**What people do:** Use Jinja2 custom filters or global functions to call Mermaid CLI or KaTeX inside template rendering — e.g., `{{ slide.mermaid | render_mermaid }}`.

**Why it's wrong:** Mixes side effects into the pure rendering pass. Makes templates non-deterministic, hard to test, and slow (subprocess per template render). Errors surface during rendering rather than during asset processing.

**Do this instead:** All asset transforms happen in `assets.py` before rendering. Templates receive already-processed strings.

### Anti-Pattern 3: Inlining CSS/JS as Strings in Python

**What people do:** Store CSS and JavaScript as Python string constants in `assembler.py` or `renderer.py`.

**Why it's wrong:** No syntax highlighting, no editor support, no ability to test CSS independently. Changes to the dark theme require editing Python source.

**Do this instead:** Store CSS in `static/base.css` and JS in `static/deck.js`. Read and inline them at assembly time: `css = Path("static/base.css").read_text()`.

### Anti-Pattern 4: No ADA Validation Pass

**What people do:** Trust that the templates produce correct ADA HTML.

**Why it's wrong:** Template changes silently break ADA compliance. The existing system documents that dot button sizes and ARIA landmarks are frequent failure points.

**Do this instead:** A lightweight post-render linting pass using Python's `html.parser` or `BeautifulSoup` checks for the known ADA requirements: skip link presence, ARIA landmark coverage, alt text on all images, aria-label on all interactive elements.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| KaTeX CDN | `<script>` tag in shell template; auto-render on page load | Default. Zero build dependency. Requires internet on viewer side. |
| KaTeX (offline) | Subprocess call to `node -e "katex.renderToString(...)"` | Optional upgrade. Requires Node.js. Eliminates CDN dependency. |
| Mermaid CLI (`mmdc`) | Subprocess via `mmdc` Python package | `pip install mmdc`. No Node.js required. Renders to SVG. |
| Syntax Highlighting | `pygments` Python library → inline `<style>` + `<code>` blocks | Pure Python. No JS runtime needed for highlighting. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `parser.py` → `renderer.py` | Pydantic `DeckModel` object | The model is the contract. Parser owns construction; renderer owns reading. |
| `assets.py` → `renderer.py` | Asset strings attached to slide models (or parallel dict keyed by slide index) | Prefer enriching the model rather than passing a side-channel dict. |
| `renderer.py` → `assembler.py` | List of rendered HTML fragment strings | Assembler only concatenates and wraps; it does not re-interpret slide content. |
| `assembler.py` → `ada_check.py` | Final HTML string | ADA pass receives the complete document, not fragments. |
| `cli.py` → pipeline | Invokes `parser → assets → renderer → assembler → ada_check` in sequence | CLI is the only orchestrator; pipeline stages do not call each other. |

## Build Order for Phases

The component dependencies dictate this implementation order:

1. **Models first** (`models.py`): Pydantic schema defines the DSL contract. Everything depends on it. Cannot proceed without a stable schema.
2. **Shell template + CSS/JS** (`templates/shell.html.j2`, `static/`): Establishes the HTML skeleton the slides will be inserted into. Enables visual testing immediately.
3. **Parser + basic layouts** (`parser.py`, first 3–4 layout templates): Validates the schema end-to-end with real YAML inputs.
4. **Asset pipeline** (`assets.py`): Mermaid and image handling. Can be stubbed (pass-through) initially.
5. **Remaining layout templates**: Add templates for all ~15 layout primitives.
6. **Assembler** (`assembler.py`): Full document assembly with sidebar, nav chrome.
7. **ADA lint pass** (`ada_check.py`): Final quality gate.
8. **Claude Code skill** (`skill/md_to_yaml.md`): Built last, after compiler is stable — the skill's output format is validated against the final schema.

## Sources

- [Marp/Marpit architecture overview — DeepWiki](https://deepwiki.com/marp-team/marpit/1-overview) (MEDIUM confidence — secondary source)
- [Marp GitHub ecosystem](https://github.com/marp-team/marp) (HIGH confidence — official)
- [Slidev — Why Slidev](https://sli.dev/guide/why) (HIGH confidence — official)
- [mmdc Python package — pure Python Mermaid renderer](https://github.com/mohammadraziei/mmdc) (MEDIUM confidence — new library, Jan 2026)
- [mermaid-cli Python wrapper](https://pypi.org/project/mermaid-cli/) (MEDIUM confidence)
- [KaTeX server-side rendering](https://katex.org/docs/api) (HIGH confidence — official)
- [Jinja2 Environment and rendering pipeline — Real Python](https://realpython.com/primer-on-jinja-templating/) (HIGH confidence)
- [Pydantic discriminated unions](https://docs.pydantic.dev/latest/) (HIGH confidence — official)
- Existing HTML deck analysis: `/Users/erlebach/src/2026/claude-code/n8n/n8n_to_python/output_html_files/` — direct inspection of ground truth output (HIGH confidence)

---
*Architecture research for: YAML-to-HTML slide DSL compiler*
*Researched: 2026-03-21*
