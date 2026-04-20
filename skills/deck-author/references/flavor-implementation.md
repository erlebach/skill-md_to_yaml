# Flavor: Implementation

Use this flavor for developer-facing decks: system architecture walkthroughs, API usage guides, deployment procedures, performance optimization talks, and any deck where code and commands are primary content.

---

## Theme

Dark. Use a dark palette with a distinct cyan-blue accent to visually differentiate from explanatory (blue) and tutorial (amber).

```css
:root {
  --bg:        #0d1117;
  --bg2:       #161b22;
  --bg3:       #21262d;
  --text:      #e6edf3;
  --muted:     #8b949e;
  --accent:    #39c5cf;
  --green:     #3fb950;
  --orange:    #f0883e;
  --border:    #30363d;
  --code-bg:   #f6f8fa;
  --code-text: #1f2328;
  --code-border: #d0d7de;
  --sidebar-w: 220px;
  --dots-h:    48px;
}

body {
  font-family: "Source Sans 3", Arial, Helvetica, sans-serif;
  background: var(--bg);
  color: var(--text);
}
```

Google Fonts import:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

---

## Mermaid Initialization

```js
mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#21262d',
    primaryTextColor: '#e6edf3',
    primaryBorderColor: '#39c5cf',
    lineColor: '#8b949e',
    secondaryColor: '#161b22',
    tertiaryColor: '#0d1117',
    fontFamily: '"Source Sans 3", Arial, Helvetica, sans-serif',
    fontSize: '14px'
  }
});
```

---

## Code Blocks

Code is the star of this flavor. Code blocks use a **light background with dark text** — this makes them visually pop against the dark slide, like a printed listing. Inline code spans use the same light treatment. Individual math formulas (MathJax/KaTeX) inherit the slide's light text color and do NOT use the light code background.

```css
pre, code {
  font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace;
  font-size: 15px;
  line-height: 1.6;
}

.code-block {
  background: var(--code-bg);       /* #f6f8fa — light background */
  color: var(--code-text);          /* #1f2328 — dark text, WCAG AA on #f6f8fa */
  border: 1px solid var(--code-border);
  border-left: 4px solid var(--accent);
  border-radius: 0 6px 6px 0;
  padding: 16px 20px;
  margin: 12px 0;
  overflow-x: auto;
  white-space: pre;
}

/* Ensure pre inherits code-block colors */
.code-block code {
  color: var(--code-text);
  background: transparent;
}

code.inline {
  background: var(--code-bg);
  color: var(--code-text);
  border: 1px solid var(--code-border);
  border-radius: 3px;
  padding: 1px 6px;
  font-size: 0.9em;
}
```

Wrap code in a `<figure>` with a `<figcaption>` when the code block illustrates a specific concept:

```html
<figure>
  <pre class="code-block"><code>python train.py \
  --model llama-7b \
  --batch-size 32 \
  --gradient-checkpointing</code></pre>
  <figcaption>Launch training with gradient checkpointing enabled to reduce peak GPU memory by ~33%.</figcaption>
</figure>
```

For short inline references, use `<code class="inline">`:
```html
Set <code class="inline">--zero-stage 3</code> in your DeepSpeed config.
```

---

## Layout Principles

| Content type | Recommended layout |
|-------------|-------------------|
| Code + explanation | Code left (`.two-col-wide-narrow`) or full-width with annotation below |
| Architecture diagram | Mermaid full-width or left, component list right |
| Step-by-step procedure | Numbered list with code blocks inline |
| Before/after comparison | Two-column: old pattern left, new pattern right |
| Performance table | Full-width table with accent header |
| Warning / note callout | `.callout-warning` or `.callout-tip` box |

**Side-by-side code + explanation** is the signature layout of this flavor:

```html
<div class="two-col-wide-narrow">
  <figure>
    <pre class="code-block"><code>
# ZeRO Stage 3 config
{
  "zero_optimization": {
    "stage": 3,
    "offload_optimizer": { "device": "cpu" }
  }
}
    </code></pre>
    <figcaption>DeepSpeed config enabling ZeRO-3 with CPU optimizer offloading.</figcaption>
  </figure>
  <div>
    <h3>What this does</h3>
    <ul>
      <li>Shards parameters across all GPUs</li>
      <li>Moves optimizer states to CPU DRAM</li>
      <li>Enables training beyond GPU VRAM limits</li>
    </ul>
  </div>
</div>
```

---

## Mermaid Diagram Style

Wrap every diagram in `.mermaid-wrap`:

```css
.mermaid-wrap {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 20px;
  margin: 12px 0;
  display: flex;
  justify-content: center;
  overflow-x: auto;
}
```

Use architecture-style diagrams (flowcharts, sequence diagrams) to show system interactions. Keep colors aligned with the dark palette:
```
style NodeName fill:#39c5cf,stroke:#39c5cf,color:#0d1117
style NodeName fill:#3fb950,stroke:#3fb950,color:#0d1117
style NodeName fill:#f0883e,stroke:#f0883e,color:#0d1117
```

---

## Callout Boxes

```css
.callout-tip {
  background: rgba(63, 185, 80, 0.12);
  border-left: 4px solid var(--green);
  padding: 12px 16px;
  border-radius: 0 6px 6px 0;
  margin: 12px 0;
  font-size: 17px;
  color: var(--text);
}
.callout-warning {
  background: rgba(240, 136, 62, 0.12);
  border-left: 4px solid var(--orange);
  padding: 12px 16px;
  border-radius: 0 6px 6px 0;
  margin: 12px 0;
  font-size: 17px;
  color: var(--text);
}
.callout-tip::before   { content: "Tip: "; font-weight: bold; color: var(--green); }
.callout-warning::before { content: "Warning: "; font-weight: bold; color: var(--orange); }
```

