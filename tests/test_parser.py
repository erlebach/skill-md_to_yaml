"""Tests for the hybrid YAML+Markdown deck file parser."""
import pytest
from pydantic import ValidationError

from schema.parser import parse_deck_file
from schema.models import (
    TitleSlide, FigureSlide, DiagramSlide, ContentSlide,
    CodeSlide, QuoteSlide, TwoColumnSlide, ComparisonSlide,
    SummarySlide, DividerSlide, HeroSlide, StepsSlide,
)


# ---------------------------------------------------------------------------
# Happy-path: valid_deck.yaml (all 12 layout types)
# ---------------------------------------------------------------------------

def test_parse_valid_deck(valid_deck_path):
    deck = parse_deck_file(valid_deck_path)
    assert len(deck.slides) == 12


def test_metadata_fields(valid_deck_path):
    deck = parse_deck_file(valid_deck_path)
    assert deck.metadata.title == 'Test Deck'
    assert deck.metadata.author == 'Test Author'
    assert deck.metadata.theme == 'dark'


def test_first_slide_is_title(valid_deck_path):
    deck = parse_deck_file(valid_deck_path)
    slide = deck.slides[0]
    assert isinstance(slide, TitleSlide)
    assert slide.subtitle == 'A comprehensive example'
    assert slide.author == 'Test Author'


def test_slide_body_extraction(valid_deck_path):
    """Content slide body should contain the Markdown bullet text."""
    deck = parse_deck_file(valid_deck_path)
    content_slide = deck.slides[2]  # 3rd slide: layout: content
    assert isinstance(content_slide, ContentSlide)
    assert content_slide.body is not None
    assert 'First point' in content_slide.body


def test_figure_alt_text(valid_deck_path):
    deck = parse_deck_file(valid_deck_path)
    figure_slide = deck.slides[4]  # layout: figure
    assert isinstance(figure_slide, FigureSlide)
    assert figure_slide.alt_text == 'System architecture showing three microservices connected via message queue'


def test_code_body(valid_deck_path):
    deck = parse_deck_file(valid_deck_path)
    code_slide = deck.slides[9]  # layout: code
    assert isinstance(code_slide, CodeSlide)
    assert code_slide.body is not None
    assert 'def hello' in code_slide.body


def test_quote_body(valid_deck_path):
    deck = parse_deck_file(valid_deck_path)
    quote_slide = deck.slides[7]  # layout: quote
    assert isinstance(quote_slide, QuoteSlide)
    assert quote_slide.body is not None
    assert 'dangerous phrase' in quote_slide.body


def test_two_column_split_marker_preserved(valid_deck_path):
    """Two-column slide body with <!-- split --> should preserve the marker (splitting is compiler's job)."""
    deck = parse_deck_file(valid_deck_path)
    # Find comparison slide (also uses split), or use the two-column slide which has a body
    # The comparison slide is layout: comparison (slide index 8)
    comparison_slide = deck.slides[8]
    assert isinstance(comparison_slide, ComparisonSlide)
    assert comparison_slide.body is not None
    assert '<!-- split -->' in comparison_slide.body


def test_slide_types_in_order(valid_deck_path):
    """All 12 layout types are present in order."""
    deck = parse_deck_file(valid_deck_path)
    expected_types = [
        TitleSlide, HeroSlide, ContentSlide, DividerSlide, FigureSlide,
        DiagramSlide, TwoColumnSlide, QuoteSlide, ComparisonSlide,
        CodeSlide, StepsSlide, SummarySlide,
    ]
    assert len(deck.slides) == len(expected_types)
    for slide, expected_type in zip(deck.slides, expected_types):
        assert isinstance(slide, expected_type), (
            f"Expected {expected_type.__name__}, got {type(slide).__name__}"
        )


def test_summary_slide_notes(valid_deck_path):
    deck = parse_deck_file(valid_deck_path)
    summary_slide = deck.slides[11]
    assert isinstance(summary_slide, SummarySlide)
    assert summary_slide.notes == 'Remember to emphasize point 2'


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_invalid_missing_alt(invalid_missing_alt_path):
    with pytest.raises(ValidationError) as exc_info:
        parse_deck_file(invalid_missing_alt_path)
    error_str = str(exc_info.value)
    assert 'alt_text' in error_str


def test_invalid_unknown_field(invalid_unknown_field_path):
    with pytest.raises(ValidationError) as exc_info:
        parse_deck_file(invalid_unknown_field_path)
    error_str = str(exc_info.value)
    # body is an excluded field; having it in frontmatter triggers extra fields error
    assert 'body' in error_str or 'extra' in error_str.lower()


# ---------------------------------------------------------------------------
# Minimal metadata
# ---------------------------------------------------------------------------

def test_minimal_metadata(minimal_metadata_path):
    deck = parse_deck_file(minimal_metadata_path)
    assert deck.metadata.title == 'Minimal Deck'
    assert len(deck.slides) == 1
    assert isinstance(deck.slides[0], ContentSlide)


def test_minimal_metadata_defaults(minimal_metadata_path):
    deck = parse_deck_file(minimal_metadata_path)
    assert deck.metadata.theme == 'dark'
    assert deck.metadata.font == 'IBM Plex Sans'
    assert deck.metadata.author is None


# ---------------------------------------------------------------------------
# Two-column variants
# ---------------------------------------------------------------------------

def test_two_column_variants(two_column_path):
    deck = parse_deck_file(two_column_path)
    assert len(deck.slides) == 4
    for slide in deck.slides:
        assert isinstance(slide, TwoColumnSlide)


def test_two_column_structured_columns(two_column_path):
    """Third slide has both left and right ColumnContent."""
    deck = parse_deck_file(two_column_path)
    slide = deck.slides[2]  # Both Structured
    assert isinstance(slide, TwoColumnSlide)
    assert slide.left is not None
    assert slide.right is not None
    assert slide.left.type == 'figure'
    assert slide.right.type == 'diagram'


def test_two_column_proportion(two_column_path):
    deck = parse_deck_file(two_column_path)
    slide = deck.slides[3]  # Narrow Wide
    assert isinstance(slide, TwoColumnSlide)
    assert slide.proportion == '40/60'


def test_two_column_free_text_body(two_column_path):
    """First slide has free text in body (left column)."""
    deck = parse_deck_file(two_column_path)
    slide = deck.slides[0]
    assert slide.body is not None
    assert 'Left side is free text' in slide.body
