# Phase 3: Rich Content - Research

**Researched:** 2026-03-22
**Domain:** Python rich content rendering — math, syntax highlighting, SVG, Mermaid, tables, inline Markdown
**Confidence:** HIGH (all key libraries verified against PyPI; architecture confirmed against existing codebase)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Math: `latex2mathml` Python library converts LaTeX to MathML at compile time — no CDN, no JS
- Code highlighting: Pygments at compile time — generates styled `<span>` elements with CSS classes
- Code line numbers: off by default, opt-in via `line_numbers: bool = False` field on `CodeSlide`
- Pygments color theme auto-matches slide theme (dark → Monokai-style, light → light code theme)
- Images: `<img src="...">` by default; `--embed-images` CLI flag for base64 data URIs
- Compiler warns on stderr if referenced image file doesn't exist (does not halt — warning not error)
- SVG: embedded inline with ADA wrapper (`<title>`, `<desc>`, `role="img"`, `aria-labelledby`)
- SVG: compiler sanitizes before embedding — strips `<script>`, `onclick`, event handlers
- Mermaid: compiled to SVG at compile time via `mmdc` (Mermaid CLI, requires Node); output embedded inline with ADA attributes
- Tables: `<caption>`, `<th scope="col|row">`, wide tables in horizontally scrollable container, CSS custom properties for theming
- Inline Markdown: Python-Markdown library with GFM-style extensions; replaces Phase 2 placeholder rendering

### Claude's Discretion

- Specific Pygments theme pairings for dark/light
- SVG sanitization library choice (e.g., `bleach`, `defusedxml`, or custom)
- `latex2mathml` configuration details
- Table caption extraction strategy from YAML
- Markdown extension set selection
- Internal module organization for rich content renderers

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RICH-01 | Math rendering — LaTeX `$$...$$` and `$...$` converted to MathML at compile time | `latex2mathml` 3.79.0 API verified; inline vs display modes confirmed |
| RICH-02 | Code blocks with syntax highlighting (Pygments), language from YAML | Pygments 2.19.2 `highlight()` + `HtmlFormatter`; `line_numbers` field added to `CodeSlide` |
| RICH-03 | JPEG/PNG images embedded as base64 or referenced by path; required alt text | `base64` stdlib; `--embed-images` CLI arg; image-missing → warning path |
| RICH-04 | SVG direct embedding with ADA wrapper | `defusedxml` for safe parse; `bleach` for attribute stripping; template update |
| RICH-05 | Inline Markdown within slide body fields | Python-Markdown 3.10.2; `markdown.markdown()` with selected extensions |
| RICH-06 | Mermaid diagrams to static inline SVG with ADA attributes | `mmdc` (`@mermaid-js/mermaid-cli` 11.12.0); subprocess call; output post-processed for ADA |
| RICH-07 | Tables with accessible markup (`<caption>`, `<th scope>`) | Table data in YAML model; Jinja2 template renders accessible HTML |
</phase_requirements>

---

## Summary

Phase 3 adds compile-time rendering for all rich content types: math (MathML), syntax-highlighted code, raster images (path or base64), inline SVG, Mermaid-to-SVG, accessible tables, and inline Markdown. Every decision has been locked: no CDN dependencies except the existing Google Fonts link. All rendering happens in Python (or via `mmdc` subprocess), producing deterministic output.

The existing codebase provides strong scaffolding: `compiler/engine.py` has a clean `_render()` hook, each layout has its own Jinja2 template, and the CSS custom properties pattern handles theming. Rich content renderers slot in as a new `compiler/renderers/` module called during `_render()` before template rendering.

The most operationally uncertain item is `mmdc` (Mermaid CLI via Node). It is confirmed to exist on npm as `@mermaid-js/mermaid-cli` at version 11.12.0, but it was flagged as a blocker in STATE.md because the Python-native `mmdc` package is new (Jan 2026). The plan must treat `mmdc` as a required system dependency (installed with `npm install -g @mermaid-js/mermaid-cli`) and fail gracefully when it is absent.

