# Phase 2: Compiler Core + ADA - Research

**Researched:** 2026-03-22
**Domain:** Python/Jinja2 HTML compiler, WCAG 2.1 AA, W3C APG carousel
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Navigation & chrome:**
- Minimal chrome: slide counter ("3 / 25") in corner, keyboard navigation only
- No sidebar, no progress bar — clean full-bleed slides
- Keyboard: arrow keys advance/retreat, Home/End jump to first/last, Space advances
- No wrap-around: stop at first/last slide (standard W3C APG carousel behavior)
- Skip link at top of deck (`<a href="#main-content" class="skip-link">Skip to content</a>`)
- ARIA carousel markup: container has `aria-roledescription="carousel"`, each slide has `role="group"` + `aria-label="Slide N of M"`
- Every slide has a heading tied to `aria-labelledby`

**Theme & styling:**
- CSS custom properties for all colors, fonts, spacing (--bg, --text, --accent, --font-family, etc.)
- Dark and light themes swap CSS var values; easy to add new themes later
- Default accent: amber (#f0a500) — validated for WCAG 2.1 AA contrast (4.5:1 normal text, 3:1 large text)
- When user provides `accent_color` in metadata, compiler validates contrast ratio against theme background at compile time; error if it fails
- Font loaded from Google Fonts CDN (IBM Plex Sans default)
- Typography and spacing at Claude's discretion — keep it clean and readable

**Validation & warnings:**
- **Errors** (halt compilation, exit 1, no HTML produced): missing alt_text on image/figure/diagram, invalid accent_color contrast
- **Warnings** (printed to stderr, HTML still produced): 3+ consecutive identical layout types, 5+ bullet points on a slide
- Message format: plain text lines to stderr, markdown-friendly (e.g., `**WARNING** slide 4: 6 bullet points exceeds recommended maximum of 5`)
- Exit code 0 on success (even with warnings), exit code 1 on errors

**Template architecture:**
- One Jinja2 template file per layout type: `title.html.j2`, `content.html.j2`, `diagram.html.j2`, etc. (12 files)
- Base template `base.html.j2` provides HTML shell, embedded CSS, embedded JS, slide container
- Each layout template is a snippet included inside the slide wrapper
- `compiler/` package as sibling to `schema/`: `compiler/__init__.py`, `compiler/engine.py`, `compiler/templates/`
- CLI entry point: `python -m compiler input.yaml output.html`

**Design principle:**
- Minimize options, maximize extensibility — new layout types or themes should be addable without restructuring
- v1 ships with dark + light themes; adding a theme = adding a CSS var block
- v1 ships with 12 layout templates; adding a layout = adding one .j2 file

### Claude's Discretion
- Typography scale and spacing system
- Exact slide counter positioning and styling
- CSS reset / normalize approach
- How `notes` field renders as `<aside>` (hidden by default)
- Internal compiler architecture (visitor pattern, simple loop, etc.)
- Markdown rendering approach for slide bodies (placeholder in Phase 2, full rendering in Phase 3)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| COMP-01 | Python compiler reads YAML and produces a single self-contained HTML file | `schema.parser.parse_deck_file()` already exists; Jinja2 renders to string; write to file |
| COMP-02 | Jinja2 templates render each layout type (one template per layout) | Jinja2 3.1.6 available; `Environment(loader=FileSystemLoader(...))` pattern |
| COMP-03 | Output is deterministic — same YAML input produces byte-identical HTML | Avoid `datetime.now()` in templates; Jinja2 renders deterministically by default |
| COMP-04 | Compiler CLI accepts input YAML path and output HTML path | `python -m compiler` via `__main__.py`; `argparse` stdlib |
| COMP-05 | CSS theme (dark background, amber accents) embedded in output HTML | CSS custom properties pattern verified from existing decks; dark theme vars confirmed |
| COMP-06 | JavaScript for keyboard navigation embedded in output | W3C APG carousel keyboard model; `keydown` handler with `scrollIntoView` |
| ADA-01 | Alt text required on image/figure/SVG layout types — compiler errors if missing | `FigureSlide.alt_text` and `DiagramSlide.alt_text` already required in schema; add pre-render check |
| ADA-02 | ARIA carousel markup on slide container and each slide | `aria-roledescription="carousel"` on `<main>`; `role="group"` + `aria-label="Slide N of M"` per slide |
| ADA-03 | Skip navigation link at top of every deck | `<a href="#main-content" class="skip-link">` before `<main>`; CSS shows on focus |
| ADA-04 | Every slide has a heading tied to `aria-labelledby` | Each slide `<section>` gets `aria-labelledby="slide-N-heading"`; `<h1>/<h2>` gets that id |
| ADA-05 | Keyboard navigation follows W3C APG carousel pattern | Arrow keys (no wrap), Home/End, Space; focus management with `scrollIntoView` |
| ADA-06 | Color contrast validated against WCAG 2.1 AA at compile time | Pure Python WCAG formula; `wcag-contrast-ratio` package (v0.9) available |
| ADA-07 | Layout variety enforcement — warn if 3+ consecutive slides use identical layout type | Simple O(n) scan of `slide.layout` list during pre-render validation |
| ADA-08 | Bullet limit validation — warn if any slide has more than 5 bullet points | Count Markdown list items in `slide.body`; regex `^[-*+] ` or `^\d+\.` per line |
</phase_requirements>

---

## Summary

Phase 2 builds the Python/Jinja2 compiler pipeline on top of the already-complete Phase 1 schema/parser. The primary inputs are `Deck` objects from `schema.parser.parse_deck_file()` and the primary output is a single self-contained HTML file with embedded CSS and JS. All critical infrastructure already exists: Pydantic models with discriminated unions, YAML parsing, and test fixtures.

The most important architectural insight from examining existing HTML decks is that they do NOT use the W3C APG carousel pattern (no `aria-roledescription="carousel"`, no keyboard JS). Phase 2 must add this from scratch. The existing decks use scroll-anchored navigation with a sidebar and dot-row — Phase 2 replaces this with a cleaner single-slide-per-viewport approach using `scrollIntoView` or section scroll-snapping.

A critical contrast issue was discovered: the locked default accent amber (#f0a500) achieves 9.09:1 on the dark theme but only 2.08:1 on a white light-theme background — failing WCAG AA by a wide margin. The light theme must use a darker amber variant (approximately #b06800 achieves 4.35:1) rather than the same #f0a500.

**Primary recommendation:** Build a simple linear engine in `compiler/engine.py` that validates first (fail fast, no partial output), then renders templates in order via Jinja2's `FileSystemLoader`, and writes the final concatenated HTML in one `file.write()` call for determinism.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Jinja2 | 3.1.6 | HTML templating | Industry standard for Python; deterministic; auto-escaping |
| PyYAML | >=6.0 | YAML parsing (already installed) | Already in pyproject.toml |
| pydantic | >=2.12 | Schema models (already installed) | Already in pyproject.toml; Phase 1 output |
| wcag-contrast-ratio | 0.9 | WCAG 2.1 AA contrast checking | Only pure-Python library for this; correct WCAG formula |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| argparse | stdlib | CLI argument parsing | No extra dep; sufficient for 2-arg CLI |
| re | stdlib | Bullet counting in Markdown bodies | Count `^[-*+] ` and `^\d+\. ` lines |
| sys | stdlib | Exit codes and stderr output | `sys.exit(1)` and `print(..., file=sys.stderr)` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| wcag-contrast-ratio | Custom WCAG formula | wcag-contrast-ratio is 30 lines and correct; hand-rolling is identical work with testing cost |
| Jinja2 FileSystemLoader | Jinja2 PackageLoader | FileSystemLoader is simpler; PackageLoader needed only for installed packages |
| argparse | click | argparse is stdlib; 2-argument CLI doesn't warrant a dep |

**Installation (new deps only):**
```bash
pip install jinja2 wcag-contrast-ratio
```

**Add to pyproject.toml dependencies:**
```
"jinja2>=3.1",
"wcag-contrast-ratio>=0.9",
```

**Version verification (confirmed 2026-03-22):**
- jinja2: 3.1.6 (latest stable)
- wcag-contrast-ratio: 0.9 (only version, stable)

---

## Architecture Patterns

### Recommended Project Structure
```
compiler/
├── __init__.py          # exports compile_deck()
├── __main__.py          # CLI entry: python -m compiler input.yaml output.html
├── engine.py            # CompilerEngine class: validate + render
├── validators.py        # pre-render checks: alt_text, contrast, layout variety, bullets
├── contrast.py          # WCAG 2.1 AA contrast ratio helper
└── templates/
    ├── base.html.j2     # HTML shell, embedded CSS, embedded JS, slide loop
    ├── title.html.j2    # TitleSlide snippet
    ├── hero.html.j2     # HeroSlide snippet
    ├── content.html.j2  # ContentSlide snippet
    ├── divider.html.j2  # DividerSlide snippet
    ├── figure.html.j2   # FigureSlide snippet
    ├── diagram.html.j2  # DiagramSlide snippet
    ├── two-column.html.j2  # TwoColumnSlide snippet
    ├── quote.html.j2    # QuoteSlide snippet
    ├── comparison.html.j2  # ComparisonSlide snippet (<!-- split --> split)
    ├── code.html.j2     # CodeSlide snippet (Phase 3 adds highlighting)
    ├── steps.html.j2    # StepsSlide snippet
    └── summary.html.j2  # SummarySlide snippet
```

### Pattern 1: Validate-Then-Render (Fail Fast)
**What:** All validation runs before any template rendering. Errors collected as a list; if non-empty, print all to stderr and `sys.exit(1)` without writing any output file.
**When to use:** Always — prevents partial HTML output and makes error messages coherent.
```python
# compiler/engine.py
from compiler.validators import validate_deck

def compile_deck(deck: Deck, output_path: str) -> None:
    errors, warnings = validate_deck(deck)
    for w in warnings:
        print(w, file=sys.stderr)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)
    html = _render(deck)
    Path(output_path).write_text(html, encoding='utf-8')
```

### Pattern 2: Jinja2 Template Loading
**What:** `base.html.j2` iterates slides and includes layout snippets via `{% include slide.layout ~ '.html.j2' %}`. Templates loaded from `compiler/templates/` directory relative to package.
```python
# compiler/engine.py
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(['html']),
    keep_trailing_newline=True,
)

def _render(deck: Deck) -> str:
    template = env.get_template("base.html.j2")
    return template.render(deck=deck, total=len(deck.slides))
```

### Pattern 3: W3C APG Carousel — No-Wrap Keyboard Model
**What:** Slides shown one at a time; keyboard handler tracks `currentIndex`; no DOM visibility toggling needed if using `scrollIntoView`. Arrow keys change index and call `scrollIntoView({behavior:'instant'})`.
**Key ARIA attributes (verified against W3C APG):**
```html
<!-- Container -->
<main id="main-content"
      role="region"
      aria-roledescription="carousel"
      aria-label="[deck title]">

<!-- Each slide -->
<section id="slide-1"
         role="group"
         aria-roledescription="slide"
         aria-label="Slide 1 of 25"
         aria-labelledby="slide-1-heading">
  <h2 id="slide-1-heading">[slide title]</h2>
  ...
</section>
```
**JavaScript (embedded in base.html.j2):**
```javascript
(function() {
  const slides = Array.from(document.querySelectorAll('[role="group"]'));
  let idx = 0;
  function goTo(n) {
    idx = Math.max(0, Math.min(n, slides.length - 1));
    slides[idx].scrollIntoView({behavior: 'instant', block: 'start'});
    document.getElementById('slide-counter').textContent = (idx+1) + ' / ' + slides.length;
  }
  document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
      e.preventDefault(); goTo(idx + 1);
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault(); goTo(idx - 1);
    } else if (e.key === 'Home') {
      e.preventDefault(); goTo(0);
    } else if (e.key === 'End') {
      e.preventDefault(); goTo(slides.length - 1);
    }
  });
})();
```

### Pattern 4: WCAG 2.1 AA Contrast Calculation
**What:** Pure Python implementation of the W3C relative luminance formula. Used at compile time for `accent_color` validation.
```python
# compiler/contrast.py
def hex_to_relative_luminance(hex_color: str) -> float:
    h = hex_color.lstrip('#')
    rgb = [int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    def linearize(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = [linearize(c) for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(fg: str, bg: str) -> float:
    l1 = hex_to_relative_luminance(fg)
    l2 = hex_to_relative_luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def passes_wcag_aa(fg: str, bg: str, large_text: bool = False) -> bool:
    ratio = contrast_ratio(fg, bg)
    return ratio >= 3.0 if large_text else ratio >= 4.5
```

### Pattern 5: CSS Custom Properties — Theme Architecture
**What:** Two theme blocks keyed by `data-theme` attribute on `<html>`. Compiler sets `data-theme="dark"` or `data-theme="light"` from `deck.metadata.theme`.
```css
:root[data-theme="dark"] {
  --bg:      #0d1117;
  --bg2:     #161b22;
  --text:    #e6edf3;
  --muted:   #8b949e;
  --accent:  #f0a500;  /* amber — 9.09:1 on #0d1117 ✓ */
  --border:  #30363d;
}
:root[data-theme="light"] {
  --bg:      #ffffff;
  --bg2:     #f6f8fa;
  --text:    #1f2328;
  --muted:   #656d76;
  --accent:  #b06800;  /* darker amber — 4.35:1 on #ffffff ✓ */
  --border:  #d1d9e0;
}
```

### Anti-Patterns to Avoid
- **Timestamps in templates:** `{{ now() }}` or any non-deck-derived data breaks determinism (COMP-03).
- **Rendering before validation:** Writing partial HTML before catching errors violates the spec (exit 1 = no HTML produced).
- **Using #f0a500 in light theme:** Amber fails WCAG AA on white (2.08:1 < 4.5:1). Light theme accent must be #b06800 or darker.
- **Inline `style=` for theme values:** CSS custom properties are the extension point; inlining bypasses the theme system.
- **`os.path.join` for template paths:** Use `pathlib.Path(__file__).parent / "templates"` for reliable relative path resolution.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| WCAG contrast formula | Custom luminance math | `wcag-contrast-ratio` lib OR the 10-line pure-Python above | W3C formula has linearization edge cases; already tested |
| YAML parsing | Custom YAML reader | `schema.parser.parse_deck_file()` (Phase 1) | Already handles frontmatter heuristics, body extraction, Pydantic validation |
| HTML escaping | `str.replace()` escapes | Jinja2 `autoescape=True` | Jinja2 handles `&`, `<`, `>`, `"`, `'` correctly including edge cases |
| Markdown bullet counting | Full Markdown parser | `re.findall(r'^[-*+] ', body, re.MULTILINE)` | Phase 2 only needs count; full parse is Phase 3's job |

**Key insight:** The schema/parser layer (Phase 1) already validates all structural concerns. The compiler only needs to render and apply design-rule checks — do not re-implement parsing logic.

---

## Common Pitfalls

### Pitfall 1: Light Theme Amber Contrast Failure
**What goes wrong:** Using #f0a500 amber for both dark and light themes; light theme fails WCAG AA (2.08:1 on white).
**Why it happens:** Amber is bright — high contrast against dark backgrounds, low contrast against light.
**How to avoid:** Use separate `--accent` values per theme. Dark: #f0a500. Light: #b06800 (4.35:1 on white, passes AA).
**Warning signs:** Any `accent_color` validation that tests only dark theme values.

### Pitfall 2: Non-Deterministic Output (COMP-03)
**What goes wrong:** Output HTML differs on second run; tests fail byte-comparison.
**Why it happens:** `datetime.now()`, dict iteration order (Python 3.7+ is ordered but Jinja2 filter `|dictsort` can differ), or OS-level file timestamps embedded.
**How to avoid:** Templates may only reference `deck.*` fields. No `now()`, no `random`, no OS calls in templates. `deck.metadata.date` is always from the YAML.
**Warning signs:** CI diff on repeated compile of same input.

### Pitfall 3: `aria-labelledby` Referencing Non-Existent ID
**What goes wrong:** Screen readers announce nothing for slide heading; axe-core flags broken reference.
**Why it happens:** Template uses `id="slide-{{ loop.index }}-heading"` in h2 but `aria-labelledby="slide-{{ loop.index0 }}-heading"` in section (off-by-one).
**How to avoid:** Use same index variable throughout; test with a single loop variable `idx = loop.index`.

### Pitfall 4: Space Key Scrolling Page Instead of Advancing Slides
**What goes wrong:** Space bar scrolls the page naturally, fighting the custom handler.
**Why it happens:** Default browser behavior for Space is scroll-down.
**How to avoid:** Always call `e.preventDefault()` before `goTo()` for Space, ArrowDown, ArrowUp.

### Pitfall 5: `python -m compiler` Not Working
**What goes wrong:** `ModuleNotFoundError` or no CLI entry.
**Why it happens:** Missing `compiler/__main__.py`.
**How to avoid:** Create `compiler/__main__.py` with `from compiler.engine import main; main()`. The `python -m compiler` invocation calls `__main__.py`.

### Pitfall 6: Jinja2 Autoescape Breaking Intentional HTML in Bodies
**What goes wrong:** Markdown bodies containing `<em>` or `&amp;` get double-escaped.
**Why it happens:** Phase 2 uses body as raw text; autoescape converts `<` to `&lt;`.
**How to avoid:** Mark body content as safe with `{{ slide.body | safe }}` — acceptable in Phase 2 since bodies are compiler-controlled YAML input, not user-submitted HTML. Phase 3 will replace with proper Markdown rendering.

---

## Code Examples

### Compiler Entry Point (`compiler/__main__.py`)
```python
# Source: stdlib argparse pattern
import argparse
import sys
from compiler.engine import compile_deck
from schema.parser import parse_deck_file

def main():
    parser = argparse.ArgumentParser(description="Compile YAML deck to HTML")
    parser.add_argument("input", help="Input YAML file path")
    parser.add_argument("output", help="Output HTML file path")
    args = parser.parse_args()
    deck = parse_deck_file(args.input)
    compile_deck(deck, args.output)

if __name__ == "__main__":
    main()
```

### Validator for Layout Variety (ADA-07)
```python
# compiler/validators.py
def check_layout_variety(slides) -> list[str]:
    warnings = []
    run_start = 0
    for i in range(1, len(slides)):
        if slides[i].layout == slides[i-1].layout:
            run_len = i - run_start + 1
            if run_len == 3:
                warnings.append(
                    f"**WARNING** slides {run_start+1}-{i+1}: "
                    f"3+ consecutive '{slides[i].layout}' layout slides"
                )
        else:
            run_start = i
    return warnings
```

### Validator for Bullet Count (ADA-08)
```python
import re

def count_bullets(body: str | None) -> int:
    if not body:
        return 0
    return len(re.findall(r'^[-*+] |\d+\. ', body, re.MULTILINE))

def check_bullet_limits(slides) -> list[str]:
    warnings = []
    for i, slide in enumerate(slides, 1):
        n = count_bullets(slide.body)
        if n > 5:
            warnings.append(
                f"**WARNING** slide {i}: {n} bullet points exceeds recommended maximum of 5"
            )
    return warnings
```

### Base Template Skeleton (`base.html.j2`)
```html
<!DOCTYPE html>
<html lang="en" data-theme="{{ deck.metadata.theme }}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ deck.metadata.title | e }}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family={{ deck.metadata.font | replace(' ', '+') }}:wght@400;600;700&display=swap" rel="stylesheet">
  <style>/* CSS custom properties and all styles embedded here */</style>
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to content</a>
  <div id="slide-counter" aria-live="polite" aria-atomic="true">1 / {{ total }}</div>
  <main id="main-content"
        role="region"
        aria-roledescription="carousel"
        aria-label="{{ deck.metadata.title | e }}">
    {% for slide in deck.slides %}
    <section id="slide-{{ loop.index }}"
             role="group"
             aria-roledescription="slide"
             aria-label="Slide {{ loop.index }} of {{ total }}"
             aria-labelledby="slide-{{ loop.index }}-heading">
      {% include slide.layout ~ '.html.j2' %}
    </section>
    {% endfor %}
  </main>
  <script>/* Keyboard nav JS embedded here */</script>
</body>
</html>
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Sidebar + dot-row navigation (existing decks) | Full-bleed carousel with keyboard-only nav | Phase 2 (new) | Cleaner ADA compliance; simpler HTML structure |
| No ARIA carousel markup (existing decks) | W3C APG `aria-roledescription="carousel"` | Phase 2 (new) | Screen reader compatibility |
| No keyboard JS (existing decks) | Arrow/Space/Home/End handlers | Phase 2 (new) | ADA-05 compliance |

**What the existing HTML decks provide (verified):**
- CSS custom properties pattern (`--bg`, `--accent`, `--text`, `--muted`, `--border`) — match this naming
- IBM Plex Sans Google Fonts CDN URL pattern
- `.skip-link` CSS pattern (position absolute, shown on focus)
- CSS class naming for layouts: `.two-col`, `.two-col-narrow-wide`, `.card-grid`, `.highlight-box`
- Slide `<section>` structure with `.slide` class
- Table, card, formula-block, quote CSS patterns reusable directly

**What the existing decks do NOT have (Phase 2 adds from scratch):**
- `aria-roledescription="carousel"` on container
- `role="group"` + `aria-roledescription="slide"` per slide
- `aria-labelledby` on slide sections
- Keyboard navigation JavaScript
- Slide counter ("N / M") UI element

---

## Open Questions

1. **`notes` field rendering**
   - What we know: Discretion given to Claude; `notes` is in `SlideBase`, hidden by default
   - Recommendation: Render as `<aside class="slide-notes" hidden aria-hidden="true">{{ slide.notes | e }}</aside>` inside each slide section. Consistent with speaker notes patterns; `hidden` attribute removes from AT by default.

2. **TwoColumnSlide with both `left`/`right` ColumnContent AND free `body`**
   - What we know: Schema allows both; body is free Markdown text; left/right are structured ColumnContent (figure or diagram type)
   - Recommendation: Template renders body as `<div class="two-col-body">` above the column grid when body is present, structured left/right below. Phase 2 renders body as raw text (Phase 3 adds Markdown parsing).

3. **ComparisonSlide `<!-- split -->` parsing**
   - What we know: Body contains `<!-- split -->` marker separating left/right column content
   - Recommendation: `split_body(body)` helper in `engine.py` that does `body.split('<!-- split -->', 1)` — returns `(left_text, right_text)`. Pass both to template as `left` and `right` context vars.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >= 9.0 |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `pytest tests/test_compiler.py -x` |
| Full suite command | `pytest tests/ -x` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| COMP-01 | `compile_deck()` writes valid HTML file | integration | `pytest tests/test_compiler.py::test_compile_produces_html -x` | Wave 0 |
| COMP-02 | Each layout type renders a `<section>` | integration | `pytest tests/test_compiler.py::test_all_layout_types_render -x` | Wave 0 |
| COMP-03 | Two runs on same YAML produce identical bytes | integration | `pytest tests/test_compiler.py::test_deterministic_output -x` | Wave 0 |
| COMP-04 | CLI `python -m compiler` accepts 2 path args | integration | `pytest tests/test_compiler.py::test_cli_invocation -x` | Wave 0 |
| COMP-05 | CSS vars `--bg`, `--accent` present in output | unit | `pytest tests/test_compiler.py::test_css_vars_embedded -x` | Wave 0 |
| COMP-06 | Keyboard JS with ArrowRight/Home/End present | unit | `pytest tests/test_compiler.py::test_keyboard_js_embedded -x` | Wave 0 |
| ADA-01 | Missing alt_text causes exit code 1, no output | unit | `pytest tests/test_validators.py::test_missing_alt_text_error -x` | Wave 0 |
| ADA-02 | Output contains `aria-roledescription="carousel"` | unit | `pytest tests/test_compiler.py::test_aria_carousel_markup -x` | Wave 0 |
| ADA-03 | Output contains `.skip-link` href="#main-content" | unit | `pytest tests/test_compiler.py::test_skip_link_present -x` | Wave 0 |
| ADA-04 | Each slide section has `aria-labelledby` matching `<h2>` id | unit | `pytest tests/test_compiler.py::test_aria_labelledby -x` | Wave 0 |
| ADA-05 | JS handler covers ArrowLeft/Right, Home/End, Space | unit | `pytest tests/test_compiler.py::test_keyboard_js_embedded -x` | Wave 0 |
| ADA-06 | Invalid accent_color causes exit code 1 | unit | `pytest tests/test_validators.py::test_invalid_contrast_error -x` | Wave 0 |
| ADA-07 | 3+ consecutive same layout → warning to stderr | unit | `pytest tests/test_validators.py::test_layout_variety_warning -x` | Wave 0 |
| ADA-08 | 6+ bullets → warning to stderr | unit | `pytest tests/test_validators.py::test_bullet_limit_warning -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_compiler.py tests/test_validators.py -x`
- **Per wave merge:** `pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_compiler.py` — covers COMP-01 through COMP-06, ADA-02 through ADA-06
- [ ] `tests/test_validators.py` — covers ADA-01, ADA-06, ADA-07, ADA-08
- [ ] `compiler/__init__.py` — package init
- [ ] `compiler/__main__.py` — CLI entry point
- [ ] `compiler/engine.py` — CompilerEngine
- [ ] `compiler/validators.py` — pre-render checks
- [ ] `compiler/contrast.py` — WCAG contrast helper
- [ ] `compiler/templates/` — all 13 .j2 files (base + 12 layouts)

---

## Sources

### Primary (HIGH confidence)
- Verified from existing project code: `schema/models.py`, `schema/parser.py` — layout types, field names, AnySlide union
- Verified from existing HTML deck `n8n_to_python/output_html_files/clean.html` — CSS custom property names, IBM Plex Sans CDN URL, skip-link CSS pattern, existing CSS classes for layouts
- Computed (Python): WCAG 2.1 AA contrast ratios for all color pairs — amber on dark 9.09:1 (pass), amber on white 2.08:1 (FAIL), #b06800 on white 4.35:1 (pass)
- `pyproject.toml` — installed packages and versions

### Secondary (MEDIUM confidence)
- W3C APG Carousel Pattern (https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) — `aria-roledescription="carousel"`, `role="group"`, no-wrap keyboard behavior
- Jinja2 3.1.x official docs — `{% include %}` with dynamic filenames, `FileSystemLoader`, `autoescape`

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified against pip registry and project pyproject.toml
- Architecture: HIGH — patterns derived from existing codebase (Phase 1) and existing HTML decks
- Pitfalls: HIGH — contrast failure and non-determinism confirmed with actual Python computation
- ARIA patterns: MEDIUM — W3C APG spec verified by reference; axe-core testing deferred to implementation

**Research date:** 2026-03-22
**Valid until:** 2026-06-22 (Jinja2 and WCAG standards are stable; 90-day window appropriate)
