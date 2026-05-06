## Before you run

1. Follow [SETUP_PYTHON.md](SETUP_PYTHON.md) to install `uv` and activate the Python environment.
2. You should be in the `standalone/` directory (where this file is).

## Run the examples

To generate an html file from a yaml input file, run the three examples below: 

```bash
./scripts/compile_to_html.sh yaml_examples/example_2158/example_2158.yaml 2158.html --embed-images

./scripts/compile_to_html.sh yaml_examples/mycontent/mycontent.yaml mycontent.html --embed-images

./scripts/compile_to_html.sh yaml_examples/quantum_seminar/quantum_seminar.yaml quantum_seminar.html --embed-images
```

The paths are relative to the current folder. 

## Figures

Figures are referenced in your YAML file as paths relative to the YAML file location. Use `--embed-figures` to create a self-contained HTML file that includes all CSS, JavaScript, and images—this makes the file fully transportable and viewable offline.

### Figure Scaling

Control figure size in the frontmatter (the `---` section at the top of your YAML file) using the `figure_scale` attribute:

```yaml
---
title: My Presentation
figure_scale: 0.8
---
```

This scales all figures proportionally. Default figures are embedded at their specified dimensions in the slide template.

## Available Slide Layouts

Your YAML file uses the `layout:` attribute to define slide type. 16 layouts are available:

- **content** — bulleted lists and paragraphs
- **code** — syntax-highlighted code blocks
- **table** — data tables with headers and rows
- **diagram** — Mermaid diagrams (flowcharts, etc.)
- **figure** — image with caption
- **figure-wide** — full-width image
- **proof** — formal mathematical proofs
- **quote** — highlighted quotes
- **comparison** — side-by-side comparison
- **steps** — numbered step-by-step procedures
- **summary** — key takeaways
- **divider** — section breaks
- **hero** — title slide
- **title** — slide heading
- **transcribe** — transcript or dialogue
- **Two-column** — left/right column layout

See `yaml_examples/` for working examples of each layout type.

## Folder structure

Execute: `tree -d .` on mac/linux: 
```
.
├── scripts
├── skills
│   └── md_to_yaml
│       ├── compiler
│       │   ├── __pycache__
│       │   ├── renderers
│       │   │   └── __pycache__
│       │   └── templates
│       │       └── md
│       └── schema
│           └── __pycache__
└── yaml_examples
    ├── example_2158
    │   └── figures
    ├── mycontent
    └── quantum_seminar
        └── figures
```
