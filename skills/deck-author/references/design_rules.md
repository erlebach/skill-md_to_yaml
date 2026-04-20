# Design rules (authoring)

These align with `validate_deck` in [`deck-compile`](../deck-compile/) and good slide hygiene.

## Mandatory

- **`alt_text`** on every `figure`, `diagram`, and on `two-column` columns whose `type` is `figure` or `diagram`.
- **No `body:` inside YAML frontmatter** — slide body is Markdown **below** the closing `---` of each slide.
- **Valid `layout`** only — see [`layouts.md`](layouts.md).

## Strongly recommended

- **Layout variety:** avoid **3+ consecutive** slides with the same `layout` (compiler warns).
- **Bullet load:** prefer ≤8 top-level bullets per slide body (compiler warns above 8).
- **Equations:** pair display math with short plain-language context where helpful; follow YAML quoting rules for LaTeX (see deck-compile / legacy `equations.md` in older skill trees if present in repo).
- **Mermaid:** raw diagram in `diagram` slide body (no triple-backtick fence); avoid problematic unquoted `|` / `<` / `>` in node labels—quote labels when needed.

## Forbidden in IR output (author)

- **No HTML**, **no CSS**, **no JavaScript** — the compiler owns structure and theme.
- Do not embed **MathML** or **rendered SVG** by hand unless you are intentionally pasting into a specialized workflow; prefer LaTeX in tables/body and Mermaid in `diagram` slides.

## Contrast

If you set **`accent_color`** in deck metadata, it must meet **4.5:1** against the theme background or compile **errors**.
