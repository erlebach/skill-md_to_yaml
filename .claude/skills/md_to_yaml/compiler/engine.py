"""Compiler engine: validate-then-render pipeline."""
import re
import sys
from pathlib import Path

import yaml as _yaml

from jinja2 import Environment, FileSystemLoader, select_autoescape

from schema.models import Deck
from compiler.validators import validate_deck
from compiler.renderers import (
    render_body,
    render_rich_text,
    get_pygments_css,
    render_code,
    render_image,
    wrap_svg_ada,
    render_mermaid,
)
from compiler.renderers.mermaid import _inject_text_color
from compiler.renderers.math import (
    extract_and_render_math,
    strip_math_display_inline_from_heading_html,
)

import html as _html

TEMPLATES_DIR = Path(__file__).parent / "templates"


def _render_col_html(col, base_dir: str, embed_images: bool, col_id: str, theme: str) -> str:
    """Render a TwoColumnSlide column to HTML, dispatching on src extension."""
    if col.src:
        ext = Path(col.src).suffix.lower()
        src_path = col.src if Path(col.src).is_absolute() else Path(base_dir) / col.src
        alt = col.alt_text or ""
        if ext == ".mmd":
            mermaid_source = _inject_text_color(Path(src_path).read_text(encoding="utf-8"))
            return (f'<div class="diagram-container" role="img" aria-label="{_html.escape(alt)}">'
                    f'<pre class="mermaid" aria-hidden="true">{_html.escape(mermaid_source)}</pre></div>')
        elif ext == ".svg":
            raw_svg = Path(src_path).read_text(encoding="utf-8")
            return (f'<div class="diagram-container" role="img" aria-label="{_html.escape(alt)}">'
                    f'{wrap_svg_ada(raw_svg, alt, col_id)}</div>')
        else:
            return render_image(col.src, alt, embed=embed_images, base_dir=base_dir)
    elif col.source:
        mermaid_source = _inject_text_color(col.source)
        alt = col.alt_text or ""
        return (f'<div class="diagram-container" role="img" aria-label="{_html.escape(alt)}">'
                f'<pre class="mermaid" aria-hidden="true">{_html.escape(mermaid_source)}</pre></div>')
    return ""


def _parse_figure_wide_body(body: str | None, theme: str, macros: dict[str, str] | None = None) -> dict:
    """Parse a figure-wide slide body into summary + left/right column sections.

    Returns dict with keys:
        rendered_fw_summary, rendered_fw_left_heading,
        rendered_fw_left_body, rendered_fw_right_heading, rendered_fw_right_body
    All values are HTML strings or None.
    """
    empty = {
        "rendered_fw_summary": None,
        "rendered_fw_left_heading": None,
        "rendered_fw_left_body": None,
        "rendered_fw_right_heading": None,
        "rendered_fw_right_body": None,
    }
    if not body:
        return empty

    parts = re.split(r'(?:^|\n)## ', body.lstrip())
    sections = []
    for part in parts:
        if not part.strip():
            continue
        first_newline = part.find('\n')
        if first_newline == -1:
            heading = part.strip()
            content = ''
        else:
            heading = part[:first_newline].strip()
            content = part[first_newline:].strip()
        sections.append((heading, content))

    summary_html = None
    col_sections = []
    for heading, content in sections:
        if heading.lower() == 'summary':
            if content:
                class _SummaryProxy:
                    layout = 'content'
                proxy = _SummaryProxy()
                proxy.body = content
                summary_html = render_body(proxy, embed_images=False, theme=theme, macros=macros)
        else:
            col_sections.append((heading, content))

    def _render_col(heading, content):
        heading_html = render_rich_text(heading, theme, macros=macros) if heading else None
        body_html = None
        if content:
            class _ColProxy:
                layout = 'content'
            proxy = _ColProxy()
            proxy.body = content
            body_html = render_body(proxy, embed_images=False, theme=theme, macros=macros)
        return heading_html, body_html

    left_h = left_b = right_h = right_b = None
    if len(col_sections) >= 1:
        left_h, left_b = _render_col(*col_sections[0])
    if len(col_sections) >= 2:
        right_h, right_b = _render_col(*col_sections[1])

    return {
        "rendered_fw_summary": summary_html,
        "rendered_fw_left_heading": left_h,
        "rendered_fw_left_body": left_b,
        "rendered_fw_right_heading": right_h,
        "rendered_fw_right_body": right_b,
    }


_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
    keep_trailing_newline=True,
)