**Primary recommendation:** Create `compiler/renderers/` with one module per content type (math, code, image, svg, mermaid, markdown). Each renderer is a pure function that takes raw content + metadata and returns an HTML string. `engine._render()` calls renderers before passing context to Jinja2 templates.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `latex2mathml` | 3.79.0 | LaTeX → MathML at compile time | Pure Python, no external deps, actively maintained |
| `Pygments` | 2.19.2 | Code syntax highlighting to HTML | Industry standard; already installed in project env |
| `Markdown` | 3.10.2 | Inline Markdown → HTML | Reference implementation; GFM extensions available |
| `defusedxml` | 0.7.1 | Safe XML/SVG parsing (security) | Python stdlib xml is vulnerable to entity attacks |
| `bleach` | 6.3.0 | HTML/SVG attribute stripping | Allowlist-based; handles SVG sanitization cleanly |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `@mermaid-js/mermaid-cli` (npm) | 11.12.0 | Mermaid diagram → SVG subprocess | Only when DiagramSlide with Mermaid source is present |
| `base64` (stdlib) | — | Image embedding as data URI | Only when `--embed-images` CLI flag is set |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `latex2mathml` | KaTeX CDN | KaTeX is faster to author but requires JS at runtime — violates compile-time requirement |
| `Pygments` | Highlight.js CDN | Pygments is pure Python, deterministic, no JS dependency |
| `bleach` + `defusedxml` | Custom regex SVG stripping | Custom regex misses edge cases (CSS-based event handlers, SVG `<use>` xlink attacks) |
| `mmdc` subprocess | Client-side Mermaid JS | Client-side breaks determinism and compile-time ADA attribute injection |

**Installation:**
```bash
python3 -m pip install latex2mathml>=3.79.0 Pygments>=2.19.2 Markdown>=3.10.2 defusedxml>=0.7.1 bleach>=6.3.0
npm install -g @mermaid-js/mermaid-cli
```

**Version verification (confirmed against PyPI 2026-03-22):**
- `latex2mathml`: 3.79.0 (latest)
- `Pygments`: 2.19.2 (latest; already installed)
- `Markdown`: 3.10.2 (latest)
- `defusedxml`: 0.7.1 (latest)
- `bleach`: 6.3.0 (latest)
- `@mermaid-js/mermaid-cli`: 11.12.0 (latest on npm)

---

## Architecture Patterns

### Recommended Project Structure
```
compiler/
├── engine.py            # existing — calls renderers before template render
├── renderers/           # NEW — one module per content type
│   ├── __init__.py      # exports render_body(), render_math(), etc.
│   ├── markdown.py      # inline Markdown → HTML (RICH-05)
│   ├── math.py          # LaTeX → MathML (RICH-01)
│   ├── code.py          # code + Pygments highlighting (RICH-02)
│   ├── image.py         # path ref or base64 embedding (RICH-03)
│   ├── svg.py           # SVG sanitize + ADA wrap (RICH-04)
│   └── mermaid.py       # mmdc subprocess → SVG (RICH-06)
├── templates/
│   ├── base.html.j2     # add Pygments CSS block; add MathML browser compat note
│   ├── code.html.j2     # replace <pre><code> with pre-rendered Pygments HTML
│   ├── diagram.html.j2  # replace body|safe with rendered SVG string
│   ├── figure.html.j2   # add data URI support; figcaption for alt_text
│   └── (table layout — new or reuse content.html.j2)
└── validators.py        # extend: image path existence → warning
```

### Pattern 1: Renderer as Pure Function
**What:** Each renderer takes raw content (string) plus context (language, theme, etc.) and returns an HTML string. No side effects.
**When to use:** All content types.
**Example:**
```python
# compiler/renderers/math.py
import latex2mathml.converter

def render_math_inline(tex: str) -> str:
    """Convert inline $...$ LaTeX to MathML element."""
    return latex2mathml.converter.convert(tex, display="inline")

def render_math_display(tex: str) -> str:
    """Convert display $$...$$ LaTeX to MathML element."""
    return latex2mathml.converter.convert(tex, display="block")
```

