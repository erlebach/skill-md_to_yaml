"""Unit tests for rich content renderers (Phase 03 — RICH-01 through RICH-07).

All renderers are pure functions; mermaid subprocess is mocked.
"""
import base64
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Math (RICH-01)
# ---------------------------------------------------------------------------

def test_math_display():
    from compiler.renderers.math import render_math_display
    result = render_math_display(r"E=mc^2")
    assert "<math" in result
    assert 'display="block"' in result or "display='block'" in result


def test_math_inline():
    from compiler.renderers.math import render_math_inline
    result = render_math_inline(r"\alpha")
    assert "<math" in result
    assert 'display="inline"' in result or "display='inline'" in result


def test_math_extraction_before_markdown():
    """Body with both math and **bold** should yield MathML AND <strong>, no mangled delimiters."""
    from compiler.renderers.math import extract_and_render_math
    from compiler.renderers.markdown import render_markdown

    body = r"$$x^2$$ and **bold**"
    after_math = extract_and_render_math(body)
    assert "<math" in after_math

    final = render_markdown(after_math)
    assert "<strong>bold</strong>" in final
    # No raw $$ delimiters should remain
    assert "$$" not in final


def test_postprocess_emphasized_mathml_wraps_strong_math():
    """**$x$** pipeline ends with accent wrapper, not <strong><math>."""
    from compiler.renderers.math import postprocess_emphasized_mathml

    frag = '<li><strong><math display="inline"><mrow><mi>N</mi></mrow></math></strong>: def</li>'
    out = postprocess_emphasized_mathml(frag)
    assert "deck-math-emphasis" in out
    assert '<strong><math' not in out
    assert "<math" in out
    assert "role=\"presentation\"" in out


def test_postprocess_emphasized_mathml_leaves_text_strong():
    from compiler.renderers.math import postprocess_emphasized_mathml

    assert postprocess_emphasized_mathml("<strong>bold</strong>") == "<strong>bold</strong>"


def test_postprocess_emphasized_mathml_text_plus_math():
    """**text $x$** becomes one accent span around text and MathML."""
    from compiler.renderers.math import postprocess_emphasized_mathml

    frag = (
        '<p><strong>text <math display="inline"><mrow><mi>&#x003B1;</mi></mrow></math>'
        "</strong></p>"
    )
    out = postprocess_emphasized_mathml(frag)
    assert "deck-math-emphasis" in out
    assert "<strong>" not in out
    assert "text " in out
    assert "<math" in out
    assert "&#x003B1;" in out or "α" in out


def test_render_body_bold_inline_math_accent_wrapper():
    from compiler.renderers import render_body
    from schema.models import ContentSlide

    slide = ContentSlide(layout="content", title="T", body="- **$N$**: context length\n")
    html = render_body(slide)
    assert "deck-math-emphasis" in html
    assert "<strong><math" not in html


def test_render_body_bold_text_plus_inline_math_accent_wrapper():
    """**symbol $\\\\alpha$**: description — symbol and math both accent-colored."""
    from compiler.renderers import render_body
    from schema.models import ContentSlide

    slide = ContentSlide(
        layout="content",
        title="T",
        body=r"- **symbol $\alpha$**: right-hand side note\n",
    )
    html = render_body(slide)
    assert "deck-math-emphasis" in html
    assert "<strong>" not in html
    assert "symbol " in html
    assert "<math" in html


# ---------------------------------------------------------------------------
# Code highlighting (RICH-02)
# ---------------------------------------------------------------------------

def test_code_highlight():
    from compiler.renderers.code import render_code
    result = render_code('print("hi")', "python")
    assert 'class="slide-code' in result or "slide-code" in result
    assert "<span" in result


def test_code_unknown_lang():
    from compiler.renderers.code import render_code
    # Should not raise; returns a plain-text highlighted string
    result = render_code("x = 1", "nonexistent_language_xyz")
    assert isinstance(result, str)
    assert len(result) > 0


def test_code_line_numbers():
    from compiler.renderers.code import render_code
    result = render_code("x = 1\ny = 2", "python", line_numbers=True)
    # Pygments adds linenodiv or linenos class
    assert "linenodiv" in result or "linenos" in result or "ln-" in result


def test_pygments_css():
    from compiler.renderers.code import get_pygments_css
    css = get_pygments_css("dark")
    assert len(css) > 0
    assert ".slide-code" in css


# ---------------------------------------------------------------------------
# Images (RICH-03)
# ---------------------------------------------------------------------------

def test_image_path_ref():
    from compiler.renderers.image import render_image
    result = render_image("fig.png", "Alt text", embed=False)
    assert '<img src="fig.png"' in result
    assert 'alt="Alt text"' in result


