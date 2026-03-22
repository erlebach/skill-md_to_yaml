# Project Research Summary

**Project:** md_to_yaml — YAML-to-HTML Presentation DSL Compiler
**Domain:** Batch slide-deck compiler with LLM-authoring frontend and ADA compliance enforcement
**Researched:** 2026-03-21
**Confidence:** HIGH (stack, architecture, pitfalls); MEDIUM (LLM-authoring schema specifics)

## Executive Summary

This project is a deterministic Python compiler that converts a structured YAML DSL into a standalone HTML slide deck. The system has two distinct concerns that must never be conflated: (1) the LLM-facing authoring layer, where a Claude Code skill transforms markdown/PDF content into YAML using a constrained DSL; and (2) the compiler layer, where pure Python renders that YAML to byte-identical HTML on every run. Keeping LLM logic strictly out of the compiler is the single most important architectural decision — any "smart" compilation step destroys the determinism that makes this system trustworthy for CI/CD and content diffing.

The recommended approach is a five-stage Python pipeline: parse (PyYAML), validate (Pydantic v2 with discriminated unions on the `layout` field), process assets (images, Mermaid SVG, KaTeX decisions), render slides (one Jinja2 template per layout primitive), and assemble the final HTML document (shell template, inlined CSS/JS, sidebar TOC, ARIA landmarks). ADA compliance is enforced at two levels: structurally by the compiler (ARIA carousel markup, skip link, heading hierarchy) and content-level by requiring `alt_text` as a non-optional schema field. No competing tool (Marp, Slidev, Reveal.js, Quarto) enforces WCAG 2.1 AA at compile time — this is the project's primary differentiator.

The key risks center on three areas: Mermaid server-side rendering (requires a strategy decision before any code is written — the library depends on a headless browser internally), YAML schema complexity (a schema too wide causes LLMs to silently skip or misname fields in less-common layouts), and the 70% of ADA violations that automated tools cannot catch (structural compliance from the compiler is necessary but not sufficient; content-level alt text must be enforced at the schema level). All three risks are preventable if addressed in the correct phase.

## Key Findings

### Recommended Stack

The compiler is pure Python with no Node.js runtime dependency. PyYAML 6.0.3 parses the DSL; Pydantic v2 validates it with typed models per layout type; Jinja2 3.1.6 renders each slide via a dedicated template; Pygments 2.19.2 handles syntax highlighting inline. Math rendering defaults to the KaTeX CDN (zero build dependency); the `markdown-katex` package is available for offline pre-rendering. Mermaid diagram compilation uses the `mmdc` Python package (no Node.js required), though this is a newer library at MEDIUM confidence — verify stability before relying on it for production.

**Core technologies:**
- **Python 3.11+**: Compiler runtime — portable, no external runtime required
- **PyYAML 6.0.3**: DSL parsing — always use `yaml.safe_load()`, never `yaml.load()`
- **Pydantic v2.12**: Schema validation — discriminated union on `layout` field; precise error messages on bad DSL
- **Jinja2 3.1.6**: HTML rendering — one template per layout primitive; shared macros for reusable elements
- **Pygments 2.19.2**: Code syntax highlighting — pure Python, 598+ lexers, inline CSS output
- **mmdc (Python-native)**: Mermaid → inline SVG — no Node.js; MEDIUM confidence, verify before use
- **markdown-katex**: LaTeX pre-rendering — bundles KaTeX binary; MEDIUM confidence on bundled version

**Dev tooling:** `uv` for package management, `ruff` for lint/format, `pyright` for static typing, `pytest` + `playwright + axe-core` for testing and CI ADA checks.

### Expected Features

The MVP must include: YAML DSL schema with ~15 layout primitives, the Python/Jinja2 compiler core, full ADA enforcement (alt text required, ARIA carousel markup, skip link, slide titles, heading hierarchy validation), KaTeX math, code blocks with syntax highlighting, SVG embedding with ADA wrapper, and the `/md_to_yaml` Claude Code skill.

**Must have (v1 table stakes):**
- ~15 named layout types (title, content/bullets, two-column, image, figure+caption, code, divider/section) — covers 90% of observed patterns
- ADA: `alt_text` required field on all image/figure/diagram slides, ARIA carousel markup, skip link — non-negotiable per PROJECT.md
- KaTeX math rendering — required for quantum/ML academic target audience
- Code blocks with syntax highlighting — required for developer/researcher talks
- Deterministic, self-contained single HTML output — the core value proposition
- `/md_to_yaml` Claude Code skill — the LLM authoring entry point

