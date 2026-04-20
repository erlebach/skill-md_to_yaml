# Skill Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote `skills/deck-author` to a full-pipeline IR generator by copying reference files from the legacy `md_to_yaml` skill and rewriting `deck-author/SKILL.md`.

**Architecture:** Copy 11 files into `skills/deck-author/references/`, then rewrite `skills/deck-author/SKILL.md` by adapting the `md_to_yaml` pipeline: update all file-read paths to point at `references/`, remove the bundled-compiler section and steps 13–15, and add a closing handoff instruction. `deck-compile` and `figure-spec` are unchanged.

**Tech Stack:** Bash (file copies), Markdown editing (SKILL.md rewrite), grep (verification).

---

## Task 1: Copy reference files from md_to_yaml

**Files:**
- Create: `skills/deck-author/references/creating_good_presentations.md`
- Create: `skills/deck-author/references/accessibility-core.md`
- Create: `skills/deck-author/references/layout_rules_llm.md`
- Create: `skills/deck-author/references/equations.md`
- Create: `skills/deck-author/references/mermaid-best-practices.md`
- Create: `skills/deck-author/references/figure_rules.md`
- Create: `skills/deck-author/references/svg.md`

- [ ] **Step 1: Copy the 7 files**

```bash
SRC=.claude/skills/md_to_yaml
DST=skills/deck-author/references
cp "$SRC/creating_good_presentations.md" "$DST/"
cp "$SRC/accessibility-core.md"          "$DST/"
cp "$SRC/layout_rules_llm.md"            "$DST/"
cp "$SRC/equations.md"                   "$DST/"
cp "$SRC/mermaid-best-practices.md"      "$DST/"
cp "$SRC/figure_rules.md"                "$DST/"
cp "$SRC/svg.md"                         "$DST/"
```

- [ ] **Step 2: Verify 7 files exist**

```bash
ls skills/deck-author/references/
```

Expected output includes all of:
```
accessibility-core.md
creating_good_presentations.md
design_rules.md
equations.md
figure_rules.md
layout_rules_llm.md
layouts.md
mermaid-best-practices.md
svg.md
```

- [ ] **Step 3: Commit**

```bash
git add skills/deck-author/references/
git commit -m "feat(deck-author): copy 7 reference files from md_to_yaml"
```

---

## Task 2: Copy flavor files from ada-slides-general

**Files:**
- Create: `skills/deck-author/references/flavor-explanatory.md`
- Create: `skills/deck-author/references/flavor-implementation.md`
- Create: `skills/deck-author/references/flavor-mathematical.md`
- Create: `skills/deck-author/references/flavor-tutorial.md`

- [ ] **Step 1: Copy the 4 flavor files**

```bash
SRC=.claude/skills/ada-slides-general
DST=skills/deck-author/references
cp "$SRC/flavor-explanatory.md"    "$DST/"
cp "$SRC/flavor-implementation.md" "$DST/"
cp "$SRC/flavor-mathematical.md"   "$DST/"
cp "$SRC/flavor-tutorial.md"       "$DST/"
```

- [ ] **Step 2: Verify 4 files exist**

```bash
ls skills/deck-author/references/flavor-*.md
```

Expected:
```
skills/deck-author/references/flavor-explanatory.md
skills/deck-author/references/flavor-implementation.md
skills/deck-author/references/flavor-mathematical.md
skills/deck-author/references/flavor-tutorial.md
```

- [ ] **Step 3: Commit**

```bash
git add skills/deck-author/references/
git commit -m "feat(deck-author): copy flavor files from ada-slides-general"
```

---

## Task 3: Initialise deck-author/SKILL.md from md_to_yaml

**Files:**
- Modify: `skills/deck-author/SKILL.md`

- [ ] **Step 1: Overwrite with md_to_yaml source**

```bash
cp .claude/skills/md_to_yaml/SKILL.md skills/deck-author/SKILL.md
```

- [ ] **Step 2: Verify line count sanity**

```bash
wc -l skills/deck-author/SKILL.md
```

Expected: ~535 lines (same as source).

---

## Task 4: Update SKILL.md — frontmatter and title

**Files:**
- Modify: `skills/deck-author/SKILL.md`

- [ ] **Step 1: Replace frontmatter (lines 1–5)**

Find:
```
---
name: md_to_yaml
description: Generate YAML DSL slide decks from PDF or folder input, then compile to ADA-compliant HTML using the bundled compiler in this skill folder. Use when the user wants to convert source material into a structured YAML slide deck (15-layout DSL including proof). Supports optional --detail (concise | standard | rich) to control overall deck length and how many slides are allocated per topic; outputs validated YAML plus compiled HTML; runs portably from the skill directory.
---
```

