# Pitfalls Research

**Domain:** Presentation DSL compiler — YAML-to-HTML slide generation
**Researched:** 2026-03-21
**Confidence:** HIGH (critical pitfalls verified via multiple sources); MEDIUM (LLM schema pitfalls); HIGH (ADA/WCAG)

---

## Critical Pitfalls

### Pitfall 1: Mermaid Cannot Be Rendered Server-Side Without a Headless Browser

**What goes wrong:**

The compiler is designed to be a deterministic Python process. Mermaid diagrams look like they can be "compiled" by calling a Node.js library, but Mermaid.js requires a real DOM environment to compute element widths and heights before emitting SVG. Attempting to invoke `mermaid.render()` in a headless Node context with jsdom or happy-dom silently fails or produces malformed SVG. The Mermaid CLI uses Puppeteer (a full headless Chromium) under the hood.

**Why it happens:**

Mermaid is architected for browser-side rendering. Server-side use is a community workaround, not a first-class design target. Developers assume "Node.js library" means server-safe.

**How to avoid:**

Choose one strategy before writing the compiler:
- Use `@mermaid-js/mermaid-cli` (mmdc) — launches Puppeteer, accepts `.mmd` files, outputs SVG. Adds a Node/Chromium dependency to the build.
- Accept Mermaid source as a code block in the YAML, defer client-side rendering to the browser (add `<script>` tag in output HTML). This avoids the build dependency but makes the HTML not self-contained for static viewing.
- Treat Mermaid diagrams as a first-class primitive in the YAML DSL and document the dependency clearly.

**Warning signs:**

- The compiler "works" in development (where Node and a browser are available) but fails in CI or on a new machine with no GUI environment.
- SVG output has `undefined` or `NaN` in width/height attributes.

**Phase to address:** Phase — Build Python Compiler (before writing the Mermaid handler, decide and document the strategy; do not discover this mid-implementation)

---

### Pitfall 2: YAML DSL Schema Designed Too Wide — LLM Reliably Generates Subset Only

**What goes wrong:**

A schema with 15+ layout types, each with 6-10 optional fields, creates a combinatorial space that an LLM explores inconsistently. The LLM will reliably use 5-7 layouts and silently omit or misname fields in the others. Result: the compiler receives structurally valid YAML that produces incorrect output for less-common layouts, and these failures are invisible unless test coverage includes every layout type.

**Why it happens:**

Complex schemas impose cognitive load on the LLM during generation. Research shows 10-15% performance degradation when models must adhere to complex structured output schemas. Union types and discriminated field sets (where field meaning changes based on `type:`) are especially error-prone. The LLM learns to avoid uncertain layouts.

**How to avoid:**

- Keep the "type" discriminator simple — each layout type should have exactly the same set of required fields with the same semantics. Variable-meaning fields (`content` means a string on one type and a list on another) are a schema smell.
- Flatten nested structures. Prefer `title: "..."` at the top level over `header: {text: "...", level: 2}`.
- Validate YAML output against the schema (pydantic or jsonschema) before passing to the compiler. Fail loudly with a useful error when the LLM drifts.
- Write the `/md_to_yaml` skill prompt with one worked example per layout type — not a prose description.

**Warning signs:**

- The LLM stops using `slide--figure` or `slide--diagram` primitives across several generated decks.
- A layout type appears in the YAML but produces blank content in the compiled HTML.
- The LLM starts inventing field names not in the schema (e.g., `body:` instead of `content:`).

**Phase to address:** Phase — Define YAML DSL Schema (design with LLM generation constraints as a first-class requirement, not an afterthought)

---

### Pitfall 3: ADA Compliance Is Tested Automatically but 70% of Violations Are Invisible to Automation

**What goes wrong:**

