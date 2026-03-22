# Feature Research

**Domain:** Presentation DSL compiler (YAML-to-HTML slide deck)
**Researched:** 2026-03-21
**Confidence:** MEDIUM — Competitor feature analysis HIGH; ADA patterns HIGH; LLM-authoring specifics MEDIUM (emerging area)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features present in every mature presentation tool (Marp, Slidev, Reveal.js, Beamer/Quarto). Missing any of these makes the product feel incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Multiple slide layout types | Every deck needs title, content, image, divider, two-column slides | MEDIUM | Derive ~15 primitives from existing HTML deck analysis; Slidev has ~20 built-in layouts |
| Inline Markdown content (bold, italic, lists, links) | Authors think in Markdown; all competing tools support it | LOW | Render inside YAML string fields; Jinja2 + markdown-it or Python-Markdown |
| Code blocks with syntax highlighting | Developer audiences require this; Marp, Slidev both built it in | MEDIUM | Use Prism.js or Highlight.js embedded in HTML output; language tag in YAML |
| LaTeX / math rendering | Expected for any technical/scientific audience; all major tools support it | MEDIUM | KaTeX already used in existing decks; load from CDN; compile `$$...$$` blocks |
| Image embedding (JPEG/PNG) | Core content type; every slide tool supports it | LOW | Base64 embed or relative path; alt text field required for ADA |
| Self-contained single HTML output | Expected for sharing; Marp and Reveal.js both support this | LOW | Embed CSS/JS inline; KaTeX CDN is acceptable per PROJECT.md |
| Keyboard navigation (arrow keys, space) | Standard for all slide viewers; users assume it works | LOW | JS event listeners; documented ARIA keyboard pattern |
| Slide titles / heading structure | Required for screen readers and document structure; all tools have this | LOW | `<h1>` per slide; ties into ARIA `aria-labelledby` |
| Theming / visual consistency | Authors expect a coherent look without per-slide CSS | LOW | Single CSS theme file embedded; dark theme with amber accents already defined |
| YAML/text-based source format | Required for LLM authoring and version control; this is the whole premise | LOW | Already the design decision; validates against competition (Quarto uses YAML frontmatter) |

### Differentiators (Competitive Advantage)

Features that go beyond competitor defaults, targeting this product's specific value: ADA compliance by construction and LLM-reliable authoring.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| ADA compliance enforced at compile time | No competitor enforces WCAG 2.1 AA by default — they rely on author discipline | MEDIUM | Compiler errors/warnings if alt text missing on images, color contrast failures, no slide title; WCAG 2.1 AA: 4.5:1 contrast for normal text, 3:1 for large |
| ARIA slide carousel markup baked in | Correct `aria-roledescription="carousel"`, `role="group"` per slide, `aria-label="N of M"` is non-trivial and rarely done right | MEDIUM | Compile-time, not optional; follows W3C APG carousel pattern |
| Skip navigation link | Required by WCAG 2.1 SC 2.4.1; almost no HTML slide tool includes it | LOW | `<a href="#main-content" class="skip-link">` rendered on every deck |
| Layout variety enforcement | LLM prompt alone cannot guarantee no three identical consecutive layouts; compiler enforces it | MEDIUM | Post-processing validation pass; warn or error if layout rhythm violated |
| Deterministic reproducible output | Given same YAML, output is byte-identical across environments | LOW | No LLM in compilation step; pure Python + Jinja2; critical for CI/CD and diffing |
| Compact DSL (10x token reduction) | LLMs generate full HTML unreliably and expensively; YAML DSL is an order of magnitude smaller | MEDIUM | This is the core architectural bet; validated by PROJECT.md — existing decks are 30-90KB HTML vs. estimated 3-9KB YAML |
| Mermaid diagram compilation to inline SVG | Competing tools render Mermaid in-browser at runtime; this compiles to static SVG (works offline, accessible) | HIGH | Requires mermaid-py or Node.js subprocess; static SVG can receive `<title>` and `role="img"` for ADA |
| SVG direct embedding with ADA wrapping | Raw SVG gets `<title>`, `<desc>`, `role="img"`, `aria-labelledby` automatically | LOW | Author provides alt text in YAML; compiler handles HTML wrapper |
| Bullet limit enforcement | More than 5 bullets per slide is a known readability failure; compiler warns | LOW | Rule-based validation; configurable threshold |
| Speaker notes field | Not universally present but expected by professional presenters; Slidev and Reveal.js support it | LOW | Rendered in hidden `<aside>` with `aria-hidden="true"` or presenter mode |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem like natural additions but create disproportionate complexity or conflict with core goals.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time preview / hot reload | Slidev and Marp both offer live preview; authors want immediate feedback | Requires a dev server, file watcher, WebSocket — multiplies architecture complexity by 2x with no benefit for LLM-authoring workflow | Run compiler CLI manually; fast enough (<1s compile) for iteration |
| PowerPoint / PPTX export | Users used to PowerPoint ask for it | python-pptx cannot replicate CSS layouts, KaTeX math, or SVG diagrams faithfully; creates a second rendering pipeline to maintain | HTML-only; explicitly out of scope per PROJECT.md |
| Theming / custom CSS per deck | Seems like user control; Marp supports per-deck CSS | Breaks ADA guarantees — custom CSS can violate contrast ratios or hide ARIA structure | Single enforced theme; limited parameterization (accent color, font size) within validated range |
| Interactive / animated slides | Reveal.js supports fragment animations; Slidev supports Vue interactivity | Animation requires runtime JS complexity; fragments can confuse screen readers and break linear reading order | CSS transitions only (scroll-snap); no JS-driven fragment reveals |
| PDF export | Common request from academics; Marp/Reveal.js support it | Headless Chrome/Puppeteer is a heavy dependency; PDF accessibility (tagged PDF) is a separate WCAG domain entirely | Link to browser Print-to-PDF as a workaround; don't build it |
| Multi-language / i18n | International users may want localization | Doubles content management complexity; not in the current use case (quantum/ML academic talks in English) | Single-language output; UTF-8 throughout handles special characters |
| LLM in the compilation step | "Smart" layout selection sounds appealing | Destroys determinism — the compiler's core value is bit-identical reproducibility | Keep LLM confined to YAML generation (/md_to_yaml skill); compiler is pure-Python |
| Slide deck editor UI | Some tools like Deckset have a GUI | Full UI is a separate product; creates a maintenance burden larger than the compiler itself | Author YAML in any editor; VS Code YAML validation via schema |