**Should have (v1.x after validation):**
- Mermaid diagram → inline SVG (HIGH complexity — strategy decision required first)
- Speaker notes field
- Layout variety enforcement at compile time (no 3 consecutive identical layouts)
- Color contrast validation at compile time
- YAML schema validation via JSON Schema for editor tooling

**Defer (v2+):**
- Tables with full ADA headers
- Configurable accent color within validated contrast range
- Fine-tuned local model on the DSL
- Hook-based auto-compilation

**Anti-features (explicitly excluded):** Real-time preview, PPTX export, PDF export, custom CSS per deck, LLM in compilation step.

### Architecture Approach

The compiler is a sequential six-stage pipeline with strict layer boundaries: each stage communicates only via well-typed interfaces (Pydantic models between parse→render; HTML strings between render→assemble). No stage calls back into a previous stage. The discriminated union pattern (Pydantic `Field(discriminator="layout")`) eliminates all `if/elif` dispatch chains — adding a layout type requires only a new model class and a new Jinja2 template. Asset pre-processing (`assets.py`) runs before any template rendering, keeping all subprocess calls and file I/O out of templates. CSS and JS are stored as source files in `static/` and inlined at assembly time — never as Python string constants.

**Major components:**
1. **`parser.py`** — PyYAML load + Pydantic model construction; the `layout` field is the discriminator
2. **`assets.py`** — Image base64 encoding, Mermaid SVG rendering, math pre-processing decisions; all side effects isolated here
3. **`renderer.py`** — Jinja2 dispatch: `slide.layout` → template lookup → HTML fragment; pure function, no I/O
4. **`assembler.py`** — Shell template injection, CSS/JS inlining, sidebar TOC, ARIA landmarks
5. **`ada_check.py`** — Post-render lint pass using `html.parser` or BeautifulSoup; checks alt text, ARIA coverage, skip link, heading sequence
6. **`cli.py`** — Sole orchestrator; invokes stages in sequence

### Critical Pitfalls

1. **Mermaid server-side rendering requires a headless browser** — `mmdc` (Python-native) is the recommended strategy; decide before writing the handler. Never discover this mid-implementation. Alternatively, defer Mermaid to client-side `<script>` rendering and document the non-self-contained trade-off.

2. **YAML schema too wide causes LLM to silently skip layouts** — Keep the `layout` discriminator simple, flatten nested structures, make all required fields consistent across layout types. Write the `/md_to_yaml` skill with one worked example per layout type, not prose descriptions. Validate LLM output with Pydantic before compiling.

3. **ADA automation catches only ~30% of violations** — Separate structural compliance (compiler's job) from content compliance (schema's job). `alt_text` must be a required, non-empty field at the schema level. The compiler must validate heading sequence. Test keyboard navigation manually — `scroll-snap` + `overflow: auto` can trap Tab focus.

4. **KaTeX fails silently on unsupported LaTeX commands** — Document unsupported commands in the DSL spec so the LLM avoids them. Add a post-compile grep for `class="katex-error"` spans as a CI check. Consider `katex.renderToString({throwOnError: true})` as a build-time validation step.

5. **Base64 image embedding bloats self-contained HTML** — Default to relative-path image references; add `--embed-images` flag with a 2MB warning. Existing decks achieve 30-90KB by using SVG and text (KaTeX), not raster images.

## Implications for Roadmap

The component dependency order from ARCHITECTURE.md directly dictates phase sequence. The schema is the foundation everything depends on; the skill is built last because it must match the finalized schema.

### Phase 1: Define YAML DSL Schema
**Rationale:** Every subsequent component depends on stable Pydantic models. Rushing past this creates cascading rework. This is also where the most critical pitfalls are prevented (schema width, `alt_text` required field, image handling strategy).
**Delivers:** `models.py` with all ~15 layout types as discriminated union; `schema/slide-dsl.yaml` as canonical spec; documented list of KaTeX-unsupported commands; Mermaid strategy decision recorded.
**Addresses:** YAML DSL schema (P1 feature), `alt_text` enforcement (P1 ADA), image embedding strategy
**Avoids:** Pitfall 2 (schema too wide), Pitfall 3 (ADA alt text), Pitfall 6 (image bloat)

### Phase 2: Shell Template and Static Assets
**Rationale:** Establishing the HTML skeleton and CSS/JS immediately enables visual testing. Once the shell exists, any compiled slide fragment can be dropped in and inspected in a browser. This unblocks parallel development of layout templates.
**Delivers:** `templates/shell.html.j2`, `static/base.css`, `static/deck.js` — dark theme, scroll-snap nav, ARIA landmarks, skip link, dot indicators with `aria-label`
**Addresses:** Self-contained HTML output, keyboard navigation, ARIA carousel markup, skip link, `prefers-reduced-motion`
**Avoids:** Pitfall 3 (keyboard trap from `overflow: hidden`), UX pitfalls (missing skip link, unlabeled dots)

