"""Math renderer: LaTeX to MathML conversion using latex2mathml.

Handles both inline ($...$) and display ($$...$$) math.
Math extraction must run BEFORE Markdown rendering to prevent delimiter mangling.
"""
from __future__ import annotations

import re

import latex2mathml.converter


def render_math_inline(tex: str) -> str:
    """Convert inline LaTeX expression to MathML with display='inline'."""
    return latex2mathml.converter.convert(tex, display="inline")


def render_math_display(tex: str) -> str:
    """Convert display LaTeX expression to MathML with display='block'."""
    return latex2mathml.converter.convert(tex, display="block")


def extract_and_render_math(text: str) -> str:
    """Replace $$...$$ and $...$ spans with rendered MathML.

    Processes display math ($$...$$) first to avoid matching $$ as two $'s.
    """
    # Display math: $$...$$ (may span multiple lines, non-greedy)
    def replace_display(match: re.Match) -> str:
        tex = match.group(1)
        try:
            return render_math_display(tex)
        except Exception:
            return match.group(0)

    text = re.sub(r'\$\$(.*?)\$\$', replace_display, text, flags=re.DOTALL)

    # Inline math: $...$ (non-greedy, single line)
    def replace_inline(match: re.Match) -> str:
        tex = match.group(1)
        try:
            return render_math_inline(tex)
        except Exception:
            return match.group(0)

    text = re.sub(r'\$(.+?)\$', replace_inline, text)

    return text
