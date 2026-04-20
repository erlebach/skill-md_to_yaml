# Flavor: Tutorial

Use this flavor for hands-on learning decks: guided workshops, step-by-step labs, onboarding walkthroughs, and any deck where the learner is expected to do something — not just understand something.

---

## Theme

Dark with warm amber accents. Distinct from the explanatory flavor (blue accents) to signal "action required."

```css
:root {
  --bg:        #0f0e0c;
  --bg2:       #1a1814;
  --bg3:       #252219;
  --text:      #e8e0d0;
  --muted:     #9a9080;
  --accent:    #d4a843;   /* amber — signals interactivity */
  --green:     #4caf6e;
  --orange:    #e07040;
  --blue:      #5a9fd4;   /* secondary for concepts */
  --border:    #36322a;
  --code-bg:   #1a1814;
  --sidebar-w: 220px;
  --dots-h:    48px;
}

body {
  font-family: "DM Sans", Arial, Helvetica, sans-serif;
  background: var(--bg);
  color: var(--text);
}
```

Google Fonts import:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

---

## Mermaid Initialization

```js
mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#252219',
    primaryTextColor: '#e8e0d0',
    primaryBorderColor: '#d4a843',
    lineColor: '#9a9080',
    secondaryColor: '#1a1814',
    tertiaryColor: '#0f0e0c',
    fontFamily: '"DM Sans", Arial, Helvetica, sans-serif',
    fontSize: '14px'
  }
});
```

---

## Tutorial Structure

Every tutorial deck must follow a scaffolded progression. Use this slide order as the template:

1. **Title / objectives** — what the learner will be able to do by the end
2. **Concept introduction** — brief theory, Mermaid diagram, no more than one slide
3. **Worked example** — instructor walks through a complete solution step by step
4. **Exercise** — learner attempts a similar problem (exercise box with instructions)
5. **Solution / debrief** — reveal the answer with annotation
6. **Checkpoint** — quick self-check questions before proceeding
7. Repeat concept → example → exercise → checkpoint for each learning unit
8. **Summary** — recap of what was learned with a skill checklist

---

## Exercise Boxes

Exercise boxes are the primary differentiator of this flavor. They must be visually distinct and clearly labeled.

```css
.exercise-box {
  background: var(--bg3);
  border: 2px solid var(--accent);
  border-radius: 8px;
  padding: 20px 24px;
  margin: 16px 0;
  position: relative;
}
.exercise-box::before {
  content: "Exercise";
  display: block;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--accent);
  margin-bottom: 10px;
  text-transform: uppercase;  /* exception: label text — single word, functional */
}
.exercise-box h3 {
  font-size: 20px;
  color: var(--text);
  margin-top: 0;
  margin-bottom: 10px;
}
.exercise-box ol, .exercise-box ul {
  color: var(--text);
}

.solution-box {
  background: var(--bg3);
  border: 2px solid var(--green);
  border-radius: 8px;
  padding: 20px 24px;
  margin: 16px 0;
}
.solution-box::before {
  content: "Solution";
  display: block;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--green);
  margin-bottom: 10px;
  text-transform: uppercase;
}

.checkpoint-box {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-top: 3px solid var(--blue);
  border-radius: 6px;
  padding: 16px 20px;
  margin: 16px 0;
}
.checkpoint-box::before {
  content: "Check your understanding";
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: var(--blue);
  margin-bottom: 10px;
}
```

Usage:
```html
<div class="exercise-box">
  <h3>Configure ZeRO-2 for a 13B model</h3>
  <p>Starting from the template below, modify the DeepSpeed config to enable ZeRO Stage 2 with gradient sharding.</p>
  <ol>
    <li>Set <code class="inline">stage</code> to 2</li>
    <li>Enable <code class="inline">allgather_partitions</code></li>
    <li>Set <code class="inline">overlap_comm</code> to true</li>
  </ol>
</div>

<div class="solution-box">
  <pre class="code-block"><code>{ "zero_optimization": { "stage": 2, "allgather_partitions": true, "overlap_comm": true } }</code></pre>
  <p>With <code class="inline">overlap_comm: true</code>, gradient communication is pipelined with backward computation, reducing idle time.</p>
</div>

<div class="checkpoint-box">
  <ul>
    <li>What does ZeRO-2 shard that ZeRO-1 does not?</li>
    <li>When would you choose ZeRO-3 over ZeRO-2?</li>
  </ul>
</div>
```