The compiler emits HTML with alt tags, ARIA labels, and proper heading hierarchy. An automated audit tool (axe, Pa11y, Lighthouse) passes. But WCAG 2.1 AA violations remain: alt text is generic (`"diagram"` instead of describing the diagram content), heading levels skip from `h1` to `h3`, color contrast is borderline in the dark theme, and keyboard users cannot exit the slide carousel without Tab-trapping.

**Why it happens:**

Automated tools catch ~25-30% of WCAG issues. The remaining 70% require human or content-aware review. Template-level compliance (the compiler adds `alt=""`) does not mean content-level compliance (the LLM must fill in meaningful alt text). These are two different problems that look like the same problem until audited.

**How to avoid:**

- Separate structural compliance (compiler's responsibility) from content compliance (LLM and schema's responsibility).
- Require `alt_text` as a non-optional field in the YAML schema for every image, figure, and diagram slide. The compiler must raise an error if it is missing or an empty string.
- The compiler must validate heading sequence (no skipping levels) at compile time.
- Run axe-core against every compiled deck during CI. Flag manually that this catches only ~30% of issues.
- Test keyboard navigation manually: Tab into the deck, navigate all slides, Tab out of the deck. Verify focus never traps inside the scroll container.

**Warning signs:**

- The `/ada-slides-general` skill sometimes produces ADA violations in existing decks (acknowledged in PROJECT.md). The same patterns will recur unless alt text is enforced at the schema level.
- Focus ring disappears when navigating between slides via keyboard.
- Axe passes but a screen reader user cannot determine they are on "slide 3 of 12."

**Phase to address:** Phase — Define YAML DSL Schema (enforce `alt_text` as required), Phase — Build Python Compiler (structural ARIA, keyboard traps, heading validation), Phase — Validation

---

### Pitfall 4: Layout Variety Constraint Not Enforced at Compile Time

**What goes wrong:**

The PROJECT.md requirement "no 3 consecutive same layouts" is intended as a constraint on the LLM-generated YAML. If only the skill prompt enforces it (not the compiler), decks with monotonous layouts will silently pass and produce valid but visually poor output. Over time the LLM will drift toward generating bullet-list-only decks.

**Why it happens:**

It is easier to put design rules in prose instructions than to write validation logic. Prose instructions erode under model updates; programmatic validation does not.

**How to avoid:**

- Encode the "no 3 consecutive same layout" rule as a compiler validation step, not just a skill prompt instruction.
- Add a "layout variety score" check: if a deck has more than 60% of one layout type, emit a compiler warning (not an error, so the YAML is still usable, but the issue is surfaced).
- Include layout variety in the test suite: a deck failing the variety check should cause a test failure.

**Warning signs:**

- Reviewing 5 compiled decks and noticing that 4 of them are predominantly `slide--content` with bullets.
- The LLM prompt has a long list of negative instructions ("do not use more than 3 bullets", "do not repeat same layout") but no positive examples showing variety.

**Phase to address:** Phase — Build Python Compiler (add validation step), Phase — Create /md_to_yaml Skill (skill prompt must include positive variety examples)

---

### Pitfall 5: KaTeX Fails Silently on Unsupported LaTeX Commands

**What goes wrong:**

The Python compiler embeds LaTeX source in the HTML and KaTeX renders it client-side. If the source deck uses `\align`, `\boldsymbol`, or custom macros that KaTeX does not support, KaTeX renders a red error inline without the surrounding presentation failing. The presenter discovers broken math at presentation time, not at compile time.

**Why it happens:**

KaTeX supports a large subset of LaTeX but not all of it. In particular, `\align` (KaTeX requires `\aligned`), some color commands, and custom macros fail silently. The Python compiler has no way to verify KaTeX support without running KaTeX itself.

**How to avoid:**

- Document the list of unsupported KaTeX commands in the YAML DSL specification so the LLM knows not to generate them.
- Add a KaTeX pre-validation step using the Node.js `katex` library (`katex.renderToString(expr, {throwOnError: true})`) as a compile-time check. This requires Node.js as a build dependency.
- Alternatively, use KaTeX's `errorColor` option and add a post-compile grep of the output HTML for KaTeX error spans as a CI check.