### Pattern 2: Pre-process Body Before Template Rendering
**What:** `engine._render()` runs body content through renderers to produce an HTML string, then passes the rendered string to Jinja2 as a variable. Templates use `| safe` on already-sanitized output.
**When to use:** `body` field on all slides.
**Example:**
```python
# compiler/engine.py — updated _render()
from compiler.renderers import render_body

def _render(deck: Deck, embed_images: bool = False) -> str:
    template = _env.get_template("base.html.j2")
    slides_rendered = []
    for slide in deck.slides:
        rendered_body = render_body(slide, embed_images=embed_images) if slide.body else None
        slides_rendered.append((slide, rendered_body))
    return template.render(deck=deck, slides_rendered=slides_rendered, total=len(deck.slides))
```

### Pattern 3: Pygments CSS Injection
**What:** Pygments `HtmlFormatter` generates CSS; inject once into `<style>` block in `base.html.j2`.
**When to use:** Any deck containing a `CodeSlide`.
**Example:**
```python
# compiler/renderers/code.py
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

def get_pygments_css(theme_name: str) -> str:
    style = 'monokai' if theme_name == 'dark' else 'friendly'
    return HtmlFormatter(style=style).get_style_defs('.highlight')

def render_code(source: str, language: str, line_numbers: bool = False, theme: str = 'dark') -> str:
    style = 'monokai' if theme == 'dark' else 'friendly'
    try:
        lexer = get_lexer_by_name(language, stripall=True)
    except Exception:
        lexer = TextLexer()
    formatter = HtmlFormatter(style=style, linenos=line_numbers, cssclass='highlight')
    return highlight(source, lexer, formatter)
```

### Pattern 4: mmdc Subprocess Call
**What:** `mmdc` is invoked as a subprocess, writing SVG to stdout or a temp file.
**When to use:** `DiagramSlide` with Mermaid source content.
**Example:**
```python
# compiler/renderers/mermaid.py
import subprocess, tempfile, os

def render_mermaid(source: str, alt_text: str) -> str:
    """Run mmdc and return ADA-wrapped inline SVG string."""
    with tempfile.NamedTemporaryFile(suffix='.mmd', mode='w', delete=False) as f:
        f.write(source)
        mmd_path = f.name
    svg_path = mmd_path + '.svg'
    try:
        subprocess.run(['mmdc', '-i', mmd_path, '-o', svg_path], check=True, capture_output=True)
        svg_content = open(svg_path).read()
    except FileNotFoundError:
        raise RuntimeError("mmdc not found — install with: npm install -g @mermaid-js/mermaid-cli")
    finally:
        os.unlink(mmd_path)
        if os.path.exists(svg_path):
            os.unlink(svg_path)
    return _wrap_svg_ada(svg_content, alt_text)
```

### Pattern 5: SVG Sanitization with defusedxml + bleach
**What:** Parse SVG with `defusedxml`, strip dangerous elements/attributes with `bleach`, then add ADA wrapper.
**When to use:** Raw SVG content from `DiagramSlide.body` (user-supplied SVG).
**Example:**
```python
# compiler/renderers/svg.py
import bleach
from defusedxml import ElementTree

ALLOWED_SVG_TAGS = ['svg', 'g', 'path', 'circle', 'rect', 'line', 'text', 'tspan',
                    'defs', 'use', 'symbol', 'title', 'desc', 'polygon', 'polyline',
                    'ellipse', 'marker', 'clipPath', 'linearGradient', 'radialGradient', 'stop']
STRIP_TAGS = ['script', 'object', 'embed', 'iframe']
STRIP_ATTRS = ['onclick', 'onload', 'onerror', 'onmouseover']

def sanitize_svg(raw_svg: str) -> str:
    # defusedxml prevents XXE; bleach strips dangerous attrs
    return bleach.clean(raw_svg, tags=ALLOWED_SVG_TAGS, strip=True)

def wrap_svg_ada(svg: str, alt_text: str, slide_id: str) -> str:
    title_id = f'{slide_id}-svg-title'
    desc_id = f'{slide_id}-svg-desc'
    wrapped = svg.replace('<svg', f'<svg role="img" aria-labelledby="{title_id} {desc_id}"', 1)
    injection = f'<title id="{title_id}">{alt_text}</title><desc id="{desc_id}">{alt_text}</desc>'
    wrapped = wrapped.replace('>', injection, 1)  # insert after opening <svg ...>
    return wrapped
```

