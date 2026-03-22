"""Mermaid diagram renderer: mmdc subprocess to SVG with ADA attributes.

Requires Node.js and @mermaid-js/mermaid-cli installed globally:
    npm install -g @mermaid-js/mermaid-cli
"""
from __future__ import annotations

import os
import subprocess
import tempfile

from compiler.renderers.svg import wrap_svg_ada


def render_mermaid(source: str, alt_text: str, slide_id: str) -> str:
    """Compile Mermaid source to inline SVG via mmdc subprocess.

    Args:
        source: Mermaid diagram source code.
        alt_text: Alt text for ADA <title>/<desc> elements.
        slide_id: Unique slide identifier for HTML id attributes.

    Returns:
        ADA-wrapped inline SVG string.

    Raises:
        RuntimeError: When mmdc is not installed/found on PATH.
    """
    with tempfile.NamedTemporaryFile(suffix='.mmd', mode='w', delete=False) as mmd_file:
        mmd_file.write(source)
        mmd_path = mmd_file.name

    svg_path = mmd_path + '.svg'

    try:
        try:
            subprocess.run(
                ['mmdc', '-i', mmd_path, '-o', svg_path],
                check=True,
                capture_output=True,
            )
        except FileNotFoundError:
            raise RuntimeError(
                "mmdc not found - install with: npm install -g @mermaid-js/mermaid-cli"
            )

        with open(svg_path, 'r', encoding='utf-8') as fh:
            svg_content = fh.read()
    finally:
        os.unlink(mmd_path)
        if os.path.exists(svg_path):
            os.unlink(svg_path)

    return wrap_svg_ada(svg_content, alt_text, slide_id)