**Warning signs:**

- Equations rendered with a red `\KaTeX parse error` span visible in the output HTML.
- Source decks use `\align` (should be `\aligned`), `\boldsymbol` (requires `boldsymbol` extension), or `\text{...}` inside display math.

**Phase to address:** Phase — Build Python Compiler (KaTeX validation step), Phase — Handle LaTeX/Math

---

### Pitfall 6: Self-Contained HTML Balloon — Embedded Images Make Files Impractically Large

**What goes wrong:**

PROJECT.md requires "self-contained HTML." If images (JPEG/PNG) are base64-embedded, a 25-slide deck with 6 figures can easily exceed 5-10MB as a single HTML file. This exceeds email attachment limits, bloats git history if committed, and slows browser load.

**Why it happens:**

"Self-contained" is interpreted as "everything embedded." But the existing decks (30-90KB HTML) achieve this by using SVG (which is XML text) and KaTeX (text), not raster images. Raster images break the self-contained assumption.

**How to avoid:**

- Define "self-contained" in the project spec: CSS, JS references, and SVG are embedded; raster images use file-relative paths or are referenced by URL.
- Add a compiler flag `--embed-images` that base64-encodes images for maximum portability, with a warning if output exceeds 2MB.
- Default behavior: write images adjacent to the HTML file and reference them with relative paths.
- Specify in the YAML DSL whether an image is embed-requested or reference-only.

**Warning signs:**

- First compiled deck with images is unexpectedly large (check with `ls -lh`).
- Opening the HTML in a browser is visibly slow.

