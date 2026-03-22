"""Mermaid diagram renderer: client-side rendering via Mermaid JS.

Embeds Mermaid source in a <pre class="mermaid"> block for browser-side rendering.
The base template includes the Mermaid JS library when diagrams are present.
"""
from __future__ import annotations

import html


def render_mermaid(source: str, alt_text: str, slide_id: str, theme: str = 'dark') -> str:
    """Return a Mermaid block for client-side rendering with ADA attributes.

    Args:
        source: Mermaid diagram source code.
        alt_text: Alt text for accessibility.
        slide_id: Unique slide identifier for HTML id attributes.
        theme: 'dark' or 'light' — stored for Mermaid JS init config.

    Returns:
        HTML string with Mermaid source for client-side rendering.
    """
    escaped = html.escape(source.strip())
    return (
        f'<div role="img" aria-label="{html.escape(alt_text)}">'
        f'<pre class="mermaid" aria-hidden="true">{escaped}</pre>'
        f'</div>'
    )
