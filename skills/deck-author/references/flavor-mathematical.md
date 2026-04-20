# Flavor: Mathematical

Use this flavor for lectures, seminars, or reading-group presentations where the core content is mathematical — theorems, derivations, proofs, algorithms with formal guarantees, or rigorous analyses. The goal is to build genuine understanding, not just name-drop results.

---

## Theme

Dark. Use the GitHub-dark palette from `accessibility-core.md` (same as `flavor-explanatory.md`).

---

## Tone

**Rigorous but narrative.** Don't just display symbol chains — motivate each step, name what you're doing ("apply Jensen's inequality here"), and bridge between derivations with one-sentence connectives. The audience should feel the logic, not just see it.

- State the *why* before the *how*: "We want to bound the variance, so we will apply Chebyshev."
- Name the technique when you use it: "By the triangle inequality…", "Expanding the square…", "Recall that…"
- End derivation sequences with a plain-English consequence: what did we just prove and why does it matter?

---

## Slide Patterns

### Canonical sequence for a mathematical result

1. **Motivation slide** (`layout: content` or `layout: hero`) — why this result matters; what problem it solves
2. **Setup / notation slide** (`layout: content`) — state all variables, spaces, and assumptions clearly
3. **Statement slide** (`layout: content`) — the theorem or claim in a box-style bullet with display math
4. **Intuition / geometric slide** (`layout: diagram` or `layout: figure`) — a curve, a geometric picture, a phase diagram, or an architecture that makes the result "visible"
5. **Proof / derivation slide(s)** (`layout: proof`) — the actual steps; mark optional with `skip: true` if the audience may not need it
6. **Consequence slide** (`layout: content`) — corollaries, special cases, why the bound is tight or loose

### When to use `layout: proof`

- Any slide whose primary content is a chain of mathematical steps leading to a claimed conclusion.
- Typical body: a short ordered or unordered list where each bullet is one step (`- **Step 1:** Apply Jensen's inequality to get $f(\mathbb{E}[X]) \leq \mathbb{E}[f(X)]$`).
- Use display math `$$...$$` sparingly on proof slides — only when the equation is the focal point. Inline `$...$` for everything else.
- Proof slides are the most natural candidates for `skip: true` when compiling a "broad audience" version.

### When to skip

Place `skip: true` on any slide that:
- Contains a proof or derivation your audience can read in the paper
- Is a technical lemma that supports a later result but isn't itself the point
- Is a calculation detail (change of variables, summation index shift) that interrupts narrative flow

The YAML source retains the full proof; the compiled HTML shows only what you need for the talk.

---

## Math Style on Slides

- **Display math `$$...$$`:** Use when the equation *is* the slide — the main theorem, a key inequality, a closed-form result. One display block per slide maximum.
- **Inline math `$...$`:** For all other uses — variables, subscripts, short expressions in bullets.
- **Bullet subheaders with math:** Keep the subheader and its formula in one `**...**` run: `**Variance bound: $\text{Var}[X] \leq \sigma^2$** ...`. Don't split `**Variance bound**` + `$...$` or the math renders body-colored.
- **Named quantities:** Introduce each symbol once on the setup slide. Don't re-define on every slide.
- **Equation numbering:** Not supported by the compiler. Reference equations by name ("the bound from the previous slide") rather than number.

---

## Figures and Diagrams

Mathematical presentations benefit from more visuals than other flavors — every major result should have at least one visual companion.

### Mermaid diagram types — choose by content

| Math content | Recommended Mermaid type |
|---|---|
| Algorithm flow, proof structure | `graph TD` or `graph LR` (flowchart) |
| Iterative/recursive process | `graph TD` with self-edges or sequence steps |
| Data / distribution curve | `xychart-beta` (line or bar) |
| System architecture, pipeline | `graph LR` or `architecture-beta` |
| Taxonomy / hierarchy | `graph TD` |
| Timeline of a proof or method history | `timeline` |
| Part-of-whole, allocation | `pie` |
| Flow with labeled quantities | `sankey-beta` |
| Mindmap of concepts | `mindmap` |

**Mermaid `architecture-beta`** is a newer diagram type (experimental 🔥) suited for showing system components and their connections — good for ML pipeline architectures, encoder–decoder structures, or multi-stage algorithms. Syntax: named `service` nodes and `junction` nodes with edge labels.

