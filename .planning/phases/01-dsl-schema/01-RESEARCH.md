# Phase 1: DSL Schema - Research

**Researched:** 2026-03-21
**Domain:** Pydantic v2 schema design, hybrid YAML+Markdown parsing, JSON Schema generation
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **12 layout types:** title, hero, content, divider, figure, diagram, two-column, quote, comparison, code, steps, summary
- `title` = deck opener (big title + subtitle + author). `hero` = section opener (section title + short description). Separate types with different visual treatment.
- `figure` = raster images (JPEG/PNG) with src, alt_text. `diagram` = SVG/Mermaid with source code, alt_text. Separate types due to different required fields and rendering pipelines.
- `summary` layout type is at Claude's discretion (whether distinct from `content` or a styled variant).
- Table layout deferred to Phase 3 (Rich Content).
- Layout list is extensible — new types can be added in later phases without schema redesign.
- **Hybrid format:** YAML frontmatter (between `---` markers) for structured fields + free Markdown body for content.
- Each slide has its own frontmatter block; slides separated by `---`.
- First frontmatter block is deck-level metadata.
- File extension: `.yaml`.
- Custom parser needed (split on `---`, parse YAML frontmatter, treat remainder as Markdown body).
- **Two-column convention:** Structured content (image/diagram/Mermaid) goes in frontmatter as `left:` or `right:`. Markdown body fills the "free content" column. If both columns are free text, body uses `<!-- split -->` marker. If both structured, both in frontmatter.
- **Mermaid:** Full-width → Mermaid code in Markdown body as fenced code block. Two-column → Mermaid goes in frontmatter under `left.source:` or `right.source:`.
- **Shared fields on every layout:** `layout` (required), `title` (required), `notes` (optional).
- `alt_text` required on all visual types (figure, diagram).
- **Strict validation** — unknown fields produce clear error messages. No silent alias coercion.
- Layout-specific fields use natural names (`attribution` on quote, `language` on code, `src` on figure).
- **Deck metadata:** first frontmatter block. `title` only required field. Optional: `author`, `date`, `theme`, `accent_color`, `font`.
- Defaults: no author, today's date, dark theme, amber accent, IBM Plex Sans.
- Two themes in v1: dark and light.
- `font` validated against preset list (e.g., IBM Plex Sans, Inter, Fira Sans) — not arbitrary.
- Speaker notes: optional `notes` field on every slide, rendered as `<aside>`.

### Claude's Discretion

