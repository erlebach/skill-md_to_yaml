# GSAP in md_to_yaml

This document tracks how the `md_to_yaml` skill uses the **GSAP** animation library
to drive declarative, JS-free slide animations from YAML. It will be updated as new
animations are added.

## Goal

Authors should never write JavaScript or HTML in their YAML decks. They opt into an
animation by setting a single key on a slide (or deck-level defaults), and the
compiler emits a single GSAP `<script>` block in the HTML output that drives every
animated slide.

## How it flows

1. **YAML author** sets a key like `bullet_animation:` or `bullet_focus:` on a slide
   (per-slide), or under `animation_defaults:` in the deck frontmatter (deck-wide).
2. **Pydantic schema** (`schema/models.py`) validates the value as a bool or a
   typed settings object.
3. **Skill defaults** in `schema/animation_defaults.py` provide a baseline that fills
   any field the deck and slide both omit.
4. **Compiler engine** (`compiler/engine.py`) merges three layers — skill defaults,
   deck `animation_defaults`, slide overrides — and serializes the merged config
   to a JSON string stored in a `data-*` attribute on the slide `<section>`.
5. **Template** (`compiler/templates/base.html.j2`) emits **one** `<script src="…gsap…">`
   tag plus an IIFE that scans the document for those `data-*` attributes and
   wires the animation. The IIFE checks
   `prefers-reduced-motion` and degrades gracefully.

## Files affected

| File | Purpose |
| --- | --- |
| `schema/animation_defaults.py` | Skill-level defaults (`SKILL_GSAP_SCRIPT_URL_DEFAULT`, `SKILL_BULLET_STAGGER_DEFAULTS`, `SKILL_BULLET_FOCUS_DEFAULTS`). |
| `schema/models.py` | Pydantic models: `BulletStaggerSettings`, `BulletFocusSettings`, `AnimationDefaults`; per-slide fields `bullet_animation`, `bullet_focus`; deck-level `gsap_script_url` and `animation_defaults`. |
| `schema/deck.schema.json` | Auto-generated from the Pydantic models. Run `PYTHONPATH=. uv run python -m schema.json_schema` after schema edits. |
| `compiler/engine.py` | `_merge_bullet_stagger_config`, `_merge_bullet_focus_config`, `_bullet_stagger_json`, `_bullet_focus_json`; sets `has_bullet_animation` and `gsap_script_url` template vars. |
| `compiler/templates/base.html.j2` | Emits `data-bullet-stagger` / `data-bullet-focus` attributes per section, and the GSAP IIFE that drives both animations. |
| `examples/mycontent.yaml` | Reference deck demonstrating each animation. |

## Animations and YAML controls

### 1. `bullet_animation` — staggered reveal on viewport entry

Triggered when the slide scrolls into view; bullets fade and slide in with a stagger.

**Per-slide YAML:**

```yaml
---
layout: content
title: Staggered bullets
bullet_animation: true       # use defaults
# or:
bullet_animation:
  duration: 0.6
  stagger: 0.2
  ease: power2.out
  threshold: 0.45            # IntersectionObserver threshold
  x_offset: -28              # initial horizontal offset (px)
---
- First bullet
- Second bullet
```

**Deck-level defaults** (frontmatter):

```yaml
animation_defaults:
  bullet_stagger:
    duration: 0.5
    stagger: 0.14
    ease: power2.out
    threshold: 0.45
    x_offset: -28
```

**Skill defaults** (used when both deck and slide omit a key):

| key | default |
| --- | --- |
| `duration` | `0.45` |
| `stagger`  | `0.12` |
| `ease`     | `power2.out` |
| `threshold` | `0.45` |
| `x_offset` | `-24.0` |

### 2. `bullet_focus` — key-driven focus walker

The first bullet starts fully opaque; the others are dimmed. Pressing the
forward key advances focus; the backward key reverses it. Exactly one bullet is
fully opaque at any time. Useful for talking through bullets one-by-one without
slide transitions.

**Per-slide YAML:**

```yaml
---
layout: content
title: Focus walker
bullet_focus: true           # use defaults (j forward, k back)
# or:
bullet_focus:
  key: j                     # forward key
  back_key: k                # backward key
  dim: 0.25                  # opacity for non-focused bullets
  duration: 0.3
  ease: power2.out
---
- First (starts focused)
- Second
- Third
```

**Deck-level defaults** (frontmatter):

```yaml
animation_defaults:
  bullet_focus:
    key: j
    back_key: k
    dim: 0.25
    duration: 0.3
    ease: power2.out
```

**Skill defaults:**

| key | default |
| --- | --- |
| `key`        | `j` |
| `back_key`   | `k` |
| `dim`        | `0.25` |
| `duration`   | `0.3` |
| `ease`       | `power2.out` |

**Behavior notes:**

- Keys are ignored when modifier keys (Ctrl/Meta/Alt) are held or when an
  `INPUT`, `TEXTAREA`, or `contenteditable` element is focused.
- Forward presses past the last bullet and back presses before the first
  bullet are no-ops (no wrapping).
- When multiple `bullet_focus` slides exist, an `IntersectionObserver` (threshold
  0.5) tracks which slide is in view; key presses are routed to the active one.
- With `prefers-reduced-motion: reduce`, all bullets are shown at full opacity
  and key presses do not animate.
- `bullet_animation` and `bullet_focus` are independent; do not enable both on
  the same slide (their opacity settings will conflict).

## Deck-wide controls

Set on the deck frontmatter:

| key | purpose | default |
| --- | --- | --- |
| `gsap_script_url` | HTTPS URL for the GSAP CDN bundle. | `https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js` |
| `animation_defaults.bullet_stagger` | Defaults merged before per-slide `bullet_animation`. | (see skill defaults above) |
| `animation_defaults.bullet_focus` | Defaults merged before per-slide `bullet_focus`. | (see skill defaults above) |

## Adding a new animation

The pattern, in order:

1. Add `SKILL_<NAME>_DEFAULTS` to `schema/animation_defaults.py`.
2. Add a `BaseModel` (`<Name>Settings`) in `schema/models.py` and expose it as
   a field on the relevant slide model(s) and on `AnimationDefaults`.
3. Add a `_merge_<name>_config` + `_<name>_json` in `compiler/engine.py`, store
   the JSON string in `slides_context`, and OR it into `has_bullet_animation`
   so the GSAP script tag is emitted.
4. Render a `data-<name>` attribute on the slide `<section>` in
   `compiler/templates/base.html.j2`, and add a block inside the existing IIFE
   that consumes the attribute and drives GSAP. Always honor
   `prefers-reduced-motion`.
5. Regenerate `schema/deck.schema.json` with
   `PYTHONPATH=. uv run python -m schema.json_schema`.
6. Add a demo slide to `examples/mycontent.yaml` and recompile with
   `bash .claude/skills/md_to_yaml/compile.sh examples/mycontent.yaml examples/mycontent.html`.
7. Document the new animation in this file.