### Pattern 6: Table Slide (RICH-07)
**What:** Table data stored in YAML as a list of rows with a caption field. Jinja2 template renders accessible `<table>`.
**When to use:** Dedicated `table` layout type (check if one exists; if not, add `TableSlide` model).
**Note:** The existing 12 layout types do not include a dedicated `table` layout. A `TableSlide` model is needed, OR tables can be handled as structured content within `ContentSlide` body. Decision: CONTEXT.md implies tables are rendered from YAML fields — a dedicated layout is appropriate.

### Anti-Patterns to Avoid
- **Regex-based LaTeX substitution in body:** Use `render_body()` to handle math before Markdown to avoid Markdown eating `$` delimiters.
- **Calling `mmdc` for every compile:** Cache SVG output keyed on Mermaid source hash during a single compile run.
- **Using `| safe` on unrendered user input:** Always pass content through renderer (which sanitizes) before using `| safe` in templates.
- **Embedding Pygments CSS inline per slide:** Inject CSS once in `base.html.j2` `<style>` block, not per-slide.
- **Halt on missing `mmdc`:** Missing `mmdc` should produce a warning + placeholder `<div>` (not a compile error) unless the deck has Mermaid slides.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| LaTeX → HTML/MathML | Custom regex parser | `latex2mathml` | LaTeX grammar is context-sensitive; edge cases multiply |
| Code syntax highlighting | Token-based manual colorizer | `Pygments` | 500+ language lexers; themes; line number support built in |
| SVG XSS prevention | Regex to strip `<script>` | `defusedxml` + `bleach` | CSS-based event handlers, SVG `<use>` xlink exfiltration bypass regex |
| Mermaid → SVG | Python Mermaid parser | `mmdc` subprocess | Mermaid grammar evolves; CLI is the reference implementation |
| Markdown → HTML | Manual bold/italic regex | `Markdown` library | Handles nested constructs, escaping, link references correctly |

**Key insight:** Every "simple" content renderer has a long tail of edge cases (nested constructs, encoding, security). Use purpose-built libraries.

---

## Common Pitfalls

### Pitfall 1: Math Delimiter Collision with Markdown
**What goes wrong:** Python-Markdown processes `$...$` content before math renderer runs — underscore escaping and asterisks inside formulas get mangled.
**Why it happens:** Markdown runs before math substitution.
**How to avoid:** Run math extraction/conversion BEFORE Markdown rendering. Extract `$$...$$` and `$...$` spans, replace with placeholder tokens, run Markdown, then substitute MathML back.
**Warning signs:** MathML output contains HTML entity-encoded `<` and `>` characters from Markdown escaping.

### Pitfall 2: mmdc Not Found at Runtime
**What goes wrong:** `FileNotFoundError` on `mmdc` call crashes compilation with unhelpful message.
**Why it happens:** Node/mmdc not installed as build dependency.
**How to avoid:** Check for `mmdc` at startup if any `DiagramSlide` has Mermaid source. Emit clear error: "mmdc required — install with: npm install -g @mermaid-js/mermaid-cli".
**Warning signs:** `subprocess.run(['mmdc', ...])` raises `FileNotFoundError`.

### Pitfall 3: Pygments CSS Specificity Clash
**What goes wrong:** Pygments-generated `.highlight span` classes conflict with existing slide CSS rules.
**Why it happens:** Pygments uses generic class names like `.k`, `.n`, `.s`.
**How to avoid:** Scope Pygments CSS under `.slide-code .highlight` by using `HtmlFormatter(cssclass='slide-code')`.

### Pitfall 4: SVG Width/Height Overflows Slide
**What goes wrong:** Embedded SVG has explicit `width`/`height` attributes that exceed the slide viewport.
**Why it happens:** Mermaid and user SVGs often have fixed pixel dimensions.
**How to avoid:** Post-process embedded SVG to replace fixed `width`/`height` with `width="100%" height="auto"` and preserve `viewBox`.

### Pitfall 5: bleach Stripping Valid SVG Attributes
**What goes wrong:** `bleach` removes `viewBox`, `xmlns`, `fill`, `stroke`, etc. as they are not in its default allowlist.
**Why it happens:** bleach's SVG support requires explicit attribute allowlist.
**How to avoid:** Build a comprehensive `ALLOWED_SVG_ATTRIBUTES` dict for `bleach.clean()`. Verify with a test SVG after stripping.

