"""Tests for pre-render validators (alt_text, contrast, layout variety, bullet limits)."""
import pytest

from schema.models import (
    Deck,
    DeckMetadata,
    ContentSlide,
    TwoColumnSlide,
    ColumnContent,
)
from compiler.validators import validate_deck


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _deck(slides, theme='dark', accent_color=None):
    """Build a minimal Deck with the given slides and optional metadata fields."""
    metadata = DeckMetadata(title='Test', theme=theme, accent_color=accent_color)
    return Deck(metadata=metadata, slides=slides)


def _content_slide(title='Slide', body=None):
    return ContentSlide(layout='content', title=title, body=body)


# ---------------------------------------------------------------------------
# Alt-text validation
# ---------------------------------------------------------------------------

def test_missing_alt_text_error():
    """TwoColumnSlide with figure column having no alt_text -> error."""
    slide = TwoColumnSlide(
        layout='two-column',
        title='Two Col',
        left=ColumnContent(type='figure', src='img.png', alt_text=None),
    )
    deck = _deck([slide])
    errors, warnings = validate_deck(deck)
    assert len(errors) > 0
    assert any('**ERROR**' in e and 'alt_text' in e for e in errors)


def test_valid_alt_text_no_error():
    """TwoColumnSlide with figure column having alt_text -> no error."""
    slide = TwoColumnSlide(
        layout='two-column',
        title='Two Col',
        left=ColumnContent(type='figure', src='img.png', alt_text='A circuit diagram'),
    )
    deck = _deck([slide])
    errors, _ = validate_deck(deck)
    assert errors == []


# ---------------------------------------------------------------------------
# Contrast validation
# ---------------------------------------------------------------------------

def test_invalid_contrast_error():
    """accent_color that fails WCAG on light theme -> error."""
    # #f0a500 vs #ffffff = ~2.08:1 (fails)
    deck = _deck([_content_slide()], theme='light', accent_color='#f0a500')
    errors, _ = validate_deck(deck)
    assert any('**ERROR**' in e and 'contrast' in e.lower() for e in errors)


def test_valid_contrast_no_error():
    """accent_color with sufficient contrast on light theme -> no error."""
    # #8b5e00 vs #ffffff — dark amber, passes 4.5:1
    deck = _deck([_content_slide()], theme='light', accent_color='#8b5e00')
    errors, _ = validate_deck(deck)
    contrast_errors = [e for e in errors if 'contrast' in e.lower()]
    assert contrast_errors == []


def test_no_accent_color_no_error():
    """No accent_color set -> no contrast error."""
    deck = _deck([_content_slide()], accent_color=None)
    errors, _ = validate_deck(deck)
    assert errors == []


def test_contrast_dark_theme_amber_passes():
    """#f0a500 vs dark background #0d1117 -> passes (>=4.5:1)."""
    deck = _deck([_content_slide()], theme='dark', accent_color='#f0a500')
    errors, _ = validate_deck(deck)
    contrast_errors = [e for e in errors if 'contrast' in e.lower()]
    assert contrast_errors == []


# ---------------------------------------------------------------------------
# Layout variety warnings
# ---------------------------------------------------------------------------

def test_layout_variety_warning():
    """Three consecutive content slides -> WARNING about consecutive layout."""
    slides = [_content_slide(f'Slide {i}') for i in range(3)]
    deck = _deck(slides)
    _, warnings = validate_deck(deck)
    assert any('**WARNING**' in w and 'consecutive' in w for w in warnings)


def test_no_layout_variety_warning_for_two():
    """Two consecutive same-layout slides -> no warning."""
    slides = [_content_slide('A'), _content_slide('B')]
    deck = _deck(slides)
    _, warnings = validate_deck(deck)
    consecutive_warnings = [w for w in warnings if 'consecutive' in w]
    assert consecutive_warnings == []


# ---------------------------------------------------------------------------
# Bullet limit warnings
# ---------------------------------------------------------------------------

def test_bullet_limit_warning():
    """Six bullet points in body -> WARNING."""
    body = '\n'.join(f'- Point {i}' for i in range(1, 7))  # 6 bullets
    slide = _content_slide(body=body)
    deck = _deck([slide])
    _, warnings = validate_deck(deck)
    assert any('**WARNING**' in w and 'bullet' in w for w in warnings)


def test_bullet_limit_ok_for_five():
    """Five bullet points -> no warning."""
    body = '\n'.join(f'- Point {i}' for i in range(1, 6))  # 5 bullets
    slide = _content_slide(body=body)
    deck = _deck([slide])
    _, warnings = validate_deck(deck)
    bullet_warnings = [w for w in warnings if 'bullet' in w]
    assert bullet_warnings == []
