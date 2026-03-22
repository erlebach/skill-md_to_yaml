"""Code renderer: Pygments syntax highlighting.

Generates styled HTML spans scoped under .slide-code to avoid CSS conflicts.
"""
from __future__ import annotations

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name


def _get_style(theme: str) -> str:
    return 'monokai' if theme == 'dark' else 'friendly'


def render_code(
    source: str,
    language: str,
    line_numbers: bool = False,
    theme: str = 'dark',
) -> str:
    """Return Pygments-highlighted HTML for source code.

    Args:
        source: Raw source code string.
        language: Pygments lexer alias (e.g. 'python', 'javascript').
        line_numbers: Include line number markup when True.
        theme: 'dark' -> monokai, 'light' -> friendly.
    """
    style = _get_style(theme)
    try:
        lexer = get_lexer_by_name(language, stripall=True)
    except Exception:
        lexer = TextLexer()

    formatter = HtmlFormatter(
        style=style,
        linenos=line_numbers,
        cssclass='slide-code',
    )
    return highlight(source, lexer, formatter)


def get_pygments_css(theme: str = 'dark') -> str:
    """Return Pygments CSS rules scoped to .slide-code."""
    style = _get_style(theme)
    formatter = HtmlFormatter(style=style, cssclass='slide-code')
    return formatter.get_style_defs('.slide-code')