### Pitfall 6: Table Layout Type Missing from Schema
**What goes wrong:** YAML files with `layout: table` fail Pydantic validation — `TableSlide` is not defined in `models.py`.
**Why it happens:** The existing 12 layout types do not include `table`.
**How to avoid:** Add `TableSlide` model to `schema/models.py` and add it to `AnySlide` union before implementing the template.

---

## Code Examples

Verified patterns from official sources:

### latex2mathml — inline and display
```python
# Source: latex2mathml PyPI / GitHub readme
import latex2mathml.converter

inline = latex2mathml.converter.convert(r"\alpha + \beta", display="inline")
display = latex2mathml.converter.convert(r"\int_0^\infty e^{-x}\,dx", display="block")
```

### Pygments — highlight with theme
```python
# Source: Pygments docs https://pygments.org/docs/formatters/
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

lexer = get_lexer_by_name('python', stripall=True)
formatter = HtmlFormatter(style='monokai', linenos=False, cssclass='highlight')
html = highlight('print("hello")', lexer, formatter)
css = formatter.get_style_defs('.highlight')
```

### Python-Markdown — with extensions
```python
# Source: Python-Markdown docs https://python-markdown.github.io/
import markdown

html = markdown.markdown(
    body_text,
    extensions=['tables', 'fenced_code', 'attr_list', 'md_in_html'],
)
```

