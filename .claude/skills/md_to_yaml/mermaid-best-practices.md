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
| Error / wrong | `#cc0000` | `#ffffff` | 5.9:1 ✓ | Saturated — preferred on dark slides |
| Error / wrong (pastel) | `#ffcccc` | `#000000` | 14.8:1 ✓ | Use on light-theme slides |
| Correct / good | `#1a7a1a` | `#ffffff` | 5.5:1 ✓ | Saturated — preferred on dark slides |
| Correct / good (pastel) | `#ccffcc` | `#000000` | 18.7:1 ✓ | Use on light-theme slides |
| Warning | `#a06000` | `#ffffff` | 5.0:1 ✓ | Use #a06000, not #b06800 (fails AA) |
| Neutral / info | `#1a4a8a` | `#ffffff` | 8.8:1 ✓ | |
| Highlight | `#f0a500` | `#000000` | 10.1:1 ✓ | Matches deck accent color |

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

---

## Diagram Type Selection

Do not default to `graph TD` for every diagram slide. Choose the type that matches
the information structure. Variety across a deck reduces visual fatigue.

| Diagram type | Mermaid keyword | Use when the slide shows... |
|---|---|---|
| Directed flowchart | `graph TD` / `graph LR` | Decision trees, causal chains, multi-step processes |
| 2×2 matrix | `quadrantChart` | Decision matrices, tradeoff grids, 2-axis comparisons |
| Sequence | `sequenceDiagram` | Ordered interactions, protocol steps, request/response |
| State machine | `stateDiagram-v2` | States and transitions (hypothesis test stages, model lifecycle) |
| Proportions | `pie` | Distribution of outcomes, composition of a dataset |
| Concept map | `mindmap` | Topic overviews, related-concept clusters |
| Ranked comparison | `xychart-beta` | Bar charts, growth curves (FWER vs number of tests) |
| Timeline | `timeline` | Historical sequence, algorithm evolution |

### Choosing direction for `graph`

- `TD` (top-down): hierarchies, causal chains where cause is "above" effect
- `LR` (left-right): pipelines, timelines, before→after sequences
- `RL` (right-left): rarely needed; use when reading direction matters
- `BT` (bottom-up): rarely needed; use when outcomes "rise from" inputs

### quadrantChart for decision matrices

The "Error Types and Power" decision matrix is better expressed as a `quadrantChart`
than four nodes in `graph TD`. Use `quadrantChart` for any 2×2 outcome grid.

```
quadrantChart
    title Decision Outcomes
    x-axis H₀ True --> H₁ True
    y-axis Fail to Reject --> Reject H₀
    quadrant-1 POWER (1 − β)
    quadrant-2 TYPE I ERROR (α)
    quadrant-3 Correct (1 − α)
    quadrant-4 TYPE II ERROR (β)
```

### sequenceDiagram for ordered processes

```
sequenceDiagram
    participant D as Data
    participant T as Test statistic
    participant N as Null distribution
    participant C as Decision
    D->>T: compute R
    T->>N: compare R to null
    N->>C: is R in rare tail?
    C-->>D: reject H₀ or fail to reject
```

### mindmap for concept overviews

```
mindmap
  root((False Discoveries))
    Random variation
    Multiple testing
      FWER
        Bonferroni
      FDR
        Benjamini–Hochberg
    Lack of replication
    Effect size ignored
```

### Deck-level diversity rule

A deck with 4 or more diagram slides should use at least 3 different Mermaid diagram
types. Review the full deck before finalising — if every diagram is `graph TD`, revise.

---

## Color Budget Rules

**Core principle: color should answer "why does this node matter?" — not decorate.**

### When to use color

| Situation | Rule |
|---|---|
| Node represents a semantic outcome (error, correct, warning) | Use semantic color from the approved pairs table above |
| One node is the key insight of the slide | Highlight that node only; leave all others default |
| Two competing states need visual separation | One color per state; maximum 2 colors |
| A step in a pipeline is the failure point or bottleneck | Highlight that step only |

### When NOT to use color

| Situation | Reason |
|---|---|
| All nodes are structurally equal steps in a process | Color implies hierarchy or importance that does not exist |
| More than 4 nodes would be colored | Signal is diluted; the diagram looks like a traffic light factory |
| The diagram type already encodes meaning via position (`quadrantChart`, `pie`) | Layout already carries the semantic load; color is redundant |
| Color would repeat information already in the label text | Redundant; adds visual noise without adding information |

### Color budget per diagram

| Budget | When to use |
|---|---|
| **0 colors** | Pure structural diagram — sequence, pipeline, concept map, `mindmap` |
| **1 color** | Single focal node: the conclusion, the failure point, the key insight |
| **2 colors** | Binary semantic split: correct vs error, pass vs fail, before vs after |
| **3 colors** | Three-way split (good / warning / bad) — use sparingly |
| **4 colors** | Maximum. More than 4 colored nodes always hurts clarity |

### Anti-patterns

```
-- BAD: coloring every node differently adds no information --
style A fill:#ccffcc
style B fill:#ffcccc
style C fill:#ccffff
style D fill:#ffff99
style E fill:#ffccff

-- GOOD: color only the nodes that differ semantically --
style ErrorNode fill:#cc0000,color:#ffffff
style CorrectNode fill:#1a7a1a,color:#ffffff
-- A, C, D, E use Mermaid default colors --
```