**Phase to address:** Phase — Define YAML DSL Schema (image handling field), Phase — Build Python Compiler (image embedding strategy)

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| String-formatting HTML directly in Python (no Jinja2) | Faster initial implementation | Whitespace bugs, escaping errors, XSS if any user content reaches compiler | Never — use Jinja2 from day one |
| Optional `alt_text` field in schema | LLM generates YAML more easily | ADA violations in every deck with images | Never — make it required |
| Mermaid rendered client-side via `<script>` tag | No build dependency on Puppeteer | Output is not truly self-contained for offline use | Acceptable for v1 if documented |
| Single `slide--content` layout as fallback for all slides | Compiler never crashes | Monotonous decks, layout variety requirement violated silently | Never — validate layout at compile time |
| Skip heading level validation | Easier to implement | WCAG 1.3.1 violation, screen readers announce confusing structure | Never |
| Hardcode CSS inside Jinja2 templates | Simpler file structure | CSS changes require modifying every template | Never — use a single CSS file included by all templates |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| KaTeX (CDN) | Loading KaTeX CSS from CDN but forgetting `defer` on the JS tag, causing FOUC (flash of un-rendered math) | Use `<link>` for CSS in `<head>`, use `<script defer>` for JS, or use KaTeX's `renderToString` for inline pre-rendered math |
| Mermaid CLI (mmdc) | Passing Mermaid source inline via stdin without setting `--backgroundColor transparent` — results in white-background diagrams on dark theme | Always set `--backgroundColor transparent --theme dark` when calling mmdc |
| Jinja2 auto-escape | Using `| safe` filter on any field that contains user-supplied content (e.g., slide titles from source PDFs) | Enable auto-escape globally; only use `| safe` for pre-sanitized or compiler-generated HTML fragments (never raw LLM-generated strings) |
| PyYAML `load()` | LLM-generated code and many tutorials use `yaml.load(f)` which allows arbitrary Python execution | Always use `yaml.safe_load(f)` in the compiler |
| `scroll-snap` + keyboard nav | Setting `overflow: hidden` on the scroll container traps Tab focus inside it | Use `overflow: auto` and manage slide focus with `tabindex` and JavaScript, following carousel ARIA patterns |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Calling `mmdc` once per diagram in a subprocess | Compile time scales linearly with diagram count; a 10-diagram deck takes 30+ seconds due to Puppeteer startup overhead | Batch all Mermaid sources into a single mmdc invocation, or render client-side | More than 2-3 Mermaid diagrams per deck |
| Re-parsing the full YAML schema for every compilation | Negligible at single-file scale; noticeable in batch mode | Load schema once, validate all slides in a loop | Batch mode with 20+ decks |
| Embedding full KaTeX font files in HTML (base64) | Output HTML is 500KB+ before content | Always reference KaTeX from CDN or a shared local path; never embed fonts | Every deck if fonts are embedded |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Using `yaml.load()` instead of `yaml.safe_load()` | Arbitrary code execution if an attacker controls the YAML input | Always use `yaml.safe_load()` |
| Using Jinja2 `render_template_string()` with LLM-generated content as the template source | Server-side template injection — full RCE | Only use `render_template()` with static template files; LLM output is always data, never template |
| Disabling Jinja2 auto-escape (`autoescape=False`) | XSS if any slide content contains `<script>` or HTML entities | Keep `autoescape=True` (default for HTML templates); explicitly mark safe only compiler-controlled fragments |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No skip link at the top of the HTML | Keyboard and screen reader users must Tab through all slide navigation controls before reaching slide content | Add `<a href="#slide-1" class="skip-link">Skip to content</a>` as the first element in `<body>` |
| Slide position not announced to screen readers | Screen reader users cannot tell they are on slide 3 of 12 | Add `role="group"` and `aria-label="Slide N of M"` to each slide wrapper |
| No `prefers-reduced-motion` check on scroll animations | Users with vestibular disorders experience nausea from scroll-snap animation | Wrap CSS transitions in `@media (prefers-reduced-motion: no-preference)` |
| Dot indicators without accessible labels | Screen reader announces "button, button, button" with no context | Give each indicator `aria-label="Go to slide N"` and `aria-current="true"` for the active slide |
| Keyboard user cannot exit slide container | Focus traps inside the `overflow: scroll` slide container | Implement `keydown` handler: Escape exits slide focus mode, Tab moves to next interactive region outside the deck |

---

## "Looks Done But Isn't" Checklist