Replace with:
```
---
name: deck-author
description: Generate validated YAML+Markdown slide deck IR from source material (PDF, folder, markdown, or topic knowledge). Outputs a single .yaml file for deck-compile. Supports --source, --append, --detail, --figures, --tone, --name, --output-dir flags and four flavors (explanatory, implementation, tutorial, mathematical). Does not run the compiler; after generation, run deck-compile to validate and produce HTML.
---
```

- [ ] **Step 2: Replace title and intro line**

Find:
```
# YAML DSL Slide Generator

Generate validated YAML DSL slide decks from source material, then compile to ADA-compliant HTML. Uses a **15-layout** type system with schema validation and accessibility-oriented HTML.

**This skill folder contains a full copy of the `compiler/` and `schema/` packages.** Run validate/compile **from this directory** so imports resolve (`compiler`, `schema`). That keeps the skill **portable** across machines without relying on an external repo path.
```

Replace with:
```
# deck-author — YAML slide deck IR generator

Generate validated YAML+Markdown IR (Intermediate Representation) from source material. Output is a single `.yaml` file. Run **`deck-compile`** afterward to validate and produce HTML.
```

- [ ] **Step 3: Verify**

```bash
head -10 skills/deck-author/SKILL.md
```

Expected first line: `---` and `name: deck-author` on line 2.

---

## Task 5: Remove `--compile-only` from invocation section

**Files:**
- Modify: `skills/deck-author/SKILL.md`

- [ ] **Step 1: Remove the `--compile-only` invocation block**

Find and delete this exact block (including the blank line before it):

```

**Recompile without regenerating content** with `--compile-only`:

```
/md_to_yaml --compile-only path/to/existing.yaml
```

```

- [ ] **Step 2: Update all remaining `/md_to_yaml` invocation examples**

Run:
```bash
grep -n "md_to_yaml" skills/deck-author/SKILL.md
```

Replace every occurrence of `/md_to_yaml` in invocation examples with `/deck-author`.

Example — find:
```
/md_to_yaml <flavor> --source path/to/file.pdf
```
Replace with:
```
/deck-author <flavor> --source path/to/file.pdf
```

Apply the same pattern to every line returned by the grep.

- [ ] **Step 3: Verify no `--compile-only` remains**

```bash
grep "compile-only" skills/deck-author/SKILL.md
```

Expected: no output.

---

## Task 6: Remove "Bundled compiler" section

**Files:**
- Modify: `skills/deck-author/SKILL.md`

- [ ] **Step 1: Delete the Bundled compiler section**

Find and delete from:
```
## Bundled compiler (run from this folder)
```
through (and including) the line:
```
**Maintainers:** The `compiler/` and `schema/` trees are **copies** of the upstream `md_to_yaml` project. Re-copy from that project when fixing compiler bugs or updating templates.
```

The section is approximately 28 lines. After deletion, `## Source Types` should follow the invocation section directly.

- [ ] **Step 2: Verify**

```bash
grep "Bundled compiler\|Maintainers.*compiler.*schema" skills/deck-author/SKILL.md
```

Expected: no output.

---

## Task 7: Remove step 1c and update step 1b

**Files:**
- Modify: `skills/deck-author/SKILL.md`

- [ ] **Step 1: Remove step 1c entirely**

Find and delete:
```
1c. **`--compile-only` mode** (if present): Read the YAML at the given path. Skip steps 2–10 (no content generation). Go directly to step 13 (validate), step 14 (layout variety check), and step 15 (compile to HTML). Use the YAML file's own stem as `BASE`.
```

- [ ] **Step 2: Update step 1b closing sentence**

Find:
```
   Then skip forward to step 13 (validate the full deck, check layout variety, compile). Do **not** change the `BASE` name — overwrite the existing YAML and HTML in-place.
```

Replace with:
```
   Then skip forward to step 12 (write YAML). Do **not** change the `BASE` name — overwrite the existing YAML in-place. After writing, run `deck-compile` to validate and produce HTML.
```

- [ ] **Step 3: Verify**

```bash
grep "step 13\|step 14\|step 15\|compile-only" skills/deck-author/SKILL.md
```

Expected: no output.

---

## Task 8: Update Read paths in steps 3–9

**Files:**
- Modify: `skills/deck-author/SKILL.md`

Apply each substitution in order.

- [ ] **Step 1: Step 3 — creating_good_presentations**

Find:
```
   Read ./creating_good_presentations.md
```
Replace with:
```
   Read ./references/creating_good_presentations.md
```

