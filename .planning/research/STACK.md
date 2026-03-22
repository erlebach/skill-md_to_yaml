# Stack Research

**Domain:** YAML-to-HTML presentation DSL compiler (Python)
**Researched:** 2026-03-21
**Confidence:** HIGH (core stack) / MEDIUM (Mermaid rendering)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ | Compiler runtime | Ships everywhere, no Node.js runtime needed, excellent templating and parsing ecosystem |
| PyYAML | 6.0.3 | Parse YAML DSL input | Standard library, `yaml.safe_load()` is safe and fast; YAML 1.1 is sufficient for this DSL since we control the schema |
| Pydantic v2 | 2.12.x | Schema validation of parsed YAML | Type-safe models with automatic error messages; catches malformed DSL before compilation begins; v2 is significantly faster than v1 |
| Jinja2 | 3.1.6 | HTML template rendering | Industry standard for Python → HTML; partials, macros, and filters map cleanly to slide layout primitives; deterministic output |
| Pygments | 2.19.2 | Code block syntax highlighting | Pure Python; 598+ language lexers; outputs inline HTML with CSS classes; integrates trivially into Jinja2 filters |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| mmdc | latest (PyPI) | Mermaid diagram → inline SVG, no Node.js required | Any slide containing a `type: mermaid` block; pure Python via PhantomJS/phasma |
| markdown-katex | latest (PyPI) | LaTeX math → HTML/MathML, bundles KaTeX binary | Any slide with `latex:` fields; avoids requiring Node.js or separate katex install |
| pytest | 8.x | Test compiler output correctness | Unit tests for each layout primitive, regression tests against reference HTML decks |
| playwright + axe-core | playwright 1.x | WCAG 2.1 AA automated accessibility checks | CI validation gate; axe-core catches ~57% of WCAG issues automatically |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Fast Python package manager and venv creation | Replaces pip + virtualenv; `uv pip install` is drop-in compatible |
| ruff | Linting and formatting | Replaces flake8 + black + isort in one tool; zero-config |
| pyright | Static type checking | Validates Pydantic models and Jinja2 filter signatures |

## Installation

```bash
# Core compiler
pip install PyYAML==6.0.3 Jinja2==3.1.6 pydantic==2.12.3 Pygments==2.19.2

# Diagram and math rendering
pip install mmdc markdown-katex

# Testing
pip install pytest playwright
playwright install chromium

# Dev tools
pip install ruff pyright
```

