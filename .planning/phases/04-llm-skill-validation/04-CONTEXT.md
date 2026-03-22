# Phase 4: LLM Skill + Validation - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Create a `/md_to_yaml` Claude Code skill that generates valid YAML DSL from PDF or folder (markdown+images) input, compiles to ADA-compliant HTML, and validate end-to-end on 3 real existing decks. The skill produces YAML using the 12 layout types from Phase 1, then auto-compiles via the Phase 2-3 compiler.

</domain>

<decisions>
## Implementation Decisions

### Skill Invocation & Input
- Input types: PDF file OR folder with markdown+image files (same as `/ada-slides-general`)
- Invocation: `/md_to_yaml <flavor> --source path/to/file.pdf` or `/md_to_yaml <flavor> --source path/to/folder/`
- For folder sources: Claude reads images with Read tool to generate accurate captions and alt-text
- Output: YAML + auto-compile to HTML in one step (YAML and HTML written next to source)
- Default diagram mode: client-side Mermaid (built in Phase 3). Note: `/ada-slides-general` SVG mode successfully embeds SVG in HTML — reference that approach if SVG issues arise

### Content Flavors
- All three flavors supported: explanatory, implementation, tutorial
- Skill reads existing `/ada-slides-general` flavor files at runtime (flavor-explanatory.md, flavor-implementation.md, flavor-tutorial.md) for content guidance
- Flavor shapes layout mix, depth, and style but output is YAML DSL (not raw HTML)

### Layout Selection Strategy
- Include full `layout_rules.md` in skill prompt — decision tree, content-mapping table, variety rules, structure rules
- IMPORTANT: Deduplicate layout_rules.md before including — remove rendering details (font sizes, bullet limits, padding) already enforced by compiler templates. Keep only: when-to-use guidance, decision tree, variety principle, content-mapping table, structure rules
- Skill does NOT modify templates — it only generates YAML content
- Layout variety enforced at YAML generation time (no 3+ consecutive same layouts)

### Validation & Error Loop
- Auto-fix and retry: skill validates generated YAML, feeds errors back to LLM, retries up to 3 times
- Validation uses Python Pydantic parser (`parse_deck_file()`) — better errors than JSON Schema
- Skill checks layout variety rules before compiling and auto-adjusts if violated
- After validation passes, compiler runs automatically

### E2E Validation
- Validate on 3 source PDFs covering different topics:
  1. `../n8n_to_python/slides_density-based.pdf` (clustering — explanatory)
  2. `../n8n_to_python/slides_prototype-based.pdf` (clustering — implementation/tutorial)
  3. `../n8n_to_python/A Survey of Quantum Transformers- Architectures, Challenges and Outlooks_nov2025_zhang etal_review.pdf` (quantum — explanatory)
- Existing HTML decks in `../n8n_to_python/output_html_files/` serve as quality reference (not inputs)
- Pass criteria (ALL must be met):
  1. Generated YAML passes Pydantic parser with no errors
  2. Compiler produces HTML successfully (warnings OK)
  3. Output HTML has ADA compliance (ARIA labels, skip links, alt text, keyboard nav)
  4. Human spot-check: layout variety, readability, professional appearance comparable to existing decks

### Claude's Discretion
- Exact prompt engineering for YAML generation (few-shot examples, system prompt structure)
- How to chunk PDF content into slides (section detection, slide count per topic)
- Error message formatting in retry loop
- Output file naming convention

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Layout & Design Rules
- `layout_rules.md` — Layout decision tree, content-mapping table, variety rules, structure rules (deduplicate rendering details before including in skill)
- `/Users/erlebach/.claude/skills/ada-slides-general/SKILL.md` — Existing skill invocation pattern, source type handling, flavor selection, required steps
- `/Users/erlebach/.claude/skills/ada-slides-general/flavor-explanatory.md` — Explanatory flavor content guidance
- `/Users/erlebach/.claude/skills/ada-slides-general/flavor-implementation.md` — Implementation flavor content guidance
- `/Users/erlebach/.claude/skills/ada-slides-general/flavor-tutorial.md` — Tutorial flavor content guidance
- `/Users/erlebach/.claude/skills/ada-slides-general/accessibility-core.md` — ADA accessibility rules (non-negotiable)

### Schema & Compiler
- `schema/models.py` — Pydantic models defining all 12 layout types and their fields
- `schema/parser.py` — `parse_deck_file()` function for YAML validation
- `schema/deck.schema.json` — JSON Schema (837 lines) for reference
- `compiler/__main__.py` — CLI entry point: `python3 -m compiler input.yaml output.html`
- `compiler/validators.py` — Layout variety and bullet limit validators

### Validation Source Material
- `../n8n_to_python/slides_density-based.pdf` — E2E validation source 1
- `../n8n_to_python/slides_prototype-based.pdf` — E2E validation source 2
- `../n8n_to_python/A Survey of Quantum Transformers- Architectures, Challenges and Outlooks_nov2025_zhang etal_review.pdf` — E2E validation source 3
- `../n8n_to_python/output_html_files/` — Reference HTML decks (quality bar)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `schema/parser.py:parse_deck_file()` — Validates YAML against Pydantic models, returns Deck object
- `compiler/engine.py:compile_deck()` — Compiles Deck to HTML string
- `compiler/validators.py:validate_deck()` — Returns warnings for layout variety, bullet limits, missing alt text
- `schema/models.py` — All 12 slide types with required/optional fields fully defined
- `compiler/__main__.py` — CLI wrapper: `python3 -m compiler input.yaml output.html [--embed-images]`

### Established Patterns
- Hybrid YAML+Markdown format: YAML frontmatter per slide + Markdown body content
- `<!-- split -->` marker separates slides in YAML files
- Client-side Mermaid rendering via `<pre class="mermaid">` blocks
- KaTeX math preserved as `$$...$$` in Markdown bodies

### Integration Points
- Skill writes YAML file, then calls `python3 -m compiler` to compile
- Pydantic parser catches field name variants and gives clear errors
- Compiler auto-detects theme (dark/light) from deck metadata

</code_context>

<specifics>
## Specific Ideas

- Skill should mirror `/ada-slides-general` invocation pattern (flavor + --source + optional flags)
- Claude should Read image files to understand content for accurate alt-text and captions (not just filenames)
- The visual-explainer skill files contain additional slide design wisdom — read those for best practices
- Web search for presentation best practices for academic/classroom context may inform content decisions

</specifics>

<deferred>
## Deferred Ideas

- Hook-based auto-compilation (file watcher triggers compiler) — ENH-04 in v2
- Fine-tuned local model on YAML DSL — ENH-03 in v2
- Speaker notes field — ENH-01 in v2

</deferred>

---

*Phase: 04-llm-skill-validation*
*Context gathered: 2026-03-22*