def compile_deck(
    deck: Deck,
    output_path: str,
    embed_images: bool = False,
    include_skipped: bool = False,
) -> None:
    """Validate deck and render to a self-contained HTML file.

    Errors (missing alt_text, bad contrast) halt with exit code 1.
    Warnings (layout variety, bullet limits) print to stderr but produce output.

    Slides with ``skip: true`` are always validated but excluded from the
    rendered HTML unless ``include_skipped=True`` is passed.
    """
    yaml_dir = str(Path(output_path).parent)
    errors, warnings = validate_deck(deck, base_dir=yaml_dir)

    for w in warnings:
        print(w, file=sys.stderr)

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)

    macros: dict[str, str] = {}
    if deck.metadata.macros:
        macros_path = Path(yaml_dir) / deck.metadata.macros
        try:
            macros = _yaml.safe_load(macros_path.read_text(encoding="utf-8")) or {}
        except FileNotFoundError:
            print(f"WARNING: macros file not found: {macros_path}", file=sys.stderr)

    html = _render(
        deck,
        output_path=output_path,
        embed_images=embed_images,
        include_skipped=include_skipped,
        macros=macros,
    )
    Path(output_path).write_text(html, encoding="utf-8")


def _render(
    deck: Deck,
    output_path: str = ".",
    embed_images: bool = False,
    include_skipped: bool = False,
    macros: dict[str, str] | None = None,
) -> str:
    """Render deck to HTML string using Jinja2 templates."""
    template = _env.get_template("base.html.j2")

    render_slides = deck.slides if include_skipped else [
        s for s in deck.slides if not getattr(s, "skip", False)
    ]

    slides_context = []
    for i, slide in enumerate(render_slides):
        slide_id = f"slide-{i + 1}"
        fw_ctx = {
            "rendered_fw_summary": None,
            "rendered_fw_left_heading": None,
            "rendered_fw_left_body": None,
            "rendered_fw_right_heading": None,
            "rendered_fw_right_body": None,
        }
        rendered_body = (
            render_body(slide, embed_images=embed_images, theme=deck.metadata.theme, macros=macros)
            if getattr(slide, "body", None)
            else None
        )

        rendered_table_headers = None
        rendered_table_rows = None
        rendered_table_caption = None
        rendered_description = None
        if slide.layout == "table":
            thm = deck.metadata.theme
            if getattr(slide, "headers", None):
                rendered_table_headers = [
                    render_rich_text(h, thm, macros=macros) for h in slide.headers
                ]
            rendered_table_rows = [
                [
                    {
                        "html": render_rich_text(cell.text, thm, macros=macros),
                        "colspan": cell.colspan,
                    }
                    if hasattr(cell, "colspan")
                    else {"html": render_rich_text(str(cell), thm, macros=macros), "colspan": 1}
                    for cell in row
                ]
                for row in slide.rows
            ]
            if getattr(slide, "caption", None):
                rendered_table_caption = render_rich_text(slide.caption, thm, macros=macros)
        if slide.layout == "hero" and getattr(slide, "description", None):
            rendered_description = render_rich_text(
                slide.description, deck.metadata.theme, macros=macros
            )

        rendered_code = None
        rendered_image = None
        rendered_svg = None
        rendered_mermaid_html = None

        rendered_title = strip_math_display_inline_from_heading_html(
            extract_and_render_math(str(slide.title), macros=macros)
        )
        rendered_subtitle = None
        rendered_author_line = None
        if slide.layout == "title":
            if getattr(slide, "subtitle", None):
                rendered_subtitle = strip_math_display_inline_from_heading_html(
                    extract_and_render_math(str(slide.subtitle), macros=macros)
                )
            if getattr(slide, "author", None):
                rendered_author_line = strip_math_display_inline_from_heading_html(
                    extract_and_render_math(str(slide.author), macros=macros)
                )

        _math_marker = "<math"
        title_has_math = _math_marker in rendered_title or (
            rendered_subtitle is not None and _math_marker in rendered_subtitle
        ) or (
            rendered_author_line is not None and _math_marker in rendered_author_line
        )

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
            ext = Path(slide.src).suffix.lower()
            if ext == ".mmd":
                mmd_path = slide.src if Path(slide.src).is_absolute() else Path(base_dir) / slide.src
                mermaid_source = Path(mmd_path).read_text(encoding="utf-8")
                rendered_mermaid_html = render_mermaid(mermaid_source, slide.alt_text, slide_id, theme=deck.metadata.theme)
            elif ext == ".svg":
                svg_path = slide.src if Path(slide.src).is_absolute() else Path(base_dir) / slide.src
                raw_svg = Path(svg_path).read_text(encoding="utf-8")
                rendered_svg = wrap_svg_ada(raw_svg, slide.alt_text, slide_id)
            else:
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
                "xychart-beta",
                "mindmap",
                "quadrantChart",
                "timeline",
                "sankey-beta",
                "block-beta",
            )
            if slide.body.strip().startswith(mermaid_starters):
                # Split body into Mermaid source and optional caption body.
                # Mermaid header line is flush-left; subsequent lines are indented.
                # Caption (if any) follows after a blank line.
                parts = slide.body.split("\n\n", 1)
                mermaid_source = parts[0]
                caption_body = parts[1].strip() if len(parts) > 1 else ""
                rendered_mermaid_html = render_mermaid(
                    mermaid_source, slide.alt_text, slide_id,
                    theme=deck.metadata.theme,
                )
                # Always reset rendered_body — the pre-computed value contains the
                # raw Mermaid source rendered as text, which must not be shown.
                if caption_body:
                    class _BodyProxy:
                        body = caption_body
                        layout = "content"
                    rendered_body = render_body(_BodyProxy(), embed_images=embed_images, theme=deck.metadata.theme, macros=macros)
                else:
                    rendered_body = None
            else:
                rendered_svg = wrap_svg_ada(slide.body, slide.alt_text, slide_id)

        rendered_left_col = None
        rendered_right_col = None
        if slide.layout == "two-column":
            base_dir = str(Path(output_path).parent) if embed_images else "."
            if slide.left:
                rendered_left_col = _render_col_html(slide.left, base_dir, embed_images, f"{slide_id}-left", deck.metadata.theme)
            if slide.right:
                rendered_right_col = _render_col_html(slide.right, base_dir, embed_images, f"{slide_id}-right", deck.metadata.theme)

        if slide.layout == 'figure-wide':
            fw_ctx = _parse_figure_wide_body(
                getattr(slide, 'body', None), deck.metadata.theme, macros=macros
            )
            base_dir = str(Path(output_path).parent) if embed_images else "."
            ext = Path(slide.src).suffix.lower()
            if ext == ".mmd":
                mmd_path = slide.src if Path(slide.src).is_absolute() else Path(base_dir) / slide.src
                mermaid_source = Path(mmd_path).read_text(encoding="utf-8")
                rendered_mermaid_html = render_mermaid(
                    mermaid_source, slide.alt_text, slide_id, theme=deck.metadata.theme
                )
            elif ext == ".svg":
                svg_path = slide.src if Path(slide.src).is_absolute() else Path(base_dir) / slide.src
                raw_svg = Path(svg_path).read_text(encoding="utf-8")
                rendered_svg = wrap_svg_ada(raw_svg, slide.alt_text, slide_id)
            else:
                rendered_image = render_image(
                    slide.src, slide.alt_text, embed=embed_images, base_dir=base_dir
                )

        slides_context.append(
            {
                "slide": slide,
                "slide_id": slide_id,
                "rendered_title": rendered_title,
                "title_has_math": title_has_math,
                "rendered_subtitle": rendered_subtitle,
                "rendered_author_line": rendered_author_line,
                "rendered_body": rendered_body,
                "rendered_table_headers": rendered_table_headers,
                "rendered_table_rows": rendered_table_rows,
                "rendered_table_caption": rendered_table_caption,
                "rendered_description": rendered_description,
                "rendered_code": rendered_code,
                "rendered_image": rendered_image,
                "rendered_svg": rendered_svg,
                "rendered_mermaid": rendered_mermaid_html,
                "rendered_left_col": rendered_left_col,
                "rendered_right_col": rendered_right_col,
                "rendered_fw_summary": fw_ctx["rendered_fw_summary"],
                "rendered_fw_left_heading": fw_ctx["rendered_fw_left_heading"],
                "rendered_fw_left_body": fw_ctx["rendered_fw_left_body"],
                "rendered_fw_right_heading": fw_ctx["rendered_fw_right_heading"],
                "rendered_fw_right_body": fw_ctx["rendered_fw_right_body"],
            }
        )

    pygments_css = (
        get_pygments_css(deck.metadata.theme)
        if any(s.layout == "code" for s in render_slides)
        else ""
    )

    has_mermaid = any(s["rendered_mermaid"] for s in slides_context) or any(
        s["rendered_left_col"] and "mermaid" in s["rendered_left_col"] or
        s["rendered_right_col"] and "mermaid" in s["rendered_right_col"]
        for s in slides_context
    )
    mermaid_theme = 'dark' if deck.metadata.theme == 'dark' else 'default'

    return template.render(
        deck=deck,
        slides=slides_context,
        total=len(render_slides),
        pygments_css=pygments_css,
        has_mermaid=has_mermaid,
        mermaid_theme=mermaid_theme,
    )