**`xychart-beta`** renders native line and bar charts directly in Mermaid — use for:
- Convergence curves (loss vs. iteration)
- Distribution comparisons
- Scaling relationships (log-scale approximations)
- Error rates vs. threshold

When a curve needs precise point values, prefer `xychart-beta` line chart over a flowchart approximation.

### When to use `layout: figure` instead of `layout: diagram`

Use `layout: figure` with a real image file (`src:`) when:
- The curve or diagram was produced by a plotting library (matplotlib, etc.) and cannot be faithfully approximated in Mermaid
- The figure is from the source paper and carries important visual information (phase diagrams, multi-panel comparisons)

For everything else, prefer Mermaid — it stays fully embedded in the HTML, scales cleanly, and respects the dark theme.

### Pairing diagrams with derivations

A powerful pattern for `--detail rich`:
```
proof slide (skip: true)  ←— full derivation, optional
diagram slide             ←— geometric picture of the same result (always shown)
content slide             ←— consequence / interpretation (always shown)
```

This lets you show the intuition and consequence to a broad audience while the proof is available for those who want it.

---

## Layout Selection for Mathematical Content

| Situation | Layout |
|---|---|
| Theorem / claim statement | `content` — bold the claim as a subheader bullet |
| Proof or derivation | `proof` |
| Geometric intuition / curve | `diagram` (Mermaid) or `figure` (image) |
| Proof sketch + geometric picture side by side | `two-column` (proof in text column, diagram in figure column) |
| Two competing bounds or methods | `comparison` |
| Assumptions or notation list | `content` |
| Algorithm steps | `steps` |
| Complexity table / benchmark | `table` |
| Major result summary | `summary` |
| Section opener | `divider` |

---

## Detail Level and Mathematical Flavor

**`--detail concise`:** One slide per major result (statement + consequence). Skip proofs entirely — mark all `proof` slides `skip: true` and optionally omit them from the YAML too.

**`--detail standard`:** Statement + intuition + key proof step (as one `proof` slide, possibly skipped) + consequence per result.

**`--detail rich`:** Full canonical sequence (motivation → setup → statement → intuition → proof → consequence) per result. Add comparison slides for competing approaches. Add a "proof technique taxonomy" content slide if multiple results use the same trick.

---

## Mermaid Node Label Rules (Mathematical Content)

Quantum and linear-algebra notation often contains `|`, `<`, `>`, `†`, and other characters that break unquoted Mermaid labels.

**Always double-quote labels containing special math characters:**
```
graph TD
  A["State |ψ⟩"] --> B["Apply U†"]
  B --> C["Measure in basis {|0⟩, |1⟩}"]
```

For bra-ket notation, consider ASCII approximations in node labels and use the text column for the full notation.

---

## Example Slide Sequence (Hoeffding's Inequality)

```yaml
---
layout: hero
title: Hoeffding's Inequality
description: "How confident can we be in a sample mean when we only see n draws?"
---

---
layout: content
title: Setup and Assumptions
---
- $X_1, \ldots, X_n$ independent, each bounded: $a_i \leq X_i \leq b_i$.
- **Goal:** bound $P(\bar{X} - \mathbb{E}[\bar{X}] \geq t)$ for any $t > 0$.
- **Why it matters:** finite-sample guarantees without knowing the distribution.

---
layout: content
title: The Statement
---
- **Hoeffding's Inequality:** for any $t > 0$,
$$P\!\left(\bar{X} - \mathbb{E}[\bar{X}] \geq t\right) \leq \exp\!\left(\frac{-2n^2 t^2}{\sum_{i=1}^n (b_i - a_i)^2}\right)$$
- The bound depends only on the **range** $b_i - a_i$, not on the shape of the distribution.
- For equal ranges $b_i - a_i = c$: bound simplifies to $\exp(-2nt^2/c^2)$.

---
layout: diagram
title: Bound Tightens with More Samples
alt_text: "Line chart showing the Hoeffding upper bound as a function of n for fixed t equals 0.1 and range equals 1. The curve falls steeply from near 1 at n equals 1 toward zero as n grows, illustrating exponential improvement."
---
xychart-beta
  title "Hoeffding bound vs n (t=0.1, range=1)"
  x-axis "n" [1, 5, 10, 20, 50, 100, 200]
  y-axis "Upper bound" 0 --> 1.0
  line [0.98, 0.61, 0.37, 0.14, 0.007, 0.0000454, 0.0]

---
layout: proof
skip: true
title: "Proof Sketch: Moment Generating Function Argument"
---
- **Step 1:** For bounded $X_i$, Hoeffding's lemma gives $\mathbb{E}[e^{sX_i}] \leq \exp\!\left(\frac{s^2(b_i - a_i)^2}{8}\right)$.
- **Step 2:** By independence, $\mathbb{E}[e^{s(\bar{X} - \mu)}] \leq \exp\!\left(\frac{s^2 \sum (b_i - a_i)^2}{8n^2}\right)$.
- **Step 3:** Apply Markov's inequality to $e^{s(\bar{X}-\mu)}$ and optimize over $s > 0$.
- **Conclusion:** Minimizing over $s$ yields the stated exponential bound. $\square$

---
layout: content
title: Consequence — Sample Complexity
---
- Rearranging: to achieve $P(\bar{X} - \mu \geq \varepsilon) \leq \delta$, we need
$$n \geq \frac{c^2 \ln(1/\delta)}{2\varepsilon^2}$$
- Sample complexity scales as $O(\varepsilon^{-2} \log \delta^{-1})$ — standard in PAC learning.
- Larger range $c$ demands more samples; tighter tolerance $\varepsilon$ demands quadratically more.
```