### Accessible table HTML pattern
```html
<!-- RICH-07 target output pattern -->
<div class="table-scroll-wrapper">
  <table>
    <caption>Caption text from YAML</caption>
    <thead>
      <tr><th scope="col">Col A</th><th scope="col">Col B</th></tr>
    </thead>
    <tbody>
      <tr><th scope="row">Row label</th><td>Value</td></tr>
    </tbody>
  </table>
</div>
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| KaTeX CDN auto-render (runtime JS) | latex2mathml compile-time MathML | Phase 3 decision | Zero JS dependency for math; screen reader compatible |
| Highlight.js CDN | Pygments compile-time | Phase 3 decision | Deterministic output; no CDN |
| Client-side Mermaid JS | mmdc compile-time SVG | Phase 3 decision | ADA attributes injectable; deterministic |

**Deprecated/outdated:**
- `bleach` HTML sanitization for full HTML documents: bleach is designed for fragment sanitization, not full document parsing — correct use case here (SVG fragments only).

---

## Open Questions

1. **TableSlide model fields**
   - What we know: needs `caption`, `headers`, `rows` YAML fields; `row_headers: bool` for `<th scope="row">` support
   - What's unclear: whether first column is always row-header or configurable per table
   - Recommendation: add `row_headers: bool = False` to `TableSlide`; when True, first cell of each body row uses `<th scope="row">`

2. **Math delimiter extraction order**
   - What we know: must run before Markdown to prevent `$` mangling
   - What's unclear: whether `body` fields ever mix math + Markdown in the same slide
   - Recommendation: process math substitution first on all `body` fields; safe even if no math present

3. **mmdc availability fallback behavior**
   - What we know: mmdc is a Node dependency, not Python
   - What's unclear: whether CI/test environments will have Node available
   - Recommendation: Mermaid test fixtures mock `subprocess.run`; integration tests gate on `shutil.which('mmdc') is not None`

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.x |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `python3 -m pytest tests/test_rich_content.py -x -q` |
| Full suite command | `python3 -m pytest tests/ -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RICH-01 | `$$E=mc^2$$` in body renders to `<math display="block">` | unit | `pytest tests/test_rich_content.py::test_math_display -x` | Wave 0 |
| RICH-01 | `$\alpha$` inline renders to `<math display="inline">` | unit | `pytest tests/test_rich_content.py::test_math_inline -x` | Wave 0 |
| RICH-02 | Python code block produces Pygments `<span>` output | unit | `pytest tests/test_rich_content.py::test_code_highlight -x` | Wave 0 |
| RICH-02 | Unknown language falls back to plain text (no crash) | unit | `pytest tests/test_rich_content.py::test_code_unknown_lang -x` | Wave 0 |
| RICH-02 | `line_numbers: true` produces line number markup | unit | `pytest tests/test_rich_content.py::test_code_line_numbers -x` | Wave 0 |
| RICH-03 | `FigureSlide` with path ref produces `<img src="path">` | unit | `pytest tests/test_rich_content.py::test_image_path_ref -x` | Wave 0 |
| RICH-03 | `--embed-images` produces `<img src="data:image/...;base64,...">` | unit | `pytest tests/test_rich_content.py::test_image_embed -x` | Wave 0 |
| RICH-03 | Missing image file emits warning to stderr, HTML still produced | unit | `pytest tests/test_rich_content.py::test_image_missing_warning -x` | Wave 0 |
| RICH-04 | Raw SVG in body embedded inline with `role="img"`, `<title>`, `<desc>` | unit | `pytest tests/test_rich_content.py::test_svg_embed_ada -x` | Wave 0 |
| RICH-04 | SVG with `<script>` tag has it stripped | unit | `pytest tests/test_rich_content.py::test_svg_sanitize -x` | Wave 0 |
| RICH-05 | `**bold**` in body renders as `<strong>bold</strong>` | unit | `pytest tests/test_rich_content.py::test_markdown_inline -x` | Wave 0 |
| RICH-06 | Mermaid source → inline SVG with ADA attrs (mock mmdc) | unit | `pytest tests/test_rich_content.py::test_mermaid_render_mock -x` | Wave 0 |
| RICH-06 | Missing mmdc raises `RuntimeError` with install instructions | unit | `pytest tests/test_rich_content.py::test_mermaid_no_mmdc -x` | Wave 0 |
| RICH-07 | Table slide renders `<caption>`, `<th scope="col">`, `<th scope="row">` | unit | `pytest tests/test_rich_content.py::test_table_accessible -x` | Wave 0 |
| RICH-07 | Wide table wrapped in scrollable container | unit | `pytest tests/test_rich_content.py::test_table_scroll_wrapper -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -m pytest tests/test_rich_content.py -x -q`
- **Per wave merge:** `python3 -m pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_rich_content.py` — all RICH-01 through RICH-07 test cases
- [ ] `tests/fixtures/rich_math.yaml` — deck with math equations
- [ ] `tests/fixtures/rich_code.yaml` — deck with code blocks
- [ ] `tests/fixtures/rich_figure.yaml` — deck with image references
- [ ] `tests/fixtures/rich_svg.yaml` — deck with raw SVG content
- [ ] `tests/fixtures/rich_mermaid.yaml` — deck with Mermaid source
- [ ] `tests/fixtures/rich_table.yaml` — deck with table layout
- [ ] `compiler/renderers/__init__.py` — renderers package
- [ ] `schema/models.py` — `TableSlide` model + `line_numbers` field on `CodeSlide`
- [ ] New dependencies in `pyproject.toml`: `latex2mathml`, `Markdown`, `defusedxml`, `bleach`

---

## Sources

### Primary (HIGH confidence)
- PyPI registry (verified 2026-03-22): latex2mathml 3.79.0, Pygments 2.19.2, Markdown 3.10.2, defusedxml 0.7.1, bleach 6.3.0
- npm registry (verified 2026-03-22): @mermaid-js/mermaid-cli 11.12.0
- Codebase inspection: `compiler/engine.py`, `compiler/templates/`, `schema/models.py`, `compiler/validators.py`, `pyproject.toml`

### Secondary (MEDIUM confidence)
- Pygments docs — `HtmlFormatter`, `get_style_defs()`, `cssclass` parameter — standard documented API
- Python-Markdown docs — extension list (tables, fenced_code, attr_list) — confirmed in library changelog
- bleach docs — allowlist-based SVG sanitization pattern is documented use case

### Tertiary (LOW confidence)
- mmdc subprocess invocation pattern — based on @mermaid-js/mermaid-cli README; exact flags may vary with version 11.x

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all library versions confirmed against PyPI/npm 2026-03-22
- Architecture: HIGH — integration points confirmed by reading actual source files
- Pitfalls: HIGH for math/Pygments/SVG; MEDIUM for mmdc (newer tool, less battle-tested in this stack)

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (30 days; mmdc check sooner if npm publish rate is high)
