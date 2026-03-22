"""Markdown renderer: inline Markdown to HTML using Python-Markdown."""
from __future__ import annotations

import markdown


def render_markdown(text: str) -> str:
    """Convert Markdown text to HTML.

    Uses extensions: tables, fenced_code, attr_list, md_in_html.
    """
    return markdown.markdown(
        text,
        extensions=['tables', 'fenced_code', 'attr_list', 'md_in_html'],
    )
