"""Rich content renderers package.

Exports render_body() orchestrator and individual renderer functions.
Math extraction runs before Markdown to prevent delimiter mangling (Pitfall 1).
"""
from __future__ import annotations

from compiler.renderers.code import get_pygments_css, render_code
from compiler.renderers.image import render_image
from compiler.renderers.markdown import render_markdown
from compiler.renderers.math import extract_and_render_math
from compiler.renderers.mermaid import render_mermaid
from compiler.renderers.svg import sanitize_svg, wrap_svg_ada

__all__ = [
    'render_body',
    'render_code',
    'get_pygments_css',
    'render_image',
    'render_markdown',
    'extract_and_render_math',
    'render_mermaid',
    'sanitize_svg',
    'wrap_svg_ada',
]


def render_body(slide, embed_images: bool = False, theme: str = 'dark') -> str:
    """Orchestrate body rendering for a slide.

    Processing order:
      1. Math extraction ($$...$$ and $...$) -> MathML
      2. Markdown rendering -> HTML

    Args:
        slide: Any slide model instance with an optional ``body`` field.
        embed_images: When True, embed image files as base64 data URIs.
        theme: 'dark' or 'light' — controls code highlighting theme.

    Returns:
        Rendered HTML string, or empty string if slide has no body.
    """
    body = getattr(slide, 'body', None)
    if not body:
        return ''

    # Step 1: Extract and render math before Markdown processes $ delimiters
    body = extract_and_render_math(body)

    # Step 2: Render remaining Markdown to HTML
    body = render_markdown(body)

    return body
