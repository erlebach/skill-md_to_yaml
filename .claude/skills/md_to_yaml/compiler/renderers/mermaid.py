"""Mermaid diagram renderer: client-side rendering via Mermaid JS.

Embeds Mermaid source in a <pre class="mermaid"> block for browser-side rendering.
The base template includes the Mermaid JS library when diagrams are present.
"""
from __future__ import annotations

import html
import re

# Matches a Mermaid style directive that sets fill: but lacks a standalone color:.
# The negative lookbehind (?<![a-z-]) inside the lookahead excludes compound names
# like stroke-color: or fill-color: which would otherwise satisfy \bcolor:.
_FILL_WITHOUT_COLOR_RE = re.compile(
    r'(style\s+\S+\s+[^\n]*fill:[^\n,]+)(?![^\n]*(?<![a-z-])color:)'
)


def _inject_text_color(source: str) -> str:
    """Inject color:#000000 into style directives that set fill but omit color.

    Mermaid's dark theme inherits a near-white default text color, which fails
    contrast against light fills. This completes the author's intent. Authors
    should still set color: explicitly (see mermaid-best-practices.md) — this
    is the compiler safety net.
    """
    return _FILL_WITHOUT_COLOR_RE.sub(r'\1,color:#000000', source)


def render_mermaid(source: str, alt_text: str, slide_id: str, theme: str = 'dark') -> str:
    """Return a Mermaid block for client-side rendering with ADA attributes."""
    source = _inject_text_color(source)
    escaped = html.escape(source.strip())
    return (
        f'<div role="img" aria-label="{html.escape(alt_text)}">'
        f'<pre class="mermaid" aria-hidden="true">{escaped}</pre>'
        f'</div>'
    )