---

## Feature Dependencies

```
[ADA-compliant HTML output]
    └──requires──> [ARIA carousel markup]
    └──requires──> [Skip navigation link]
    └──requires──> [Alt text enforcement (compile-time error)]
    └──requires──> [Color contrast validation]
    └──requires──> [Slide title / heading structure]

[Mermaid diagram support]
    └──requires──> [Static SVG compilation]
                       └──requires──> [Mermaid CLI or mermaid-py subprocess]
    └──enhances──> [ADA-compliant HTML output] (SVG gets <title> + aria attrs)

[Layout variety enforcement]
    └──requires──> [Layout primitives defined (YAML schema)]
    └──enhances──> [LLM-reliable authoring] (constraint reduces hallucination surface)

[Code syntax highlighting]
    └──requires──> [Prism.js or Highlight.js embedded in theme]
    └──conflicts──> [LLM-in-compiler] (highlighting must be deterministic)

[Speaker notes]
    └──requires──> [HTML structure that separates notes from visible content]
    └──conflicts──> [PDF export] (notes don't map to PDF naturally)

[LaTeX / KaTeX rendering]
    └──requires──> [KaTeX CDN or embedded JS]
    └──enhances──> [Technical credibility] (academic/ML audience)
```

### Dependency Notes

- **ADA output requires all five sub-features:** Any one missing breaks WCAG 2.1 AA compliance. Alt text enforcement and ARIA markup are the highest-value, highest-miss items in existing tools.
- **Mermaid requires an external process:** mermaid-py or a Node.js subprocess must run at compile time. This is the highest-complexity dependency in the stack. Consider making it optional in v1.
- **Layout variety enforcement requires schema to be finalized first:** Cannot validate layout rhythms until the ~15 primitives are enumerated. Sequence: analyze existing decks → define schema → implement enforcement.
- **Speaker notes conflict with PDF export:** Notes should be hidden from visible output but accessible to presenter tools. Since PDF export is an anti-feature, this conflict is safely avoided.

---

## MVP Definition

### Launch With (v1)

Minimum viable product to validate LLM-authoring + ADA compilation pipeline end-to-end.

- [ ] YAML DSL schema with ~15 layout primitives — the foundation everything else builds on
- [ ] Python/Jinja2 compiler: YAML → single-file HTML — validates the two-stage pipeline concept
- [ ] Layout types: title, content (bullets), two-column, image, figure+caption, code, divider/section — covers 90% of observed slide patterns
- [ ] ADA enforcement: alt text required on images, ARIA carousel markup, skip link, slide titles — non-negotiable per PROJECT.md
- [ ] KaTeX math rendering — required for target audience (quantum/ML academic decks)
- [ ] Code blocks with syntax highlighting — required for target audience (developer/researcher talks)
- [ ] SVG direct embedding with ADA wrapper — lightweight; already used in existing decks
- [ ] Bullet limit validation warning (>5 bullets) — low-complexity, high-value quality gate
- [ ] /md_to_yaml Claude Code skill — generates YAML from markdown/content input

### Add After Validation (v1.x)

Add once core pipeline is proven correct on 3+ real decks.

- [ ] Mermaid diagram compilation to inline SVG — HIGH complexity; add when diagram-heavy decks are needed
- [ ] Speaker notes field — add when first presenter uses the system for a live talk
- [ ] Layout variety enforcement (no 3 consecutive identical) — add after observing LLM output patterns
- [ ] YAML schema validation (JSON Schema) — add to catch authoring errors before compilation
- [ ] Color contrast validation at compile time — add once theme is locked

### Future Consideration (v2+)