### Phase 3: Parser and Core Layout Templates
**Rationale:** Validate the end-to-end pipeline with real YAML input before building the full layout set. Build the 4-5 most common layouts (title, content, two-column, code, divider) and prove the pipeline works before adding complexity.
**Delivers:** `parser.py`, `renderer.py`, first 5 layout templates, `cli.py` entry point; compiles a real test deck to HTML
**Uses:** PyYAML + Pydantic (parse), Jinja2 + Pygments (render)
**Implements:** Discriminated union dispatch, template-per-layout pattern, macros for shared elements

### Phase 4: Asset Pipeline and Remaining Layouts
**Rationale:** Asset processing (`assets.py`) is isolated and testable independently. Complete the remaining ~10 layout templates once the dispatch pattern is proven.
**Delivers:** `assets.py` with image embedding and Mermaid strategy implemented; all ~15 layout templates; Mermaid integration per chosen strategy
**Addresses:** Mermaid diagrams (P2 feature), SVG embedding with ADA wrapper (P1 feature)
**Avoids:** Pitfall 1 (Mermaid strategy chosen and implemented correctly), `mmdc` background transparency gotcha

### Phase 5: Full Assembly and ADA Lint Pass
**Rationale:** Assembler and ADA check are the last pure-Python stages. The ADA lint pass is a quality gate that should run before any real decks are compiled.
**Delivers:** `assembler.py` with sidebar TOC, full nav chrome; `ada_check.py` post-render linter; CI integration with `playwright + axe-core`
**Addresses:** ADA structural compliance (heading hierarchy, ARIA landmark coverage, skip link presence), layout variety enforcement warning
**Avoids:** Pitfall 3 (ADA violations), Anti-Pattern 4 (no ADA validation pass)

### Phase 6: LaTeX / KaTeX Validation
**Rationale:** KaTeX CDN auto-render is the default and lowest-risk path. This phase hardens the math story with compile-time validation and documents unsupported commands.
**Delivers:** KaTeX CDN integration in shell template; post-compile grep for `katex-error` spans in CI; documented list of unsupported LaTeX commands in DSL spec
**Addresses:** KaTeX math rendering (P1 feature), silent KaTeX failure detection
**Avoids:** Pitfall 5 (KaTeX silent failure), KaTeX FOUC issue (use `<script defer>`)

### Phase 7: /md_to_yaml Claude Code Skill
**Rationale:** Built last because the skill's output format must match the finalized schema. Building it earlier creates a moving-target problem where the skill generates YAML that is invalidated by later schema changes.
**Delivers:** `skill/md_to_yaml.md` Claude Code skill; one worked example per layout type; Pydantic validation layer with field-name coercion for common LLM drift patterns
**Addresses:** `/md_to_yaml` skill (P1 feature), layout variety prompt examples
**Avoids:** Pitfall 2 (LLM silently skipping layouts), field-name drift (`body` → `content` coercion)

### Phase 8: Validation on Real Decks
**Rationale:** End-to-end validation on 3+ real existing decks from `/n8n_to_python/output_html_files/` proves the pipeline handles real content before broader use.
**Delivers:** Regression test suite with reference HTML fixtures; confirmed output on 3+ real decks; v1 release
**Addresses:** All P2 features added based on observed gaps; test coverage for all 15+ layout types

### Phase Ordering Rationale

- Schema must precede everything — Pydantic models are the interface contract between all stages
- Shell template precedes layout templates — enables visual testing from day one
- Asset pipeline can be stubbed (pass-through) while layout templates are developed, then completed
- ADA lint pass comes after assembler — it validates the complete document, not fragments
- Skill is last — it consumes the finalized schema; building it earlier creates churn

### Research Flags

Phases needing deeper research during planning:
- **Phase 1 (Schema):** LLM-authoring schema design is an emerging area; research how other YAML DSLs for LLM generation handle discriminated unions in practice. Consider generating 5-10 test decks with a draft schema before finalizing.
- **Phase 4 (Mermaid):** `mmdc` Python package is a newer library (Jan 2026) at MEDIUM confidence. Prototype the Mermaid handler in isolation before committing to it; have the client-side `<script>` fallback ready.

