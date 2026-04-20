# Flavor: Explanatory

Use this flavor for conceptual overviews, paper summaries, survey presentations, and any deck where the goal is building understanding rather than showing code.

---

## Theme

Dark. Use the GitHub-dark palette from `accessibility-core.md`.

```css
:root {
  --bg:        #0d1117;
  --bg2:       #161b22;
  --bg3:       #21262d;
  --text:      #e6edf3;
  --muted:     #8b949e;
  --accent:    #58a6ff;
  --green:     #3fb950;
  --orange:    #f0883e;
  --border:    #30363d;
  --sidebar-w: 220px;
  --dots-h:    48px;
}

body {
  font-family: "IBM Plex Sans", Arial, Helvetica, sans-serif;
  background: var(--bg);
  color: var(--text);
}
```

Google Fonts import for IBM Plex Sans:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap" rel="stylesheet">
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
    primaryBorderColor: '#30363d',
    lineColor: '#8b949e',
    secondaryColor: '#161b22',
    tertiaryColor: '#0d1117',
    fontFamily: '"IBM Plex Sans", Arial, Helvetica, sans-serif',
    fontSize: '14px'
  }
});
```

---

## Layout Principles

**Mix layouts freely** across slides to create visual variety. Match the layout to the content:

| Content type | Recommended layout |
|-------------|-------------------|
| Concept taxonomy / flow | Mermaid diagram left + bullets right |
| Process / lifecycle | Mermaid diagram full-width or left, narrative right |
| Comparison | Table or two-column cards |
| Key insight | Full-width highlight box with supporting bullets |
| Challenge catalogue | Challenge card grid |
| Real figure from source | Figure left + explanation right |

**Mermaid diagrams are preferred over figures** when a concept can be expressed structurally (hierarchy, flow, sequence, timeline). Include a real figure only when it adds genuine value that a diagram cannot replicate — e.g., a chart showing exponential growth, or a multi-panel comparison from a paper.

---

## Mermaid Diagram Style

Wrap every diagram in `.mermaid-wrap`:

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
.mermaid { font-size: 14px; }
```

Apply color to Mermaid nodes using the dark palette:
```
style NodeName fill:#58a6ff,stroke:#58a6ff,color:#0d1117
style NodeName fill:#3fb950,stroke:#3fb950,color:#0d1117
style NodeName fill:#f0883e,stroke:#f0883e,color:#0d1117
```

Every Mermaid diagram must be accompanied by a caption — use `<figcaption>` inside a wrapping `<figure>`, or a `<p>` directly below `.mermaid-wrap`.

---

## Side-by-Side Layout (Mermaid + Bullets)

This is the signature layout of the explanatory flavor. Use it on slides where a diagram communicates structure and bullets provide commentary.

```html
<div class="two-col">
  <div>
    <div class="mermaid-wrap">
      <div class="mermaid">
        graph TD
          A --> B
      </div>
    </div>
    <p style="font-size:15px; color:var(--muted); font-style:italic;">
      Caption describing what the diagram shows.
    </p>
  </div>
  <div>
    <h3>Key Points</h3>
    <ul>
      <li>...</li>
    </ul>
  </div>
</div>
```

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
  border-left: 4px solid var(--accent);
  padding: 14px 18px;
  border-radius: 0 6px 6px 0;
  margin: 14px 0;
}

.challenge-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 14px; margin-top: 8px; }
.challenge-item {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-top: 3px solid var(--orange);
  border-radius: 6px;
  padding: 14px;
}
.challenge-item h3 { margin-top: 0; color: var(--orange); font-size: 17px; }

.tag-row { display: flex; flex-wrap: wrap; gap: 10px; margin: 12px 0; }
.tag {
  display: inline-block;
  background: var(--bg3);
  border: 1px solid var(--border);
  color: var(--accent);
  font-size: 15px;
  padding: 4px 12px;
  border-radius: 20px;
}
```

---

## Navigation Chrome

> **CRITICAL**: Use the SlideEngine JS from `visual-explainer/references/slide-patterns.md` — NOT anchor-link (`location.href='#sN'`) navigation. The SlideEngine manages active states on dots and sidebar links automatically. Do NOT write `onclick="location.href='#sN'"` on dots or sidebar links. Do NOT use `<div id="main">` as the slide container — use `<div class="deck">` with scroll-snap.

CSS for sidebar and dots appearance (styles only — behavior comes from SlideEngine):

```css
/* Sidebar */
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

/* Dots */
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
  transition: background 0.15s, border-color 0.15s, color 0.15s;
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

/* Responsive */
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
  position: relative;
  display: flex;
  flex-direction: column;
}
.slide-hero {
  background: linear-gradient(135deg, #0d1117 0%, #1a2332 60%, #0d2137 100%);
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
