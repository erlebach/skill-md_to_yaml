"""Compiler engine: validate-then-render pipeline."""
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from schema.models import Deck
from compiler.validators import validate_deck
from compiler.renderers import (
    render_body,
    get_pygments_css,
    render_code,
    render_image,
    wrap_svg_ada,
    render_mermaid,
)

TEMPLATES_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
    keep_trailing_newline=True,
)


def compile_deck(deck: Deck, output_path: str, embed_images: bool = False) -> None:
    """Validate deck and render to a self-contained HTML file.

    Errors (missing alt_text, bad contrast) halt with exit code 1.
    Warnings (layout variety, bullet limits) print to stderr but produce output.
    """
    errors, warnings = validate_deck(deck)

    for w in warnings:
        print(w, file=sys.stderr)

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)

    html = _render(deck, output_path=output_path, embed_images=embed_images)
    Path(output_path).write_text(html, encoding="utf-8")


def _render(deck: Deck, output_path: str = ".", embed_images: bool = False) -> str:
    """Render deck to HTML string using Jinja2 templates."""
    template = _env.get_template("base.html.j2")

    slides_context = []
    for i, slide in enumerate(deck.slides):
        slide_id = f"slide-{i + 1}"
        rendered_body = (
            render_body(slide, embed_images=embed_images, theme=deck.metadata.theme)
            if getattr(slide, "body", None)
            else None
        )

        rendered_code = None
        rendered_image = None
        rendered_svg = None
        rendered_mermaid_html = None

        if slide.layout == "code" and getattr(slide, "body", None):
            code_body = slide.body.strip()
            # Strip markdown code fences if present
            if code_body.startswith("```"):
                lines = code_body.split("\n")
                lines = lines[1:]  # remove opening fence
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]  # remove closing fence
                code_body = "\n".join(lines)
            rendered_code = render_code(
                code_body,
                slide.language,
                slide.line_numbers,
                deck.metadata.theme,
            )
        elif slide.layout == "figure":
            base_dir = str(Path(output_path).parent) if embed_images else "."
            rendered_image = render_image(
                slide.src,
                slide.alt_text,
                embed=embed_images,
                base_dir=base_dir,
            )
        elif slide.layout == "diagram" and getattr(slide, "body", None):
            mermaid_starters = (
                "graph ",
                "sequenceDiagram",
                "classDiagram",
                "flowchart ",
                "erDiagram",
                "gantt",
                "pie ",
                "gitGraph",
                "stateDiagram",
            )
            if slide.body.strip().startswith(mermaid_starters):
                rendered_mermaid_html = render_mermaid(
                    slide.body, slide.alt_text, slide_id,
                    theme=deck.metadata.theme,
                )
            else:
                rendered_svg = wrap_svg_ada(slide.body, slide.alt_text, slide_id)

        slides_context.append(
            {
                "slide": slide,
                "slide_id": slide_id,
                "rendered_body": rendered_body,
                "rendered_code": rendered_code,
                "rendered_image": rendered_image,
                "rendered_svg": rendered_svg,
                "rendered_mermaid": rendered_mermaid_html,
            }
        )

    pygments_css = (
        get_pygments_css(deck.metadata.theme)
        if any(s.layout == "code" for s in deck.slides)
        else ""
    )

    has_mermaid = any(s["rendered_mermaid"] for s in slides_context) or any(
        getattr(getattr(s, 'left', None), 'source', None) or
        getattr(getattr(s, 'right', None), 'source', None)
        for s in deck.slides
    )
    mermaid_theme = 'dark' if deck.metadata.theme == 'dark' else 'default'

    return template.render(
        deck=deck,
        slides=slides_context,
        total=len(deck.slides),
        pygments_css=pygments_css,
        has_mermaid=has_mermaid,
        mermaid_theme=mermaid_theme,
    )
