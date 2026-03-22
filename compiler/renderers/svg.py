"""SVG renderer: sanitization and ADA-compliant wrapping.

Uses bleach for allowlist-based attribute stripping to prevent XSS via
CSS-based event handlers, onclick, and SVG <use> xlink attacks.
"""
from __future__ import annotations

import re

import bleach

ALLOWED_SVG_TAGS = [
    'svg', 'g', 'path', 'circle', 'rect', 'line', 'text', 'tspan',
    'defs', 'use', 'symbol', 'title', 'desc', 'polygon', 'polyline',
    'ellipse', 'marker', 'clipPath', 'linearGradient', 'radialGradient', 'stop',
]

ALLOWED_SVG_ATTRS = {
    '*': ['id', 'class', 'style', 'transform'],
    'svg': [
        'viewBox', 'xmlns', 'xmlns:xlink', 'width', 'height',
        'fill', 'stroke', 'stroke-width', 'font-size', 'text-anchor',
        'dominant-baseline',
    ],
    'g': ['fill', 'stroke', 'stroke-width', 'transform'],
    'path': ['d', 'fill', 'stroke', 'stroke-width'],
    'circle': ['cx', 'cy', 'r', 'fill', 'stroke', 'stroke-width'],
    'rect': ['x', 'y', 'width', 'height', 'rx', 'ry', 'fill', 'stroke', 'stroke-width'],
    'line': ['x1', 'y1', 'x2', 'y2', 'stroke', 'stroke-width'],
    'text': ['x', 'y', 'font-size', 'text-anchor', 'dominant-baseline', 'fill'],
    'tspan': ['x', 'y', 'dx', 'dy'],
    'use': ['xlink:href', 'href', 'x', 'y', 'width', 'height'],
    'symbol': ['viewBox', 'width', 'height'],
    'polygon': ['points', 'fill', 'stroke', 'stroke-width'],
    'polyline': ['points', 'fill', 'stroke', 'stroke-width'],
    'ellipse': ['cx', 'cy', 'rx', 'ry', 'fill', 'stroke', 'stroke-width'],
    'marker': ['id', 'markerWidth', 'markerHeight', 'refX', 'refY', 'orient', 'markerUnits'],
    'clipPath': ['id'],
    'linearGradient': ['id', 'x1', 'y1', 'x2', 'y2', 'gradientUnits'],
    'radialGradient': ['id', 'cx', 'cy', 'r', 'fx', 'fy', 'gradientUnits'],
    'stop': ['offset', 'stop-color', 'stop-opacity'],
    'title': [],
    'desc': [],
    'defs': [],
}


def sanitize_svg(raw_svg: str) -> str:
    """Strip dangerous tags and attributes from SVG using bleach allowlist."""
    return bleach.clean(raw_svg, tags=ALLOWED_SVG_TAGS, attributes=ALLOWED_SVG_ATTRS, strip=True)


def _normalize_svg_dimensions(svg: str) -> str:
    """Replace fixed width/height on <svg> tag with responsive values, preserve viewBox."""
    # Replace width="..." and height="..." attributes on the opening <svg tag
    svg = re.sub(r'(<svg[^>]*?)\bwidth="[^"]*"', r'\1width="100%"', svg, count=1)
    svg = re.sub(r'(<svg[^>]*?)\bheight="[^"]*"', r'\1height="auto"', svg, count=1)
    return svg


def wrap_svg_ada(svg: str, alt_text: str, slide_id: str) -> str:
    """Sanitize SVG, normalize dimensions, and inject ADA accessibility attributes.

    Adds role="img", aria-labelledby, <title>, and <desc> elements.
    """
    svg = sanitize_svg(svg)
    svg = _normalize_svg_dimensions(svg)

    title_id = f'{slide_id}-svg-title'
    desc_id = f'{slide_id}-svg-desc'

    # Inject role + aria-labelledby into the <svg> opening tag
    svg = re.sub(
        r'<svg\b',
        f'<svg role="img" aria-labelledby="{title_id} {desc_id}"',
        svg,
        count=1,
    )

    # Inject <title> and <desc> as first children of <svg>
    injection = (
        f'<title id="{title_id}">{alt_text}</title>'
        f'<desc id="{desc_id}">{alt_text}</desc>'
    )
    # Insert after the closing > of the opening <svg ...> tag
    svg = re.sub(r'(<svg[^>]*>)', r'\1' + injection, svg, count=1)

    return svg