---

## Quantitative Emphasis Rules (md_to_yaml skill supplement)

These rules augment the general guidance above when generating slides with the `md_to_yaml` skill. They override general guidance where they conflict.

1. **`proof` is the default layout for formal content.** Use `proof` for:
   - Formal definitions with symbolic notation (e.g., rejection criterion $R \in C_\alpha$)
   - Named theorems or lemmas (e.g., Neyman–Pearson Lemma, Bayes' theorem)
   - Exact calculations showing intermediate steps — not just a final decimal
   - Derivations of key quantities (power formula, FWER, expected false-positive count)

2. **Display math (`$$...$$`) is expected on most `proof` slides** and on any `content` slide whose main point is a formula. The "1–2 per deck" guideline in `equations.md` applies to other flavors; for `mathematical`, use `$$...$$` wherever the equation is the focal point of the slide.

3. **Formula-first structure on `proof` slides.** Lead with the display formula, then add 2–4 contextual bullets that:
   - Define each symbol in the formula with inline `$...$`
   - Give a concrete numerical example computed from the formula
   - State a key consequence, limit, or special case

4. **Quantitative bullets on `content` slides.** Even ordinary `content` slides should carry inline `$...$` to give conditions, parameter ranges, or scaling relationships — not purely verbal descriptions. Examples:
   - Instead of "doubling the sample size increases power," write "power grows as $\sqrt{n}$: doubling $n$ multiplies the argument by $\sqrt{2}$"
   - Instead of "a small p-value triggers rejection," write "reject $H_0$ when $p < \alpha$, where $\alpha$ is committed before seeing the data"

5. **Augment tables with formula columns.** When a `table` slide lists methods or tests, add a column for the test statistic or decision threshold (e.g., $R = $ two-sample $t$; threshold $= \alpha/m$).

6. **Surface the algebra behind verbal claims.** When a claim can be substantiated with a short derivation, add the derivation as a `proof` slide or inline in a bullet:
   - p-value fallacy → show Bayes' theorem: $P(H_0 \mid R) = P(R \mid H_0)\,\pi_0 / P(R)$
   - "Controls any false positive" → Union bound: $P\!\left(\bigcup_i A_i\right) \le \sum_i P(A_i)$
   - "Power grows with $n$" → write out the z-test power formula $\Phi\!\left(\delta\sqrt{n}/\sigma - z_\alpha\right)$
   - "Expected false positives" → derive $E[\text{FP}] = m_0\,\alpha$ explicitly with a numeric example

7. **YAML quoting for math-heavy strings.** In `table` `rows:` and `headers:`, always use **single quotes** for cells containing `\sim`, `\mathrm`, `\xrightarrow`, `\mathcal`, `\text`, or any macro where `\X` could be misread as a YAML escape in double-quoted strings (e.g., `\s`, `\t`, `\n`, `\a`). See `equations.md` — *YAML quoting and LaTeX* — for the full rules.