Usage:
```html
<div class="callout-tip">
  <p>Use BF16 instead of FP16 on Ampere GPUs — it avoids loss scaling complexity and is numerically more stable.</p>
</div>
<div class="callout-warning">
  <p>ZeRO-3 adds All-Gather overhead at every forward pass. Benchmark before deploying at scale.</p>
</div>
```

---

## Available Layout Classes

```css
.two-col              { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 8px; }
.two-col-narrow-wide  { display: grid; grid-template-columns: 2fr 3fr; gap: 32px; margin-top: 8px; }
.two-col-wide-narrow  { display: grid; grid-template-columns: 3fr 2fr; gap: 32px; margin-top: 8px; }

.card-grid  { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; margin-top: 8px; }
.card       { background: var(--bg2); border: 1px solid var(--border); border-radius: 8px; padding: 18px; }
.card-title { font-size: 17px; font-weight: bold; color: var(--accent); margin-bottom: 6px; }

.step-list  { counter-reset: steps; list-style: none; margin: 0; padding: 0; }
.step-list li {
  counter-increment: steps;
  padding: 10px 0 10px 48px;
  position: relative;
  border-bottom: 1px solid var(--border);
}
.step-list li::before {
  content: counter(steps);
  position: absolute; left: 0; top: 10px;
  width: 30px; height: 30px;
  background: var(--accent); color: #fff;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: bold; font-size: 14px;
}
```

---

## Navigation Chrome

> **CRITICAL**: Use the SlideEngine JS from `visual-explainer/references/slide-patterns.md` — NOT anchor-link (`location.href='#sN'`) navigation. The SlideEngine manages active states on dots and sidebar links automatically. Do NOT write `onclick="location.href='#sN'"` on dots or sidebar links. Do NOT use `<div id="main">` as the slide container — use `<div class="deck">` with scroll-snap.

CSS for sidebar and dots appearance (styles only — behavior comes from SlideEngine):

```css
#sidebar {
  position: fixed; top: 0; left: 0;
  width: var(--sidebar-w); height: 100vh;
  background: var(--bg2); border-right: 1px solid var(--border);
  overflow-y: auto; padding: 16px 0; z-index: 100;
}
#sidebar .sidebar-title {
  font-size: 13px; font-weight: bold; color: var(--muted);
  letter-spacing: 0.04em; padding: 0 16px 12px;
  border-bottom: 1px solid var(--border); margin-bottom: 8px;
}
#sidebar a {
  display: block; padding: 8px 16px;
  color: var(--muted); text-decoration: none;
  font-size: 13px; line-height: 1.4;
  border-left: 3px solid transparent;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}
#sidebar a:hover, #sidebar a:focus-visible {
  color: var(--text); background: var(--bg3); border-left-color: var(--accent);
}
#sidebar a.active { color: var(--accent); border-left-color: var(--accent); }

#dots {
  position: fixed; bottom: 0; left: var(--sidebar-w); right: 0;
  height: var(--dots-h); background: var(--bg2);
  border-top: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  gap: 8px; z-index: 100; flex-wrap: wrap; padding: 0 12px;
}
.dot {
  width: 26px; height: 26px; min-width: 26px; min-height: 26px;
  border-radius: 50%; border: 2px solid var(--muted);
  background: transparent; cursor: pointer;
  font-size: 10px; color: var(--muted);
  display: flex; align-items: center; justify-content: center;
}
.dot:hover { border-color: var(--accent); color: var(--accent); }
.dot.active { background: var(--accent); border-color: var(--accent); color: var(--bg); }

/* Deck — replaces #main. Scroll-snap is mandatory. */
.deck {
  margin-left: var(--sidebar-w);
  height: 100dvh;
  overflow-y: auto;
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
  padding-bottom: var(--dots-h);
}

@media (max-width: 900px) {
  :root { --sidebar-w: 0px; }
  #sidebar { display: none; }
  .slide { padding: 28px 20px 44px; }
  .two-col, .two-col-narrow-wide, .two-col-wide-narrow { grid-template-columns: 1fr; }
}
```

---

## Slide Anatomy

```css
.slide {
  height: 100dvh;
  scroll-snap-align: start;
  overflow: hidden;
  padding: 44px 52px 52px;
  border-bottom: 2px solid var(--border);
  display: flex;
  flex-direction: column;
}
.slide-hero {
  background: linear-gradient(135deg, #0d1117 0%, #0d2137 60%, #0d1a2e 100%);
  justify-content: center;
}
.slide-number {
  font-size: 13px; color: var(--muted); font-weight: bold;
  letter-spacing: 0.08em; margin-bottom: 14px;
}
h1.slide-title { color: var(--accent); }
h2.slide-title { color: var(--text); }
h3 { font-size: 21px; font-weight: 600; color: var(--accent); margin-bottom: 8px; margin-top: 20px; }
.lead { font-size: 24px; color: var(--muted); line-height: 1.5; }
```

---

## Tables

```css
table { width: 100%; border-collapse: collapse; font-size: 17px; margin: 10px 0; }
th { background: var(--accent); color: #fff; text-align: left; padding: 9px 12px; font-weight: bold; }
td { padding: 8px 12px; border: 1px solid var(--border); color: var(--text); vertical-align: top; }
tr:nth-child(even) td { background: var(--bg2); }
```