---

## Code Blocks

Use the same monospace font as the implementation flavor, but style against the dark background:

```css
pre, code {
  font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace;
  font-size: 15px;
  line-height: 1.6;
}

.code-block {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  border-radius: 0 6px 6px 0;
  padding: 16px 20px;
  margin: 12px 0;
  overflow-x: auto;
  white-space: pre;
  color: var(--text);
}

code.inline {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 1px 6px;
  font-size: 0.9em;
  color: var(--accent);
}
```

---

## Layout Principles

| Content type | Recommended layout |
|-------------|-------------------|
| Concept intro | Mermaid diagram (full or left) + brief bullets right |
| Worked example | Step list with inline code blocks |
| Exercise | Exercise box full-width, code template inside |
| Side-by-side walkthrough | Two-col: annotated code left, step explanation right |
| Checkpoint | Checkpoint box full-width |
| Summary | Skill checklist card-grid |

**Progress indicator on each slide** — learners need to know where they are in the tutorial sequence. Use a progress badge:

```html
<div class="progress-badge">Step 3 / 7</div>
```

```css
.progress-badge {
  display: inline-block;
  background: var(--accent);
  color: var(--bg);
  font-size: 13px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 12px;
  margin-bottom: 14px;
}
```

---

## Skill Checklist (Summary Slide)

Use on the final slide to let learners self-assess:

```html
<div class="skill-checklist">
  <h3>What you can now do</h3>
  <ul>
    <li class="skill-item">Configure ZeRO stages in DeepSpeed</li>
    <li class="skill-item">Choose between ZeRO-1, 2, and 3 based on model size</li>
    <li class="skill-item">Profile GPU memory usage with <code class="inline">nvidia-smi</code></li>
  </ul>
</div>
```

```css
.skill-checklist { margin: 16px 0; }
.skill-item {
  padding: 8px 0 8px 32px;
  position: relative;
  border-bottom: 1px solid var(--border);
  list-style: none;
  color: var(--text);
}
.skill-item::before {
  content: "✓";
  position: absolute; left: 0;
  color: var(--green);
  font-weight: bold;
  font-size: 18px;
}
```

---

## Mermaid Diagram Style

```css
.mermaid-wrap {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px;
  margin: 12px 0;
  display: flex;
  justify-content: center;
  overflow-x: auto;
}
```

Preferred Mermaid diagram types for tutorials:
- `graph TD` / `graph LR` — concept structure or decision flows
- `sequenceDiagram` — step-by-step interactions
- `stateDiagram-v2` — state transitions a learner navigates

---

## Available Layout Classes

```css
.two-col              { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 8px; }
.two-col-narrow-wide  { display: grid; grid-template-columns: 2fr 3fr; gap: 32px; margin-top: 8px; }
.two-col-wide-narrow  { display: grid; grid-template-columns: 3fr 2fr; gap: 32px; margin-top: 8px; }

.card-grid  { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; margin-top: 8px; }
.card       { background: var(--bg3); border: 1px solid var(--border); border-radius: 8px; padding: 18px; }
.card-title { font-size: 17px; font-weight: bold; color: var(--accent); margin-bottom: 6px; }

.highlight-box {
  background: var(--bg3);
  border-left: 4px solid var(--blue);
  padding: 14px 18px;
  border-radius: 0 6px 6px 0;
  margin: 14px 0;
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
  transition: color 0.2s, border-color 0.2s;
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
  background: linear-gradient(135deg, #0f0e0c 0%, #1e1a10 60%, #251f0d 100%);
  justify-content: center;
}
.slide-number {
  font-size: 13px; color: var(--muted); font-weight: bold;
  letter-spacing: 0.08em; margin-bottom: 14px;
}
h3 { font-size: 21px; font-weight: 600; color: var(--accent); margin-bottom: 8px; margin-top: 20px; }
.lead { font-size: 24px; color: var(--muted); line-height: 1.5; }
```

---

## Tables

```css
table { width: 100%; border-collapse: collapse; font-size: 17px; margin: 10px 0; }
th { background: var(--bg3); color: var(--accent); text-align: left; padding: 9px 12px; border: 1px solid var(--border); font-weight: bold; }
td { padding: 8px 12px; border: 1px solid var(--border); color: var(--text); vertical-align: top; }
tr:nth-child(even) td { background: var(--bg2); }
```