- [ ] **Alt text enforcement:** Compiler produces HTML with `alt=""` — verify that the YAML schema rejects empty or missing `alt_text` fields for image and diagram slides, not just passes an empty string through.
- [ ] **Heading hierarchy:** The compiler emits `h2` headings in slide titles — verify no slide produces `h4` without a preceding `h3` in the same document context.
- [ ] **Keyboard trap test:** The compiled HTML passes axe — verify manually that Tab from the last slide's focusable element exits the slide container and reaches the page footer/skip link target.
- [ ] **KaTeX error spans:** The compiled HTML looks correct visually — verify by searching the output for `class="katex-error"` spans that KaTeX renders in red when an expression fails to parse.
- [ ] **Dark theme contrast ratio:** Colors look fine on your monitor — verify the amber-on-dark color pair meets 4.5:1 contrast ratio using the WebAIM contrast checker; amber `#F59E0B` on dark `#1F2937` passes, but variations may not.
- [ ] **Mermaid background transparency:** Diagrams render — verify the diagram background matches the slide background (no white box on dark theme) by inspecting the SVG's `background-color` or `style` attribute.
- [ ] **Layout variety validation:** A deck compiles without errors — verify it passes the layout variety check (no more than 60% one layout type, no 3 consecutive identical layouts).
- [ ] **YAML injection:** `yaml.safe_load()` is called — verify no fallback path in the code calls `yaml.load()` (grep the compiler source).

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Mermaid server-side strategy chosen wrong | MEDIUM | Switch from inline SVG to client-side rendering by adding `<script src="mermaid.min.js">` to the HTML template and changing the compiler to emit `<div class="mermaid">` blocks instead of SVG. One-day change. |
| Schema too complex — LLM generates wrong fields | MEDIUM | Add a pydantic validation layer with coercion: map common LLM field-name variants to canonical names (e.g., `body` → `content`). Update the skill prompt with corrected examples. |
| ADA violations found post-launch | MEDIUM–HIGH | Identify violation categories (alt text, heading order, keyboard trap). Fix at the compiler/schema level so all future decks are correct. Re-compile all existing decks. |
| Image embedding bloats HTML files | LOW | Add `--no-embed-images` flag to compiler, switch to relative path references. Existing decks must be recompiled. |
| KaTeX unsupported commands in source material | LOW | Add a pre-processing step in the `/md_to_yaml` skill that normalizes known incompatible commands (`\align` → `\aligned`, etc.). Add KaTeX validation to CI. |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Mermaid server-side rendering | Phase: Build Python Compiler (Mermaid handler design) | Compile a deck with 2+ Mermaid diagrams; inspect SVG output for valid `viewBox` and no `NaN` values |
| YAML schema too wide for LLM | Phase: Define YAML DSL Schema | Generate 10 test decks with the skill; count how many use each layout type; verify all 15+ are used |
| ADA violations — alt text | Phase: Define YAML DSL Schema | Attempt to compile a deck with missing `alt_text`; confirm compiler raises `ValidationError` |
| ADA violations — keyboard trap | Phase: Build Python Compiler | Manual keyboard navigation test on compiled output |
| Layout variety not enforced | Phase: Build Python Compiler | Compile a monotonous deck (all `slide--content`); confirm compiler emits a warning |
| KaTeX silent failure | Phase: Handle LaTeX/Math | Compile a deck with an invalid LaTeX expression; verify output contains no `katex-error` spans (or that CI catches them) |
| Self-contained HTML image bloat | Phase: Define YAML DSL Schema + Build Python Compiler | Compile a deck with 5 JPEG images; verify output HTML is under 2MB |
| `yaml.load()` security | Phase: Build Python Compiler | `grep -r "yaml.load(" compiler/` — must return zero results |

---

## Sources

- [KaTeX Common Issues](https://katex.org/docs/issues) — official documentation on unsupported LaTeX commands
- [Mermaid Server-Side Rendering Issue #3650](https://github.com/mermaid-js/mermaid/issues/3650) — canonical discussion of DOM requirement
- [Bad Schemas Could Break LLM Structured Outputs — Instructor](https://python.useinstructor.com/blog/2024/09/26/bad-schemas-could-break-your-llm-structured-outputs/) — schema complexity and LLM failure modes
- [WCAG 2.1 AA Checklist — accessible.org](https://accessible.org/wcag/) — full success criteria checklist
- [CSS Carousels Accessibility — Sara Soueidan](https://www.sarasoueidan.com/blog/css-carousels-accessibility/) — scroll-snap accessibility pitfalls
- [Accessible Carousel — The A11Y Collective](https://www.a11y-collective.com/blog/accessible-carousel/) — ARIA patterns for slide navigation
- [Jinja2 XSS Vulnerability CVE-2024-22195 — Snyk](https://snyk.io/blog/jinja2-xss-vulnerability/) — Jinja2 escaping pitfalls
- [Math Rendering and Accessibility Conflicts](https://vm70.neocities.org/posts/2024-03-24-math-rendering/) — KaTeX vs MathJax accessibility tradeoffs
- [Taming LLM Outputs — Dataiku](https://www.dataiku.com/stories/blog/your-guide-to-structured-text-generation) — structured output cognitive load
- [LLM Output Drift: Cross-Provider Validation](https://arxiv.org/html/2511.07585v1) — schema drift and compliance failure metrics

---
*Pitfalls research for: YAML-to-HTML Presentation DSL Compiler*
*Researched: 2026-03-21*
