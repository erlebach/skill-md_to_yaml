# Skill Split Design: md_to_yaml → deck-author / deck-compile / figure-spec

**Date:** 2026-04-19  
**Status:** Approved

## Goal

Replace the monolithic `md_to_yaml` skill with three focused, self-contained skills:

| Skill | Responsibility |
|-------|---------------|
| `deck-author` | Generate YAML+Markdown IR from source material |
| `deck-compile` | Validate IR and compile to ADA-oriented HTML |
| `figure-spec` | Pre-authoring figure briefs (metadata, alt_text, asset paths) |

`md_to_yaml` is deprecated once this split is complete.

## Design Decisions

### Self-contained skills

No skill references another skill's files or `ada-slides-general`. Each skill folder is independently portable and will eventually become a plugin.

### Figure files are external

Mermaid diagrams and SVG figures are written to separate files (`.mmd`, `.svg`) in a figures folder. The YAML IR (Intermediate Representation) holds only metadata: `src:` path and `alt_text`. Inline Mermaid in `diagram` slide body remains valid for simple cases but external files are the preferred pattern.

### Compilation is deck-compile's job

`deck-author` ends at a validated `.yaml` file. It does not run the compiler. Steps 13–15 from the old `md_to_yaml` pipeline (schema validation, layout-variety check, HTML compile) move entirely to `deck-compile`.

### Client-side Mermaid rendering (current)

The compiler renders `.mmd` files via Mermaid JS in the browser, with `role="img"` / `aria-label` ADA wrapper. Pre-rendering `.mmd` → static SVG is a future compiler enhancement, out of scope for this work.

## File Distribution

### `skills/deck-author/references/` — files to copy

| File | From |
|------|------|
| `layouts.md` | already present |
| `design_rules.md` | already present |
| `creating_good_presentations.md` | `.claude/skills/md_to_yaml/` |
| `accessibility-core.md` | `.claude/skills/md_to_yaml/` |
| `layout_rules_llm.md` | `.claude/skills/md_to_yaml/` |
| `equations.md` | `.claude/skills/md_to_yaml/` |
| `mermaid-best-practices.md` | `.claude/skills/md_to_yaml/` |
| `figure_rules.md` | `.claude/skills/md_to_yaml/` |
| `svg.md` | `.claude/skills/md_to_yaml/` |
| `flavor-explanatory.md` | `.claude/skills/ada-slides-general/` |
| `flavor-implementation.md` | `.claude/skills/ada-slides-general/` |
| `flavor-mathematical.md` | `.claude/skills/ada-slides-general/` |
| `flavor-tutorial.md` | `.claude/skills/ada-slides-general/` |

### `skills/deck-compile/` — no changes

Compiler and schema already vendored. `references/compile_pipeline.md` already present.

### `skills/figure-spec/references/` — no changes

`brief_schema.md` already present and sufficient.

## `deck-author/SKILL.md` Rewrite (Approach A)

The rewrite adapts the full content-generation pipeline from `md_to_yaml/SKILL.md` with these changes:

### Added / changed

- All reference file paths updated from `./` to `references/` (e.g. `./equations.md` → `references/equations.md`)
- Flavor file paths: `../ada-slides-general/flavor-{flavor}.md` → `references/flavor-{flavor}.md`
- Pipeline ends at step 12 (write YAML file); steps 13–15 removed
- Closing instruction added: "IR written to `<path>`. Run `deck-compile` to validate and produce HTML."
- Figure authoring rule: prefer writing Mermaid/SVG to external files; YAML references by `src:` + `alt_text`

### Removed

- Bundled compiler section (belongs to `deck-compile`)
- Steps 13–15: schema validation, layout-variety check, HTML compilation
- `--compile-only` flag (not applicable to IR generation)

### Preserved

- All 12 content-generation steps (source detection, flavor/detail resolution, reference file reads, slide planning, YAML generation, figure file writing, basename + output-dir logic)
- All invocation flags: `--source`, `--append`, `--detail`, `--figures`, `--tone`, `--name`, `--output-dir`
- Full YAML Format Reference section
- Design Guidance section (updated paths)
- Error Recovery section

## Workflow After Split

```
[optional] figure-spec  →  briefs + asset paths
                ↓
         deck-author    →  .yaml IR + .mmd/.svg figure files
                ↓
         deck-compile   →  validated, ADA-oriented HTML
```

`figure-spec` is optional; `deck-author` can be run directly when figures are not pre-planned.