- Whether `summary` layout is distinct from `content` or just a styled variant.
- Exact Pydantic model inheritance hierarchy (base model, mixins, per-layout models).
- JSON Schema generation approach (Pydantic's built-in `.model_json_schema()` or custom).
- Validation error message formatting.
- Which font presets to include in the validated set.

### Deferred Ideas (OUT OF SCOPE)

- Table layout type — deferred to Phase 3 (Rich Content).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DSL-01 | Hybrid YAML+Markdown format: YAML frontmatter per slide + Markdown content body | Custom parser design: split on `---`, parse YAML block, treat remainder as Markdown body |
| DSL-02 | ~15 layout primitives derived from analysis of existing HTML decks | Deck analysis confirms: title, hero, content, divider, figure, diagram, two-column, quote, comparison, code, steps, summary (12 decided + potential summary variant) |
| DSL-03 | Each layout type has a Pydantic model with required/optional fields and validation | Pydantic v2 2.12.5 with discriminated unions and `model_config = ConfigDict(extra='forbid')` |
| DSL-04 | Schema enforces structural consistency across layout types (isomorphic where possible) | Base model with shared fields + per-layout subclasses; discriminated union on `layout` field |
| DSL-05 | Deck-level metadata section (title, author, date, theme) defined in schema | Separate `DeckMetadata` Pydantic model; title required, rest optional with defaults |
| DSL-06 | JSON Schema generated from Pydantic models for external validation | `model.model_json_schema()` built into Pydantic v2 — no extra dependencies |
</phase_requirements>

---

## Summary

Phase 1 delivers a purely Python artifact: Pydantic v2 models defining 12 slide layout types plus deck metadata, a custom file parser that splits the hybrid `.yaml` format into frontmatter+body pairs, and a JSON Schema export. No compiler, no rendering, no HTML — just the schema and its validation machinery.

The existing HTML decks (20 files in `n8n_to_python/output_html_files/`) confirm the layout primitives in use: `slide--content`, `slide-hero`, `slide--figure`, `slide--title`, `slide--divider`, `slide--diagram`, `two-col`, `step-list`, and `code-block` class names were all found. The decided layout list maps directly to these observed classes. The `two-column` layout is the most complex due to its flexible content permutations (text+image, image+text, text+text, image+image).

Pydantic v2 (current: 2.12.5) is the correct choice. Its discriminated union feature enables parsing a list of heterogeneous slide dicts into the correct typed model with one call. `model_json_schema()` is built-in and requires no extra tooling. `ConfigDict(extra='forbid')` enforces strict validation automatically.

**Primary recommendation:** Define a `SlideBase` with shared fields (`layout`, `title`, `notes`), per-layout subclasses with `Literal` type discriminators, a `Annotated` union type, and parse the whole deck file with a 3-step parser: split-on-fence → YAML-load frontmatter → validate with Pydantic.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | 2.12.5 | Model definition, validation, JSON Schema export | Industry standard for Python data validation; v2 is Rust-backed, 5-10x faster than v1; discriminated unions are built-in |
| PyYAML | 6.0.3 | Parse YAML frontmatter blocks | De-facto standard YAML parser in Python ecosystem |
| pytest | 9.0.2 | Test fixtures — validate good/bad YAML files | Universal Python test framework |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-cov | 4.x | Coverage reporting | When running full test suite |
| python-dateutil | 2.x | Parse and validate date fields in metadata | If flexible date input formats needed (e.g., "March 21, 2026" → `date` type) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyYAML | ruamel.yaml | ruamel preserves comments and round-trips; not needed here since we only parse, never write back |
| Pydantic v2 | attrs + cattrs | pydantic dominates for JSON Schema export and LLM tooling integration |
| Custom JSON Schema | pydantic's built-in | Custom gives more control over `$defs` naming; built-in is sufficient for this phase |

**Installation:**
```bash
pip install pydantic==2.12.5 PyYAML==6.0.3 pytest==9.0.2
```

**Version verification (confirmed 2026-03-21):**
- pydantic: 2.12.5 (latest on PyPI)
- PyYAML: 6.0.3 (latest on PyPI)
- pytest: 9.0.2 (latest on PyPI)

---

## Architecture Patterns

### Recommended Project Structure

```
md_to_yaml/
├── schema/
│   ├── __init__.py
│   ├── models.py          # All Pydantic models (DeckMetadata, SlideBase, per-layout)
│   ├── parser.py          # Hybrid file parser (split → YAML → validate)
│   └── json_schema.py     # JSON Schema export utility
├── tests/
│   ├── fixtures/
│   │   ├── valid_deck.yaml       # Happy-path: all 12 layout types
│   │   ├── invalid_missing_alt.yaml   # Missing alt_text on figure
│   │   ├── invalid_unknown_field.yaml # Unknown field triggers error
│   │   └── deck_metadata.yaml    # Deck-level metadata variants
│   ├── test_models.py     # Unit tests: each model's required/optional fields
│   ├── test_parser.py     # Unit tests: file splitting, frontmatter extraction
│   └── test_json_schema.py  # JSON Schema generation + round-trip validation
└── .planning/
    └── phases/01-dsl-schema/
```

### Pattern 1: Discriminated Union on `layout` Field

**What:** A single `Annotated[Union[...], Field(discriminator="layout")]` type covers all slide variants. Pydantic routes each dict to the correct subclass based on the `layout` value. Unknown layout values produce a clear validation error automatically.

**When to use:** Any time a list field contains heterogeneous typed dicts with a shared tag field.

**Example:**
```python
# Source: Pydantic v2 docs — discriminated unions
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field, ConfigDict

class SlideBase(BaseModel):
    model_config = ConfigDict(extra='forbid')
    layout: str
    title: str
    notes: str | None = None

class TitleSlide(SlideBase):
    layout: Literal['title']
    subtitle: str | None = None
    author: str | None = None

class ContentSlide(SlideBase):
    layout: Literal['content']
    # body comes from Markdown, not frontmatter

class FigureSlide(SlideBase):
    layout: Literal['figure']
    src: str
    alt_text: str          # required — ADA-01

class DiagramSlide(SlideBase):
    layout: Literal['diagram']
    alt_text: str          # required — ADA-01

class CodeSlide(SlideBase):
    layout: Literal['code']
    language: str
    # code body comes from Markdown fenced block

AnySlide = Annotated[
    Union[TitleSlide, ContentSlide, FigureSlide, DiagramSlide, CodeSlide, ...],
    Field(discriminator='layout')
]
```

### Pattern 2: Deck Model as Top-Level Container

**What:** A `Deck` model holds `DeckMetadata` plus a `list[AnySlide]`. Parsing and validation happen together.

**Example:**
```python
from pydantic import BaseModel, field_validator
from datetime import date

class DeckMetadata(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str
    author: str | None = None
    date: date | None = None   # defaults to today in CLI
    theme: Literal['dark', 'light'] = 'dark'
    accent_color: str | None = None   # validated for contrast in Phase 2
    font: Literal['IBM Plex Sans', 'Inter', 'Fira Sans', 'Roboto'] = 'IBM Plex Sans'

class Deck(BaseModel):
    metadata: DeckMetadata
    slides: list[AnySlide]
```

### Pattern 3: Hybrid File Parser

**What:** Custom 3-step parser for the `.yaml` file format.

**When to use:** Every time a deck file is loaded — by the compiler (Phase 2) and by the validator (this phase).

**Example:**
```python
import yaml
from pydantic import TypeAdapter

def parse_deck_file(path: str) -> Deck:
    text = open(path).read()
    # Split on YAML document separators
    # First block is deck metadata, rest are slides
    blocks = _split_blocks(text)
    metadata = DeckMetadata(**yaml.safe_load(blocks[0]))
    slides = []
    for block in blocks[1:]:
        parts = block.split('\n\n', 1)  # frontmatter vs body
        frontmatter = yaml.safe_load(parts[0]) if parts[0].strip() else {}
        body = parts[1] if len(parts) > 1 else ''
        frontmatter['_body'] = body.strip()   # carry Markdown body through
        slide_adapter = TypeAdapter(AnySlide)
        slides.append(slide_adapter.validate_python(frontmatter))
    return Deck(metadata=metadata, slides=slides)
```

Note: The `_body` field pattern is one approach — the planner should decide whether the Markdown body field is part of the Pydantic model (as an excluded-from-schema field) or injected post-validation.

### Pattern 4: Two-Column Structured Content

**What:** `TwoColumnSlide` frontmatter carries optional `left` and `right` structured blocks. The Markdown body carries free-text for whichever column is unstructured.

**Example:**
```yaml
---
layout: two-column
title: Kernel Function
left:
  type: figure
  src: kernel.png
  alt_text: Gaussian kernel density plot
---
Each data point contributes a smooth influence function...
```

```yaml
---
layout: two-column
title: Comparison
---
Left side free text

<!-- split -->

Right side free text
```

### Pattern 5: JSON Schema Export

**What:** Use Pydantic's built-in `model_json_schema()` on the `Deck` model. Write to a `.json` file.

**Example:**
```python
import json

schema = Deck.model_json_schema()
with open('schema/deck.schema.json', 'w') as f:
    json.dump(schema, f, indent=2)
```

Pydantic v2 generates `$defs` for each submodel and uses `anyOf` + `const` discriminators. The output is valid JSON Schema Draft 2020-12.

### Anti-Patterns to Avoid

- **Pydantic v1 style:** Do not use `class Config:` inner class — use `model_config = ConfigDict(...)` (Pydantic v2 style).
- **`extra='allow'`:** Never use this. It masks typos in field names silently. Always `extra='forbid'`.
- **Flat model with all possible fields:** Don't put every layout's fields on one giant model with everything optional. Use per-layout subclasses with discriminated unions.
- **Pre-validation alias coercion:** The context locked "no silent alias coercion." Do not use `validation_alias` to accept both `body` and `content` — validate strictly and emit the "did you mean" message in a custom `@model_validator`.
- **Storing Markdown body inside Pydantic model with schema export:** The Markdown body is content, not schema. Either exclude it from `model_json_schema()` output using `exclude=True` on the field, or handle body as a separate dataclass wrapper around the Pydantic model.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON Schema generation | Manual dict assembly | `model.model_json_schema()` | Pydantic v2 handles `$defs`, `anyOf`, discriminators, required/optional correctly — hundreds of edge cases |
| YAML parsing | String split + regex | `yaml.safe_load()` | YAML has 50+ edge cases (multiline strings, special chars, anchors, aliases) |
| Discriminated routing | `if layout == 'figure'` chain | `TypeAdapter(AnySlide).validate_python(data)` | Pydantic's discriminated union validates AND routes in one call, with clear error messages |
| Date parsing/validation | `datetime.strptime` chain | Pydantic `date` field type | Pydantic handles ISO 8601 + validation automatically |
| Required field enforcement | Manual `if field not in data` | Pydantic required fields (no default) | Pydantic generates the error message, field path, and type information |

**Key insight:** Pydantic v2 IS the schema — the models are the schema. Every feature that seems like it needs custom code (required fields, type coercion, JSON Schema export, discriminated routing) is already built in. The main custom work is only the file parser.

---

## Common Pitfalls

### Pitfall 1: YAML `---` Separator Ambiguity

**What goes wrong:** The `---` separator used to split slides is also valid inside YAML values (e.g., a code block in the Markdown body containing `---`).

**Why it happens:** The file format uses `---` both as a YAML document separator and as a Markdown horizontal rule / slide boundary.

**How to avoid:** Parse the file section-by-section: read until `---` at the START of a line only (regex `^---$` with `re.MULTILINE`). The Markdown body section may contain `---` safely inside code fences.

**Warning signs:** Parser produces extra empty slide blocks or misaligned slide indices.

### Pitfall 2: Pydantic v1 vs v2 API Confusion

**What goes wrong:** Pydantic v1 patterns (`validator`, `class Config`, `.dict()`, `.schema()`) do not work in v2.

**Why it happens:** Many tutorials and Stack Overflow answers are still v1. Training data is mixed.

**How to avoid:** Use ONLY v2 APIs: `@field_validator`, `@model_validator`, `ConfigDict`, `.model_dump()`, `.model_json_schema()`.

**Warning signs:** `AttributeError: 'ModelMetaclass' object has no attribute 'schema'` or deprecation warnings at import.

### Pitfall 3: Discriminated Union with `None` Variant

**What goes wrong:** If `AnySlide` includes `None` as a possible type, Pydantic's error messages become confusing.

**Why it happens:** Slides are never optional in the list — each block must parse to a specific layout.

**How to avoid:** Do not include `None` in the `AnySlide` union. Make parsing fail loudly if a block's `layout` field is missing or unknown.

### Pitfall 4: JSON Schema `$defs` Naming Instability

**What goes wrong:** Pydantic v2 names `$defs` entries by model class name. Renaming a class changes the JSON Schema output, breaking downstream validators.

**Why it happens:** `model_json_schema()` uses Python class names as `$defs` keys.

**How to avoid:** Use `model_config = ConfigDict(title='FigureSlide')` on each model to lock the title regardless of class name. Or accept the coupling and document that class names are public API.

### Pitfall 5: Two-Column Body Split Edge Cases

**What goes wrong:** `<!-- split -->` marker may have surrounding whitespace, be inside a code fence, or appear multiple times.

**Why it happens:** LLMs generating the YAML file may produce slightly different whitespace patterns.

**How to avoid:** Strip and normalize the `<!-- split -->` split in the parser. If marker appears more than once, use only the first occurrence. Document this in the DSL spec.

### Pitfall 6: `date` Field Default — "Today" Is Not Static

**What goes wrong:** Setting `date = date.today()` as a Pydantic default means the schema's default is evaluated once at class definition time in Python < 3.11, or dynamically via `default_factory`.

**Why it happens:** Pydantic v2 distinguishes `default` (static) from `default_factory` (called each time).

**How to avoid:** Use `Field(default_factory=date.today)` for the `date` field in `DeckMetadata`.

---

## Code Examples

### SlideBase and Discriminated Union (complete)

```python
# Source: Pydantic v2 docs - https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions
from __future__ import annotations
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field, ConfigDict
from datetime import date

class SlideBase(BaseModel):
    model_config = ConfigDict(extra='forbid')
    layout: str
    title: str
    notes: str | None = None

class TitleSlide(SlideBase):
    layout: Literal['title']
    subtitle: str | None = None
    author: str | None = None

class HeroSlide(SlideBase):
    layout: Literal['hero']
    description: str | None = None

class ContentSlide(SlideBase):
    layout: Literal['content']

class DividerSlide(SlideBase):
    layout: Literal['divider']

class FigureSlide(SlideBase):
    layout: Literal['figure']
    src: str
    alt_text: str

class DiagramSlide(SlideBase):
    layout: Literal['diagram']
    alt_text: str

class ColumnContent(BaseModel):
    model_config = ConfigDict(extra='forbid')
    type: Literal['figure', 'diagram']
    src: str | None = None        # for figure
    alt_text: str | None = None   # required when type is figure or diagram

class TwoColumnSlide(SlideBase):
    layout: Literal['two-column']
    left: ColumnContent | None = None
    right: ColumnContent | None = None

class QuoteSlide(SlideBase):
    layout: Literal['quote']
    attribution: str | None = None

class ComparisonSlide(SlideBase):
    layout: Literal['comparison']

class CodeSlide(SlideBase):
    layout: Literal['code']
    language: str = 'text'

class StepsSlide(SlideBase):
    layout: Literal['steps']

class SummarySlide(SlideBase):
    layout: Literal['summary']

AnySlide = Annotated[
    Union[
        TitleSlide, HeroSlide, ContentSlide, DividerSlide,
        FigureSlide, DiagramSlide, TwoColumnSlide, QuoteSlide,
        ComparisonSlide, CodeSlide, StepsSlide, SummarySlide,
    ],
    Field(discriminator='layout')
]
```

### DeckMetadata

```python
from pydantic import field_validator

VALID_FONTS = ('IBM Plex Sans', 'Inter', 'Fira Sans', 'Roboto', 'Source Sans 3')

class DeckMetadata(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str
    author: str | None = None
    date: date | None = Field(default_factory=date.today)
    theme: Literal['dark', 'light'] = 'dark'
    accent_color: str | None = None
    font: str = 'IBM Plex Sans'

    @field_validator('font')
    @classmethod
    def validate_font(cls, v: str) -> str:
        if v not in VALID_FONTS:
            raise ValueError(f"font must be one of: {', '.join(VALID_FONTS)}")
        return v
```

### JSON Schema Export

```python
import json
from pydantic import RootModel

class Deck(BaseModel):
    metadata: DeckMetadata
    slides: list[AnySlide]

# Export
schema = Deck.model_json_schema()
with open('schema/deck.schema.json', 'w') as f:
    json.dump(schema, f, indent=2)
```

### File Parser Skeleton

```python
import re
import yaml
from pydantic import TypeAdapter

FENCE_RE = re.compile(r'^---\s*$', re.MULTILINE)
SPLIT_MARKER = '<!-- split -->'

def parse_deck_file(path: str) -> Deck:
    text = open(path, encoding='utf-8').read().strip()
    # Strip leading ---
    if text.startswith('---'):
        text = text[3:]
    parts = FENCE_RE.split(text)
    # parts[0] = deck metadata YAML
    # parts[1..] = alternating frontmatter + body (need re-pairing)
    # Because each slide block is: frontmatter\nbody\n---\n
    # after split: [metadata_yaml, slide1_fm, slide1_body+slide2_fm, ...]
    # Actual split behavior depends on file format — test thoroughly
    metadata_raw = yaml.safe_load(parts[0]) or {}
    metadata = DeckMetadata(**metadata_raw)
    slide_adapter = TypeAdapter(AnySlide)
    slides = []
    # Pair up frontmatter and body blocks — implementation detail for planner
    return Deck(metadata=metadata, slides=slides)
```

Note: The exact pairing logic depends on whether the file uses `---` between every slide or only as a frontmatter fence. The CONTEXT.md says "Each slide has its own frontmatter block; slides separated by `---`". A slide consists of `---\nfrontmatter\n---\nbody\n`. This means each slide uses TWO `---` markers (open + close frontmatter), making the split produce 3 parts per slide. Test fixtures must exercise this.

---

## Layout Primitive Evidence from Existing Decks

Analysis of 20 HTML decks in `n8n_to_python/output_html_files/`:

| HTML Class Observed | Count | Maps to DSL Layout |
|---------------------|-------|--------------------|
| `slide--content` | 47 | `content` |
| `slide-hero` | 21 | `hero` |
| `slide-figure` / `slide--figure` | 14 | `figure` |
| `slide--title` / `slide-title` | many | `title` |
| `slide--divider` | 1 | `divider` |
| `slide--diagram` | 1 | `diagram` |
| `two-col` | 100+ | `two-column` |
| `two-col-narrow-wide` | 6 | `two-column` variant |
| `step-list` | 8 | `steps` |
| `code-block` | 8 | `code` |

Observations:
- `two-column` is the most common complex layout, appearing in nearly every deck.
- `steps` and `code` are implementation-specific and appear in technical decks.
- `comparison`, `quote`, and `summary` are not directly evidenced in existing HTML — they are planned additions to increase layout variety. This is expected since the new DSL is a superset of current practice.
- The existing `two-col-narrow-wide` and `two-col-wide-narrow` variants suggest the `two-column` type may need an optional `proportion` field (e.g., `50/50`, `40/60`) for Phase 2 to map to CSS grid templates. This is at Claude's discretion for Phase 1.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pydantic v1 `validator` decorator | Pydantic v2 `@field_validator` / `@model_validator` | Pydantic 2.0 (2023) | Validators are classmethods; cleaner composition |
| `.dict()` method | `.model_dump()` | Pydantic 2.0 | Old name still works with deprecation warning |
| `.schema()` method | `.model_json_schema()` | Pydantic 2.0 | Returns JSON Schema Draft 2020-12 |
| `class Config:` inner class | `model_config = ConfigDict(...)` | Pydantic 2.0 | Type-safe configuration |
| Union with string tag routing | `Annotated[Union[...], Field(discriminator='field')]` | Pydantic 1.9+ | Built-in discriminated union, no custom validator needed |

**Deprecated/outdated:**
- `pydantic.validator`: replaced by `@field_validator` — do not use.
- `BaseModel.__fields__`: replaced by `model_fields` — do not use.
- `BaseModel.schema()`: replaced by `model_json_schema()` — do not use.

---

## Open Questions

1. **Markdown body as part of Pydantic model or not?**
   - What we know: The Markdown body is parsed separately from the frontmatter. It must reach the compiler.
   - What's unclear: Should it be stored on the Pydantic slide model (excluded from JSON Schema via `exclude=True`) or in a wrapper dataclass?
   - Recommendation: Store as an optional `body: str | None = Field(None, exclude=True)` on `SlideBase`. This keeps the deck as one object but excludes body content from the JSON Schema export. Planner should decide.

2. **`summary` layout distinctness**
   - What we know: User left this to Claude's discretion.
   - Recommendation: Make `summary` a distinct layout type (not an alias for `content`) with the same fields as `content`. This allows Phase 2 to render it with a visually distinct template (e.g., checkmark bullet style) without schema changes.

3. **Two-column proportion field**
   - What we know: Existing decks use `two-col-narrow-wide` and `two-col-wide-narrow` CSS classes.
   - What's unclear: Is this a Phase 1 schema concern or Phase 2 CSS concern?
   - Recommendation: Add an optional `proportion: Literal['50/50', '40/60', '60/40'] = '50/50'` field to `TwoColumnSlide` in Phase 1 so Phase 2 can use it. Adding it later would require a schema revision.

4. **File extension `.yaml` with hybrid content**
   - What we know: The file extension is `.yaml` but the content is not pure YAML — it contains Markdown bodies.
   - What's unclear: Will standard YAML linters/editors complain about the hybrid format?
   - Recommendation: Document this as a "YAML-adjacent" format. The extension signals the frontmatter format, not the full file format. Not a blocking concern for Phase 1.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | `pytest.ini` or `pyproject.toml [tool.pytest.ini_options]` — Wave 0 gap |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v --tb=short` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DSL-01 | Hybrid file with frontmatter + Markdown body parses without error | integration | `pytest tests/test_parser.py::test_parse_valid_deck -x` | Wave 0 |
| DSL-01 | Slide body is correctly extracted from multi-slide file | unit | `pytest tests/test_parser.py::test_body_extraction -x` | Wave 0 |
| DSL-02 | All 12 layout types parse from YAML to correct Pydantic model | unit | `pytest tests/test_models.py::test_all_layout_types -x` | Wave 0 |
| DSL-03 | Missing required field (e.g., `alt_text` on figure) raises ValidationError | unit | `pytest tests/test_models.py::test_missing_alt_text -x` | Wave 0 |
| DSL-03 | Unknown field raises ValidationError with actionable message | unit | `pytest tests/test_models.py::test_unknown_field -x` | Wave 0 |
| DSL-04 | All layout types share `layout`, `title`, `notes` fields | unit | `pytest tests/test_models.py::test_shared_fields -x` | Wave 0 |
| DSL-05 | Deck metadata with only `title` validates (all optionals have defaults) | unit | `pytest tests/test_models.py::test_deck_metadata_minimal -x` | Wave 0 |
| DSL-05 | Invalid theme value raises ValidationError | unit | `pytest tests/test_models.py::test_invalid_theme -x` | Wave 0 |
| DSL-05 | Invalid font raises ValidationError | unit | `pytest tests/test_models.py::test_invalid_font -x` | Wave 0 |
| DSL-06 | `Deck.model_json_schema()` returns valid JSON Schema | unit | `pytest tests/test_json_schema.py::test_schema_generates -x` | Wave 0 |
| DSL-06 | Generated JSON Schema validates the same test fixtures (round-trip) | integration | `pytest tests/test_json_schema.py::test_schema_validates_fixtures -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/fixtures/valid_deck.yaml` — all 12 layout types, valid
- [ ] `tests/fixtures/invalid_missing_alt.yaml` — figure slide missing `alt_text`
- [ ] `tests/fixtures/invalid_unknown_field.yaml` — slide with unknown field `body`
- [ ] `tests/fixtures/deck_metadata_minimal.yaml` — only `title` in metadata
- [ ] `tests/test_models.py` — unit tests for all model variants
- [ ] `tests/test_parser.py` — parser unit and integration tests
- [ ] `tests/test_json_schema.py` — JSON Schema export and round-trip tests
- [ ] `tests/conftest.py` — shared fixtures (fixture file paths, loaded deck objects)
- [ ] `pytest.ini` or `pyproject.toml` — pytest configuration
- [ ] `schema/__init__.py`, `schema/models.py`, `schema/parser.py`, `schema/json_schema.py` — implementation files
- [ ] Framework install: `pip install pydantic==2.12.5 PyYAML==6.0.3 pytest==9.0.2`

---

## Sources

### Primary (HIGH confidence)

- PyPI registry (2026-03-21) — pydantic 2.12.5, PyYAML 6.0.3, pytest 9.0.2 version verification
- Existing HTML decks in `n8n_to_python/output_html_files/` — layout primitive analysis (20 files, direct code inspection)
- CONTEXT.md Phase 1 decisions — locked implementation choices

### Secondary (MEDIUM confidence)

- Pydantic v2 discriminated unions API — consistent with training data (v2 stable since 2023); verified via pip availability of 2.12.5
- PyYAML `safe_load` for YAML frontmatter parsing — standard community practice

### Tertiary (LOW confidence)

- `<!-- split -->` marker convention for two-column free-text — invented for this project, no external reference; needs empirical validation during implementation
- `proportion` field recommendation for `TwoColumnSlide` — inferred from existing CSS class names, not explicitly decided

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions confirmed via PyPI registry 2026-03-21
- Architecture: HIGH — Pydantic v2 discriminated union pattern is well-established; layout list confirmed against existing decks
- Pitfalls: HIGH — Pydantic v1→v2 migration pitfalls are well-known; YAML separator ambiguity is empirically grounded
- Two-column edge cases: MEDIUM — `<!-- split -->` marker is a new convention, behavior under edge cases needs implementation testing

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (stable libraries; Pydantic v2 API is stable)