def test_image_embed():
    from compiler.renderers.image import render_image
    # Minimal valid 1x1 PNG (67 bytes)
    minimal_png = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
        b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
        b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        img_path = os.path.join(tmpdir, "test.png")
        with open(img_path, "wb") as f:
            f.write(minimal_png)
        result = render_image("test.png", "Alt", embed=True, base_dir=tmpdir)
    assert "data:image/png;base64," in result


def test_image_missing_warning(capsys):
    from compiler.renderers.image import render_image
    result = render_image("nonexistent_file_xyz.png", "Alt", embed=True, base_dir="/tmp")
    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "<img src=" in result


# ---------------------------------------------------------------------------
# SVG sanitization + ADA (RICH-04)
# ---------------------------------------------------------------------------

def test_svg_sanitize():
    from compiler.renderers.svg import sanitize_svg
    raw = '<svg><script>alert(1)</script><circle r="5"/></svg>'
    result = sanitize_svg(raw)
    # bleach strips the <script> element (tag removed, text content may remain — harmless)
    assert "<script" not in result


def test_svg_sanitize_onclick():
    from compiler.renderers.svg import sanitize_svg
    raw = '<svg onclick="alert(1)"><circle/></svg>'
    result = sanitize_svg(raw)
    assert "onclick" not in result


def test_svg_embed_ada():
    from compiler.renderers.svg import wrap_svg_ada
    raw = '<svg viewBox="0 0 100 100"><circle r="5"/></svg>'
    result = wrap_svg_ada(raw, "A circle", "slide-1")
    assert 'role="img"' in result
    assert "<title" in result
    assert "<desc" in result


def test_svg_dimensions():
    from compiler.renderers.svg import wrap_svg_ada
    raw = '<svg width="800" height="600" viewBox="0 0 800 600"><rect/></svg>'
    result = wrap_svg_ada(raw, "A rect", "slide-2")
    assert 'width="100%"' in result
    assert 'height="auto"' in result
    assert "viewBox" in result


# ---------------------------------------------------------------------------
# Mermaid (RICH-06)
# ---------------------------------------------------------------------------

def test_mermaid_render():
    """Verify render_mermaid returns client-side mermaid block with ADA attrs."""
    from compiler.renderers import mermaid as mermaid_mod

    result = mermaid_mod.render_mermaid("graph TD; A-->B", "A diagram", "slide-3")

    assert 'role="img"' in result
    assert 'class="mermaid"' in result
    assert "graph TD" in result
    assert 'aria-label="A diagram"' in result


# ---------------------------------------------------------------------------
# Markdown (RICH-05)
# ---------------------------------------------------------------------------

def test_markdown_inline():
    from compiler.renderers.markdown import render_markdown
    result = render_markdown("**bold**")
    assert "<strong>bold</strong>" in result


def test_markdown_list():
    from compiler.renderers.markdown import render_markdown
    result = render_markdown("- item one\n- item two")
    assert "<ul>" in result
    assert "<li>" in result


# ---------------------------------------------------------------------------
# render_body orchestration
# ---------------------------------------------------------------------------

def test_render_body_orchestration():
    from compiler.renderers import render_body
    from schema.models import ContentSlide

    slide = ContentSlide(layout="content", title="Test", body=r"$$x^2$$ and **bold**")
    result = render_body(slide)
    assert "<math" in result
    assert "<strong>bold</strong>" in result


# ---------------------------------------------------------------------------
# Schema models (RICH-07 + RICH-02)
# ---------------------------------------------------------------------------

def test_table_model():
    from schema.models import TableSlide
    slide = TableSlide(
        layout="table",
        title="My Table",
        headers=["Col A", "Col B"],
        rows=[["1", "2"], ["3", "4"]],
    )
    assert slide.layout == "table"
    assert slide.headers == ["Col A", "Col B"]
    assert slide.caption is None
    assert slide.row_headers is False


def test_code_slide_line_numbers_field():
    from schema.models import CodeSlide
    slide = CodeSlide(layout="code", title="Code", line_numbers=True)
    assert slide.line_numbers is True


def test_table_model_in_anyslide():
    """TableSlide should be accepted by the AnySlide discriminated union."""
    from schema.models import AnySlide
    from pydantic import TypeAdapter
    adapter = TypeAdapter(AnySlide)
    slide = adapter.validate_python(
        {"layout": "table", "title": "T", "headers": ["A"], "rows": [["1"]]}
    )
    from schema.models import TableSlide
    assert isinstance(slide, TableSlide)


def test_rich_text_leading_gt_is_literal():
    """A cell like '>10K rps' is data, not a Markdown blockquote."""
    from compiler.renderers import render_rich_text
    out = render_rich_text(">10K rps")
    assert "blockquote" not in out
    assert "&gt;10K rps" in out or ">10K rps" in out


def test_rich_text_leading_hash_is_literal():
    """A cell like '#1 rank' is data, not a Markdown heading."""
    from compiler.renderers import render_rich_text
    out = render_rich_text("#1 rank")
    assert "<h1" not in out
    assert "#1 rank" in out
