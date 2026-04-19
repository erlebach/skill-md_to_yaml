"""Pre-render validation for ADA compliance and slide design guidelines.

Runs before compilation to catch errors and emit warnings early ("fail fast").
"""
from __future__ import annotations

import re
from pathlib import Path

from schema.models import Deck, DeckMetadata
from compiler.contrast import contrast_ratio

THEME_BACKGROUNDS = {'dark': '#0d1117', 'light': '#ffffff'}


def _check_alt_text(slides: list) -> list[str]:
    """Check that all figure/diagram slides (and columns) have non-empty alt_text."""
    errors: list[str] = []
    for i, slide in enumerate(slides, start=1):
        layout = slide.layout
        if layout in ('figure', 'diagram'):
            if not (hasattr(slide, 'alt_text') and slide.alt_text):
                errors.append(
                    f"**ERROR** slide {i}: missing alt_text on {layout} slide"
                )
        elif layout == 'two-column':
            for side_name in ('left', 'right'):
                col = getattr(slide, side_name, None)
                if col is None:
                    continue
                if col.type in ('figure', 'diagram') and not col.alt_text:
                    errors.append(
                        f"**ERROR** slide {i}: missing alt_text on {layout} "
                        f"{side_name} column ({col.type})"
                    )
    return errors


def _check_contrast(metadata: DeckMetadata) -> list[str]:
    """Validate accent_color contrast ratio against the theme background."""
    if metadata.accent_color is None:
        return []
    color = metadata.accent_color
    bg = THEME_BACKGROUNDS[metadata.theme]
    ratio = contrast_ratio(color, bg)
    if ratio < 4.5:
        return [
            f"**ERROR** accent_color {color} fails WCAG 2.1 AA contrast "
            f"({ratio:.2f}:1) against {metadata.theme} background {bg}"
        ]
    return []


def _check_layout_variety(slides: list) -> list[str]:
    """Warn when 3+ consecutive slides share the same layout."""
    warnings: list[str] = []
    if not slides:
        return warnings

    run_layout = slides[0].layout
    run_start = 1
    run_len = 1

    def _maybe_warn(layout: str, start: int, length: int) -> None:
        if length >= 3:
            end = start + length - 1
            warnings.append(
                f"**WARNING** slides {start}-{end}: "
                f"3+ consecutive '{layout}' layout slides"
            )

    for i, slide in enumerate(slides[1:], start=2):
        if slide.layout == run_layout:
            run_len += 1
        else:
            _maybe_warn(run_layout, run_start, run_len)
            run_layout = slide.layout
            run_start = i
            run_len = 1

    _maybe_warn(run_layout, run_start, run_len)
    return warnings


def _check_bullet_limits(slides: list) -> list[str]:
    """Warn when a slide body contains more than 8 bullet points."""
    warnings: list[str] = []
    for i, slide in enumerate(slides, start=1):
        body = getattr(slide, 'body', None)
        if not body:
            continue
        bullets = re.findall(r'^[-*+] |^\d+\. ', body, re.MULTILINE)
        n = len(bullets)
        if n > 8:
            warnings.append(
                f"**WARNING** slide {i}: {n} bullet points exceeds "
                f"recommended maximum of 8"
            )
    return warnings


def _check_image_paths(slides: list, base_dir: str = '.') -> list[str]:
    """Warn when a figure slide references a non-existent image file."""
    warnings: list[str] = []
    for i, slide in enumerate(slides, start=1):
        if slide.layout == 'figure':
            src = getattr(slide, 'src', None)
            if src:
                resolved = Path(src) if Path(src).is_absolute() else Path(base_dir) / src
                if not resolved.exists():
                    warnings.append(
                        f"WARNING: Image file not found: {src} (slide {i})"
                    )
    return warnings


def validate_deck(deck: Deck, base_dir: str = '.') -> tuple[list[str], list[str]]:
    """Run all pre-render validators and return (errors, warnings).

    Errors cause exit code 1; warnings are informational (stderr).
    ``base_dir`` is used to resolve relative image src paths.
    """
    slides = deck.slides
    errors = _check_alt_text(slides) + _check_contrast(deck.metadata)
    warnings = (
        _check_layout_variety(slides)
        + _check_bullet_limits(slides)
        + _check_image_paths(slides, base_dir=base_dir)
    )
    return errors, warnings
