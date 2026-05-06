# YAML to Self-Contained HTML Slide Decks

Convert structured YAML slide definitions into standalone, transportable HTML presentations. This tool is designed for faculty and content creators who want to generate **self-contained slide decks** without external dependencies.

## What You Get

- **Single HTML file** that includes all CSS, JavaScript, and embedded images
- **No internet required** to view slides after generation
- **ADA-compliant output** (WCAG 2.1/2.2 AA accessibility standards)
- **16 layout types** for content, code, tables, diagrams (Mermaid), proof, quote, comparison, and more
- **Theme customization**: dark/light themes, font selection
- **Responsive design**: works across browsers and devices

## Input: Structured YAML

Define your presentation in YAML using Markdown-like syntax:

```yaml
---
title: My Presentation
author: Your Name
theme: dark
---

---
layout: content
title: First Slide
---
- Point 1
- Point 2

---
layout: table
title: Data Table
headers: [Column A, Column B]
rows:
  - [Data 1a, Data 1b]
  - [Data 2a, Data 2b]
```

See `yaml_examples/` for complete examples with figures, diagrams, and LaTeX equations.

## Quick Start

1. **[Install Python environment](SETUP_PYTHON.md)** — uses `uv` for reproducible setup
2. **[Generate slides](USAGE.md)** — run three example commands to create HTML output
3. **Open in browser** — each `.html` file is ready to share and view offline

No build tools, databases, or external dependencies — just Python and a browser.

---

## Author

**Gordon Erlebacher**  
gerlebacher@fsu.edu  
(850) 322-0194 *(I don't answer calls from outside (850))*

---

- [Environment Setup →](SETUP_PYTHON.md)
- [Usage & Examples →](USAGE.md)
