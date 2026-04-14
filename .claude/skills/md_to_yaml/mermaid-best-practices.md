# Mermaid Diagram Best Practices

This file governs how Mermaid diagrams are authored in YAML slide decks.
All rules apply to `diagram` layout slides that use Mermaid source.

---

## Contrast in Colored Nodes (WCAG 1.4.3)

**Rule: whenever you set `fill:` in a `style` directive, you MUST also set `color:`.**

Mermaid's dark theme inherits a near-white default text color. On a light-background
node (pastel fills, white, light gray) the inherited text becomes unreadable.
The compiler injects `color:#000000` as a safety net, but explicit authoring
is required — do not rely on the fallback.

### Required pattern

```
style NodeId fill:#ffcccc,color:#000000
style NodeId fill:#ccffcc,color:#000000
```

### Forbidden pattern

```
style NodeId fill:#ffcccc       ← missing color: — ADA failure without compiler patch
```

---

## Approved Color Pairs for Mermaid Nodes

These pairs are pre-verified at WCAG AA (≥ 4.5:1). Use them for semantic coloring
(error = red family, success/correct = green family, neutral = blue/gray family).

| Semantic role | fill | color | Contrast | Notes |
|---------------|------|-------|----------|-------|
| Error / wrong | `#cc0000` | `#ffffff` | 5.1:1 ✓ | Saturated — preferred on dark slides |
| Error / wrong (pastel) | `#ffcccc` | `#000000` | 12.5:1 ✓ | Use on light-theme slides |
| Correct / good | `#1a7a1a` | `#ffffff` | 5.6:1 ✓ | Saturated — preferred on dark slides |
| Correct / good (pastel) | `#ccffcc` | `#000000` | 14.1:1 ✓ | Use on light-theme slides |
| Warning | `#b06800` | `#ffffff` | 4.7:1 ✓ | |
| Neutral / info | `#1a4a8a` | `#ffffff` | 7.2:1 ✓ | |
| Highlight | `#f0a500` | `#000000` | 8.9:1 ✓ | Matches deck accent color |

---

## Theme Alignment

The deck theme is `dark` by default. Choose fills accordingly:

- **Dark slides**: use saturated fills (`#cc0000`, `#1a7a1a`) with `color:#ffffff`
- **Light slides** (`theme: light`): use pastel fills (`#ffcccc`, `#ccffcc`) with `color:#000000`

Mixing pastel fills on dark-background slides creates low-perceived contrast
even when the text technically passes — prefer saturated fills on dark decks.

---

## Do Not Rely on Color Alone (WCAG 1.4.1)

Color alone must not be the only way information is conveyed. In decision matrices
and flowcharts, also include text labels that describe the semantic meaning
(e.g. "TYPE I ERROR", "CORRECT") — not just colored boxes.

---

## Alt Text

Every `diagram` slide must have `alt_text:` in the YAML describing the diagram's
conclusion in plain English, not just its structure.

```yaml
# Good
alt_text: "Decision matrix showing Type I error (false positive) and Type II error (false negative) outcomes."

# Bad
alt_text: "Diagram with four boxes."
```

---

## Subgraph Labels

Subgraph titles (e.g. `subgraph Reality: H0 True`) are rendered as plain text
inside the Mermaid SVG. They inherit the theme foreground color and are generally
readable, but verify visually after compile — Mermaid version upgrades can change
subgraph label styling.