- [ ] **Step 2: Step 4 — accessibility-core**

Find:
```
   Read ./accessibility-core.md
```
Replace with:
```
   Read ./references/accessibility-core.md
```

- [ ] **Step 3: Step 5 — flavor files**

Find:
```
   Read ../ada-slides-general/flavor-{flavor}.md
```
Replace with:
```
   Read ./references/flavor-{flavor}.md
```

- [ ] **Step 4: Step 6 — layout_rules_llm**

Find:
```
   Read {{skill_dir}}/layout_rules_llm.md
```
Replace with:
```
   Read ./references/layout_rules_llm.md
```

- [ ] **Step 5: Step 7 — equations**

Find:
```
   Read {{skill_dir}}/equations.md
```
Replace with:
```
   Read ./references/equations.md
```

- [ ] **Step 6: Step 9 — mermaid-best-practices**

Find:
```
   Read ./mermaid-best-practices.md
```
Replace with:
```
   Read ./references/mermaid-best-practices.md
```

- [ ] **Step 7: Step 9 — figure_rules**

Find:
```
   Read ./figure_rules.md
```
Replace with:
```
   Read ./references/figure_rules.md
```

- [ ] **Step 8: Step 9 — svg**

Find:
```
   Read ./svg.md
```
Replace with:
```
   Read ./references/svg.md
```

- [ ] **Step 9: Verify no legacy Read paths remain**

```bash
grep -n "Read \./[^r]\|Read \.\./ada\|Read {{skill_dir}}" skills/deck-author/SKILL.md
```

Expected: no output.

---

## Task 9: Remove steps 13–15 and add closing handoff

**Files:**
- Modify: `skills/deck-author/SKILL.md`

- [ ] **Step 1: Delete step 13 (Validate)**

Find and delete from:
```
13. **Validate** (from **this skill directory**):
```
through the blank line before `14.` (inclusive of the closing bullet):
```
    - Common issues: `body:` inside YAML frontmatter (move below `---`), invalid `layout`, missing `alt_text` on figure/diagram/two-column visual.
```

- [ ] **Step 2: Delete step 14 (Check layout variety)**

Find and delete:
```
14. **Check layout variety:**

    ```bash
    cd /path/to/this/skill/md_to_yaml
    export PYTHONPATH="$(pwd)"
    python3 -c "from schema.parser import parse_deck_file; from compiler.validators import validate_deck; deck = parse_deck_file('<yaml_path>'); errors, warnings = validate_deck(deck); [print(w) for w in warnings]"
    ```

    Address **3+ consecutive same-layout** warnings when practical.
```

- [ ] **Step 3: Delete step 15 (Compile to HTML)**

Find and delete from:
```
15. **Compile to HTML** (same **`BASE`** as in steps 11–12):
```
through (and including):
```
    Use absolute paths if the deck is outside this folder.
```

- [ ] **Step 4: Add closing handoff instruction after step 12**

Step 12 ends with:
```
    - No `--source` (topic-only) → current working directory.
```

After that line (before `## YAML Format Reference`), insert:

```

After writing the YAML file, inform the user:

> "IR written to `<path>`. Run **`deck-compile`** to validate and produce HTML:
> `./compile.sh <path>.yaml <path>.html --embed-images`"
```

- [ ] **Step 5: Verify**

```bash
grep -n "^13\.\|^14\.\|^15\." skills/deck-author/SKILL.md
```

Expected: no output.

```bash
grep "Run.*deck-compile" skills/deck-author/SKILL.md
```

Expected: one match (the closing handoff instruction).

---

## Task 10: Update YAML Format Reference and Design Guidance

**Files:**
- Modify: `skills/deck-author/SKILL.md`

- [ ] **Step 1: Update YAML filenames critical rule**

Find:
```
- **YAML and HTML filenames:** use the **same** basename for both — `<source_basename>-<flavor>-<depth>-<YYYYMMDD_HHMM>.yaml` and `.html` — so each compiled pair is unambiguous (see steps 11–15).
```

Replace with:
```
- **YAML filename:** use `<source_basename>-<flavor>-<YYYYMMDD_HHMM>.yaml`. The HTML basename is determined by `deck-compile` and matches the YAML stem.
```

- [ ] **Step 2: Update `--include-skipped` reference in YAML Format Reference**

Find:
```
Use `./compile.sh ... --include-skipped` to render a version that includes skipped slides.
```

Replace with:
```
Use `deck-compile` with `--include-skipped` to render a version that includes skipped slides.
```

- [ ] **Step 3: Add figure authoring rule to Design Guidance**

Find:
```
## Design Guidance
```

