"""Math renderer: LaTeX to MathML conversion using latex2mathml.

Handles both inline ($...$) and display ($$...$$) math.
Math extraction must run BEFORE Markdown rendering to prevent delimiter mangling.
"""
from __future__ import annotations

import re

import latex2mathml.converter

# latex2mathml emits xmlns on every <math>; in text/html the namespace is implicit.
_MATHML_XMLNS_ATTR = re.compile(
    r'\s+xmlns="http://www\.w3\.org/1998/Math/MathML"',
)


def strip_mathml_xmlns(mathml_fragment: str) -> str:
    """Remove redundant MathML xmlns from a converter fragment.

    In HTML5, ``<math>`` is in the MathML namespace without an xmlns attribute.
    The deck template records the URI once in ``<head>`` for clarity.

    Args:
        mathml_fragment: Raw string from latex2mathml (one root ``<math>``…).

    Returns:
        Same fragment without ``xmlns="http://www.w3.org/1998/Math/MathML"``.

    """
    return _MATHML_XMLNS_ATTR.sub("", mathml_fragment)


# Opening <math display="inline"> in slide headings; some UAs/layout break on this.
_MATH_OPEN_DISPLAY_INLINE_GT = re.compile(
    r'<math\s+display\s*=\s*["\']inline\s*["\']\s*>',
    flags=re.IGNORECASE,
)
# Rare: other attributes after display="inline" before >
_MATH_OPEN_DISPLAY_INLINE_ATTR = re.compile(
    r'<math\s+display\s*=\s*["\']inline\s*["\']\s+',
    flags=re.IGNORECASE,
)


def strip_math_display_inline_from_heading_html(html: str) -> str:
    """Drop ``display="inline"`` from ``<math>`` in heading HTML only.

    latex2mathml always sets ``display="inline"`` on ``$...$`` output; for
    ``<h1>``/``<h2>``/``<h3>`` titles, omitting the attribute avoids bad line
    breaking in some browsers while keeping body math unchanged.

    Args:
        html: Rendered title, subtitle, or author line (may contain ``<math>``).

    Returns:
        Same string with ``display="inline"`` (or ``'inline'``) removed from
        each opening ``<math>`` tag.

    """
    if not html or "<math" not in html:
        return html
    out = _MATH_OPEN_DISPLAY_INLINE_ATTR.sub("<math ", html)
    out = _MATH_OPEN_DISPLAY_INLINE_GT.sub("<math>", out)
    return out


def render_math_inline(tex: str) -> str:
    """Convert inline LaTeX expression to MathML with display='inline'."""
    return strip_mathml_xmlns(
        latex2mathml.converter.convert(tex, display="inline")
    )


def render_math_display(tex: str) -> str:
    """Convert display LaTeX expression to MathML with display='block'."""
    return strip_mathml_xmlns(
        latex2mathml.converter.convert(tex, display="block")
    )


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