Phases with standard patterns (skip research):
- **Phase 2 (Shell template):** Scroll-snap CSS carousel with ARIA is well-documented (W3C APG, Sara Soueidan). Implement directly from patterns.
- **Phase 3 (Parser/Renderer):** PyYAML + Pydantic + Jinja2 pipeline is textbook Python. No novel patterns.
- **Phase 6 (KaTeX):** CDN integration is trivial; KaTeX docs are authoritative. Only the validation step needs care.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Core stack (PyYAML, Pydantic v2, Jinja2, Pygments) is well-established with confirmed versions. `mmdc` and `markdown-katex` are MEDIUM — newer libraries, verify stability before production commitment. |
| Features | MEDIUM–HIGH | Competitor feature analysis is HIGH. LLM-authoring-specific constraints (schema width, field consistency) are MEDIUM — emerging research, patterns are plausible but not battle-tested at scale. |
| Architecture | HIGH | Pipeline pattern is standard for batch compilers. Discriminated union dispatch is documented Pydantic best practice. Existing HTML deck analysis (ground truth) supports component boundaries. |
| Pitfalls | HIGH | Mermaid DOM requirement is documented in upstream issues. KaTeX unsupported commands are in official docs. ADA automation coverage (~30%) is from axe-core's own documentation. Schema/LLM failure modes are from published research. |

**Overall confidence:** HIGH for implementation approach; MEDIUM for LLM schema ergonomics (validate with real generation tests early)

### Gaps to Address

- **`mmdc` production stability:** The Python-native Mermaid renderer is new (Jan 2026). Prototype it against 2-3 real diagram inputs before Phase 4 commits to it. If it fails, the fallback is client-side Mermaid rendering (acceptable for v1).
- **KaTeX version alignment:** `markdown-katex` bundles a KaTeX binary; confirm the bundled version matches the CDN link used in the shell template to avoid rendering inconsistencies between compile-time pre-rendering and browser fallback.
- **Exact layout primitive list:** The ~15 primitives need enumeration from analysis of existing `/n8n_to_python/output_html_files/` decks. This analysis should happen in Phase 1, not be assumed.
- **LLM field-name drift patterns:** Research which field names the LLM is most likely to invent (`body`, `text`, `description` instead of `content`). Build coercion into `parser.py` proactively rather than discovering drift post-launch.

## Sources

### Primary (HIGH confidence)
- [Jinja2 PyPI](https://pypi.org/project/Jinja2/) — version 3.1.6 confirmed
- [PyYAML PyPI](https://pypi.org/project/PyYAML/) — version 6.0.3 confirmed
- [Pygments PyPI](https://libraries.io/pypi/Pygments) — version 2.19.2 confirmed
- [Pydantic v2.12 announcement](https://pydantic.dev/articles/pydantic-v2-12-release) — v2.12.x stable
- [KaTeX API docs](https://katex.org/docs/api) — server-side pre-rendering, CSP requirements
- [KaTeX Common Issues](https://katex.org/docs/issues) — unsupported LaTeX commands
- [axe-core GitHub](https://github.com/dequelabs/axe-core) — WCAG 2.1 AA tag support
- [Pydantic discriminated unions](https://docs.pydantic.dev/latest/) — official docs
- [W3C WAI: Making Events Accessible](https://www.w3.org/WAI/teach-advocate/accessible-presentations/) — WCAG presentation requirements
- Existing HTML deck analysis: `/Users/erlebach/src/2026/claude-code/n8n/n8n_to_python/output_html_files/` — ground truth

### Secondary (MEDIUM confidence)
- [mmdc GitHub](https://github.com/mohammadraziei/mmdc) — Python-native Mermaid, Jan 2026
- [markdown-katex PyPI](https://pypi.org/project/markdown-katex/) — bundles KaTeX binary
- [Bad Schemas Could Break LLM Structured Outputs — Instructor](https://python.useinstructor.com/blog/2024/09/26/bad-schemas-could-break-your-llm-structured-outputs/) — schema complexity and LLM failure modes
- [LLM Output Drift — arXiv 2511.07585](https://arxiv.org/html/2511.07585v1) — schema drift metrics
- [Marp/Marpit architecture — DeepWiki](https://deepwiki.com/marp-team/marpit/1-overview) — architecture reference
- [CSS Carousels Accessibility — Sara Soueidan](https://www.sarasoueidan.com/blog/css-carousels-accessibility/) — scroll-snap pitfalls
- [LLM-Powered Slide Decks format comparison](https://nbrosse.github.io/posts/llm-slides/llm-slides.html)
- [Talk to Your Slides — arXiv 2505.11604](https://arxiv.org/abs/2505.11604) — structured data + LLM slide editing

### Tertiary (LOW confidence — validate during implementation)
- `mmdc` Python package production stability (new library, limited track record)
- KaTeX bundled version in `markdown-katex` matching CDN version

---
*Research completed: 2026-03-21*
*Ready for roadmap: yes*