After the `## Design Guidance` heading line, insert:

```
- **Figure files:** write Mermaid source to `.mmd` files and SVG diagrams to `.svg` files in the figures folder. The YAML holds only `src:` path and `alt_text`. Inline Mermaid in `diagram` slide body is valid for simple cases but external files are preferred.
```

- [ ] **Step 4: Update Design Guidance bare file references**

Find:
```
- **Layout selection:** decision tree in `layout_rules_llm.md`.
- **Rhetoric and bullets:** `creating_good_presentations.md`.
- **Math:** `equations.md` — use `$...$` inline; `$$...$$` when the equation is the focal point of the slide. For the **`mathematical`** flavor, see **`mathematical` flavor: quantitative emphasis** below — the `$$...$$` frequency rule is relaxed.
- **Mermaid:** see `mermaid-best-practices.md` (read in step 9) for canvas aspect ratios, two-column stacking rules, color budgets, alt text, and diagram type selection.
```

Replace with:
```
- **Layout selection:** decision tree in `references/layout_rules_llm.md`.
- **Rhetoric and bullets:** `references/creating_good_presentations.md`.
- **Math:** `references/equations.md` — use `$...$` inline; `$$...$$` when the equation is the focal point of the slide. For the **`mathematical`** flavor, see **`mathematical` flavor: quantitative emphasis** below — the `$$...$$` frequency rule is relaxed.
- **Mermaid:** see `references/mermaid-best-practices.md` (read in step 9) for canvas aspect ratios, two-column stacking rules, color budgets, alt text, and diagram type selection.
```

- [ ] **Step 5: Verify no bare file references remain in Design Guidance**

```bash
grep "layout_rules_llm\.md\|creating_good_presentations\.md\|equations\.md\|mermaid-best-practices\.md" \
  skills/deck-author/SKILL.md | grep -v "references/"
```

Expected: no output.

- [ ] **Step 6: Add "Relationship to other skills" section before Error Recovery**

Find:
```
## Error Recovery
```

Insert before it:

```
## Relationship to other skills

- **`deck-compile`** — turns this IR into HTML; validators run **inside** compile. Point users there for `./compile.sh …` or `python3 -m compiler …`.
- **`figure-spec`** — optional structured briefs for figures before assets exist; produces `src` paths and `alt_text` to copy into the IR.

---

```

- [ ] **Step 7: Verify section present**

```bash
grep "Relationship to other skills" skills/deck-author/SKILL.md
```

Expected: one match.

---

## Task 11: Final verification and commit

**Files:**
- Read: `skills/deck-author/SKILL.md`
- Read: `skills/deck-author/references/` (directory listing)

- [ ] **Step 1: Confirm all 13 reference files present**

```bash
ls skills/deck-author/references/
```

Expected (13 files):
```
accessibility-core.md
creating_good_presentations.md
design_rules.md
equations.md
figure_rules.md
flavor-explanatory.md
flavor-implementation.md
flavor-mathematical.md
flavor-tutorial.md
layout_rules_llm.md
layouts.md
mermaid-best-practices.md
svg.md
```

- [ ] **Step 2: Confirm no forbidden references in SKILL.md**

```bash
grep "ada-slides-general\|compile-only\|Bundled compiler\|{{skill_dir}}\|Read \./[^r]" skills/deck-author/SKILL.md
```

Expected: no output.

- [ ] **Step 3: Confirm skill name is deck-author**

```bash
grep "^name:" skills/deck-author/SKILL.md
```

Expected:
```
name: deck-author
```

- [ ] **Step 4: Confirm step count ends at 12**

```bash
grep -E "^[0-9]+\. \*\*" skills/deck-author/SKILL.md | tail -5
```

Expected: last step numbered is `12`.

- [ ] **Step 5: Commit**

```bash
git add skills/deck-author/SKILL.md
git commit -m "feat(deck-author): rewrite SKILL.md as full IR generator pipeline"
```

---

## Task 12: Smoke test

- [ ] **Step 1: Check deck-compile still runs from its own directory**

```bash
cd skills/deck-compile
python3 -c "from schema.parser import parse_deck_file; print('schema OK')"
```

Expected:
```
schema OK
```

- [ ] **Step 2: Verify deck-author references no files outside its own folder**

```bash
grep -n "\.\./" skills/deck-author/SKILL.md
```

Expected: no output.

- [ ] **Step 3: Commit smoke-test confirmation (no code changes — just a note)**

If steps 1–2 passed with no output/errors, commit:

```bash
git commit --allow-empty -m "chore(deck-author): smoke test passed — skill split complete"
```