Defer until product-market fit established.

- [ ] Tables — complex ADA requirements (headers, scope attributes); defer until needed
- [ ] Configurable accent color within validated contrast range — low priority; current dark+amber theme works
- [ ] Fine-tuned local model on YAML DSL — noted in PROJECT.md as future work
- [ ] Hook-based auto-compilation — noted in PROJECT.md as future enhancement

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| YAML DSL schema (~15 primitives) | HIGH | MEDIUM | P1 |
| Python/Jinja2 compiler core | HIGH | MEDIUM | P1 |
| ADA: alt text enforcement + ARIA carousel | HIGH | MEDIUM | P1 |
| ADA: skip link + slide titles | HIGH | LOW | P1 |
| KaTeX math | HIGH | LOW | P1 |
| Code blocks + syntax highlighting | HIGH | LOW | P1 |
| SVG embedding with ADA wrapper | HIGH | LOW | P1 |
| /md_to_yaml Claude Code skill | HIGH | MEDIUM | P1 |
| Bullet limit validation | MEDIUM | LOW | P2 |
| Speaker notes | MEDIUM | LOW | P2 |
| Layout variety enforcement | MEDIUM | MEDIUM | P2 |
| YAML schema validation | MEDIUM | LOW | P2 |
| Color contrast validation at compile time | HIGH | MEDIUM | P2 |
| Mermaid diagram → inline SVG | MEDIUM | HIGH | P2 |
| Tables with ADA headers | MEDIUM | HIGH | P3 |
| Configurable theming | LOW | MEDIUM | P3 |
| PDF export | LOW | HIGH | anti-feature |
| PPTX export | LOW | HIGH | anti-feature |
| Real-time preview | LOW | HIGH | anti-feature |

**Priority key:**
- P1: Must have for v1 launch
- P2: Add after v1 validation
- P3: Future consideration

---

## Competitor Feature Analysis

| Feature | Marp | Slidev | Reveal.js | Quarto/Beamer | Our Approach |
|---------|------|--------|-----------|---------------|--------------|
| Source format | Markdown | Markdown + frontmatter | HTML | Markdown + YAML | YAML DSL (LLM-optimized) |
| Layout primitives | 3 themes, limited layouts | ~20 built-in layouts (Vue) | HTML-based, unlimited | LaTeX macros or HTML | ~15 named types, schema-enforced |
| ADA compliance | Not enforced | Not enforced | Not enforced | Not enforced | Enforced at compile time (differentiator) |
| Math | KaTeX/MathJax | KaTeX | MathJax | LaTeX native | KaTeX (already in decks) |
| Code highlighting | Highlight.js | Shiki | Highlight.js | Pandoc | Prism.js or Highlight.js embedded |
| Mermaid diagrams | Via plugin | Built-in (runtime) | Via plugin | Via plugin | Static SVG compilation (better ADA) |
| LLM authoring | Markdown (workable) | Markdown (workable) | HTML (poor) | Markdown+YAML (good) | YAML DSL (purpose-built) |
| Deterministic output | YES | NO (Vue runtime) | NO (JS runtime) | YES | YES (pure Python) |
| Self-contained HTML | YES | Partial | YES | YES | YES |
| Speaker notes | YES | YES | YES | YES | v1.x |
| Export to PPTX | YES | NO | NO | YES | Explicitly excluded |
| Token efficiency for LLM | LOW (Markdown prose) | LOW | VERY LOW (HTML) | MEDIUM | HIGH (YAML DSL design goal) |

---

## Sources

- [Slidev Features](https://sli.dev/features/) — official documentation
- [Slidev Built-in Layouts](https://sli.dev/builtin/layouts) — layout primitives reference
- [Marp Official Site](https://marp.app/) — feature overview
- [Marp VS Code Extension](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) — features list
- [W3C WAI: Making Events Accessible](https://www.w3.org/WAI/teach-advocate/accessible-presentations/) — WCAG presentation requirements
- [LLM-Powered Slide Decks: A Comparison of Formats](https://nbrosse.github.io/posts/llm-slides/llm-slides.html) — LLM format comparison
- [Talk to Your Slides (arXiv 2505.11604)](https://arxiv.org/abs/2505.11604) — structured data + LLM slide editing research
- [A11Y Collective: Accessible Carousel](https://www.a11y-collective.com/blog/accessible-carousel/) — ARIA carousel patterns
- [Chrome for Developers: Accessible Carousel](https://developer.chrome.com/blog/accessible-carousel) — scroll-snap + ARIA patterns
- [WCAG 2.1 ADA Requirements 2026](https://www.foxbright.com/pub/stories/view/wcag-2-1-what-you-need-to-know-about-the-new-ada-requirements-for-2026) — compliance timeline
- [10 Code-Based Presentation Tools 2025 (Medium)](https://medium.com/demohub-tutorials/10-code-based-presentation-tools-for-developers-ranked-2025-fe764698f132) — ecosystem overview

---
*Feature research for: YAML-to-HTML Slide DSL Compiler*
*Researched: 2026-03-21*