Using uv (recommended):
```bash
uv pip install pyyaml jinja2 pydantic pygments mmdc markdown-katex
uv pip install --dev pytest playwright ruff pyright
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| PyYAML 6.0.3 | ruamel.yaml | When roundtrip comment preservation matters; not needed here since we only read, never write back |
| Pydantic v2 | jsonschema + cerberus | If you need JSON Schema compatibility for external tooling; Pydantic gives better DX for Python-native DSLs |
| Jinja2 | Mako / Chameleon | Mako is faster for pure Python-heavy templates; Jinja2 wins for maintainability and ecosystem familiarity |
| mmdc (Python-native) | mermaid-js/mermaid-cli (npm) | If you already have Node.js in the build environment and want the official renderer; mmdc avoids the Node.js dependency entirely |
| markdown-katex | katex npm CLI + subprocess | markdown-katex bundles the binary; use the npm CLI only if you need KaTeX version control independent of PyPI |
| Pygments | highlight.js (client-side) | highlight.js is simpler if you accept client-side JS; Pygments is better for fully standalone offline HTML |
| playwright + axe-core | pa11y / wave API | pa11y is simpler CLI; axe-core has broader WCAG coverage and is the most widely adopted engine |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| MathJax | 10x heavier than KaTeX; much slower browser render; existing decks already use KaTeX CDN | KaTeX (via markdown-katex for compilation, CDN link in output HTML) |
| Sphinx or MkDocs | These are documentation site generators, not slide compilers; wrong abstraction level; add enormous overhead | Custom Jinja2 templates |
| Reveal.js or Impress.js | JavaScript-driven slide frameworks; add client-side complexity and break the "standalone HTML" constraint cleanly | Custom scroll-snap CSS matching existing deck style |
| pydantic-yaml (PyPI package) | Thin wrapper with no active maintenance signal; standard `yaml.safe_load()` + `model_validate()` is simpler and more explicit | PyYAML + Pydantic v2 directly |
| Marko / mistune markdown parsers | Markdown is the input format to the Claude skill, not the compiler; the compiler only sees YAML | PyYAML |
| Node.js in the compiler | Adds a runtime dependency that breaks the "pure Python" portability goal | mmdc (Python-native) and markdown-katex (bundles binary) |

## Stack Patterns by Variant

**If a slide contains `type: code`:**
- Use Pygments `HtmlFormatter(style='monokai', noclasses=False)` to produce CSS-class-based highlighting
- Embed the formatter CSS once in the HTML `<head>` via a Jinja2 block
- This keeps the output self-contained without inline styles per code block

**If a slide contains `type: mermaid`:**
- At compile time, call `mmdc` to render the Mermaid source to SVG string
- Inline the SVG directly in the HTML — no CDN, no JavaScript required at render time
- Fall back to a `<figure>` with an error message if mmdc fails; never silently drop content

**If a slide contains LaTeX (`latex:` field):**
- Use `markdown-katex` to pre-render to HTML at compile time
- Keep the KaTeX CDN stylesheet link in `<head>` for font loading
- KaTeX's server-side output requires `style-src 'unsafe-inline'` in CSP — document this

**If validating ADA compliance in CI:**
- Run `playwright` headless with `@axe-core/playwright` against the generated HTML file
- Assert zero violations for tags `wcag2aa` and `wcag21aa`
- This catches missing alt text, contrast failures, missing ARIA labels automatically

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| pydantic==2.12.x | Python 3.8–3.14 | v2 API (BaseModel, model_validate) — do not use v1 field syntax |
| Jinja2==3.1.6 | Python 3.7+ | Requires MarkupSafe>=2.0 (auto-installed) |
| PyYAML==6.0.3 | Python 3.8+ | Always use `yaml.safe_load()`, never `yaml.load()` (security) |
| Pygments==2.19.2 | Python 3.8+ | No known conflicts with above |
| playwright | Python 3.8+ | Requires separate `playwright install chromium` after pip install |

## Sources

- [Jinja2 PyPI](https://pypi.org/project/Jinja2/) — version 3.1.6 confirmed, released 2025-03-05 (HIGH confidence)
- [PyYAML PyPI](https://pypi.org/project/PyYAML/) — version 6.0.3 confirmed, released 2025-09-25 (HIGH confidence)
- [Pygments PyPI libraries.io](https://libraries.io/pypi/Pygments) — version 2.19.2 confirmed, released 2025-06-21 (HIGH confidence)
- [Pydantic v2.12 announcement](https://pydantic.dev/articles/pydantic-v2-12-release) — v2.12.x stable (HIGH confidence)
- [mmdc GitHub](https://github.com/mohammadraziei/mmdc) — Python-native, no Node.js, actively maintained as of 2026-01 (MEDIUM confidence — newer project, verify stability before production use)
- [markdown-katex PyPI](https://pypi.org/project/markdown-katex/) — bundles KaTeX binary, no Node.js required (MEDIUM confidence — verify KaTeX version bundled matches CDN version used in output)
- [axe-core GitHub](https://github.com/dequelabs/axe-core) — 3B+ downloads, WCAG 2.1 AA tag support confirmed (HIGH confidence)
- [KaTeX API docs](https://katex.org/docs/api) — server-side pre-rendering confirmed, CSP `unsafe-inline` requirement documented (HIGH confidence)

---
*Stack research for: YAML-to-HTML slide DSL compiler*
*Researched: 2026-03-21*
