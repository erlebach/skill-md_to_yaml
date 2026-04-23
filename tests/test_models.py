"""Tests for all Pydantic v2 slide models and deck metadata."""
from __future__ import annotations

import pytest
from datetime import date
from pydantic import ValidationError

from schema.models import (
    TitleSlide, HeroSlide, ContentSlide, DividerSlide,
    FigureSlide, DiagramSlide, TwoColumnSlide, QuoteSlide,
    ComparisonSlide, CodeSlide, StepsSlide, SummarySlide,
    ColumnContent, AnySlide, DeckMetadata, Deck, VALID_FONTS,
)
from pydantic import TypeAdapter

AnySlideAdapter = TypeAdapter(AnySlide)


# ---------------------------------------------------------------------------
# Basic layout validation — happy path
# ---------------------------------------------------------------------------

def test_title_slide_validates():
    slide = TitleSlide(layout='title', title='Hello', subtitle='World')
    assert slide.title == 'Hello'
    assert slide.subtitle == 'World'


def test_title_slide_optional_author():
    slide = TitleSlide(layout='title', title='Hello', author='Me')
    assert slide.author == 'Me'


def test_hero_slide_validates():
    slide = HeroSlide(layout='hero', title='Section')
    assert slide.title == 'Section'


def test_hero_slide_optional_description():
    slide = HeroSlide(layout='hero', title='Section', description='Short desc')
    assert slide.description == 'Short desc'


def test_content_slide_validates():
    slide = ContentSlide(layout='content', title='Body')
    assert slide.layout == 'content'


def test_divider_slide_validates():
    slide = DividerSlide(layout='divider', title='Break')
    assert slide.layout == 'divider'


def test_figure_slide_validates():
    slide = FigureSlide(layout='figure', title='Img', src='x.png', alt_text='desc')
    assert slide.src == 'x.png'
    assert slide.alt_text == 'desc'


def test_figure_slide_missing_alt_text_raises():
    with pytest.raises(ValidationError) as exc_info:
        FigureSlide(layout='figure', title='Img', src='x.png')
    assert 'alt_text' in str(exc_info.value)


def test_figure_slide_missing_src_raises():
    with pytest.raises(ValidationError):
        FigureSlide(layout='figure', title='Img', alt_text='desc')


def test_diagram_slide_validates():
    slide = DiagramSlide(layout='diagram', title='D', alt_text='desc')
    assert slide.alt_text == 'desc'


def test_diagram_slide_missing_alt_text_raises():
    with pytest.raises(ValidationError) as exc_info:
        DiagramSlide(layout='diagram', title='D')
    assert 'alt_text' in str(exc_info.value)


def test_two_column_slide_with_figure_left():
    left = ColumnContent(type='figure', src='x.png', alt_text='d')
    slide = TwoColumnSlide(layout='two-column', title='TC', left=left)
    assert slide.left.type == 'figure'


def test_two_column_slide_no_columns():
    slide = TwoColumnSlide(layout='two-column', title='TC')
    assert slide.left is None
    assert slide.right is None


def test_two_column_slide_proportion_default():
    slide = TwoColumnSlide(layout='two-column', title='TC')
    assert slide.proportion == '50/50'


@pytest.mark.parametrize('proportion', ['50/50', '40/60', '60/40'])
def test_two_column_slide_proportion_values(proportion):
    slide = TwoColumnSlide(layout='two-column', title='TC', proportion=proportion)
    assert slide.proportion == proportion


def test_two_column_slide_invalid_proportion_raises():
    with pytest.raises(ValidationError):
        TwoColumnSlide(layout='two-column', title='TC', proportion='30/70')


def test_quote_slide_validates():
    slide = QuoteSlide(layout='quote', title='Q', attribution='Author')
    assert slide.attribution == 'Author'


def test_comparison_slide_validates():
    slide = ComparisonSlide(layout='comparison', title='C')
    assert slide.layout == 'comparison'


def test_code_slide_validates():
    slide = CodeSlide(layout='code', title='Ex', language='python')
    assert slide.language == 'python'


def test_code_slide_language_defaults_to_text():
    slide = CodeSlide(layout='code', title='Ex')
    assert slide.language == 'text'


def test_steps_slide_validates():
    slide = StepsSlide(layout='steps', title='Steps')
    assert slide.layout == 'steps'


def test_summary_slide_validates():
    slide = SummarySlide(layout='summary', title='Sum')
    assert slide.layout == 'summary'


# ---------------------------------------------------------------------------
# Optional notes field on all slides
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('slide_cls,kwargs', [
    (TitleSlide, {'layout': 'title', 'title': 'T'}),
    (HeroSlide, {'layout': 'hero', 'title': 'T'}),
    (ContentSlide, {'layout': 'content', 'title': 'T'}),
    (DividerSlide, {'layout': 'divider', 'title': 'T'}),
    (FigureSlide, {'layout': 'figure', 'title': 'T', 'src': 'x.png', 'alt_text': 'd'}),
    (DiagramSlide, {'layout': 'diagram', 'title': 'T', 'alt_text': 'd'}),
    (TwoColumnSlide, {'layout': 'two-column', 'title': 'T'}),
    (QuoteSlide, {'layout': 'quote', 'title': 'T'}),
    (ComparisonSlide, {'layout': 'comparison', 'title': 'T'}),
    (CodeSlide, {'layout': 'code', 'title': 'T'}),
    (StepsSlide, {'layout': 'steps', 'title': 'T'}),
    (SummarySlide, {'layout': 'summary', 'title': 'T'}),
])
def test_all_slides_accept_optional_notes(slide_cls, kwargs):
    slide = slide_cls(**kwargs, notes='Speaker note')
    assert slide.notes == 'Speaker note'


# ---------------------------------------------------------------------------
# extra='forbid' — unknown fields raise ValidationError
# ---------------------------------------------------------------------------

def test_content_slide_rejects_unknown_field():
    with pytest.raises(ValidationError):
        ContentSlide(layout='content', title='T', unknown_field='x')


def test_figure_slide_rejects_unknown_field():
    with pytest.raises(ValidationError):
        FigureSlide(layout='figure', title='T', src='x.png', alt_text='d', bogus='y')


# ---------------------------------------------------------------------------
# DeckMetadata
# ---------------------------------------------------------------------------

def test_deck_metadata_minimal_validates():
    meta = DeckMetadata(title='My Deck')
    assert meta.title == 'My Deck'
    assert meta.theme == 'dark'
    assert meta.font == 'IBM Plex Sans'
    assert meta.date == date.today()


def test_deck_metadata_invalid_theme_raises():
    with pytest.raises(ValidationError):
        DeckMetadata(title='D', theme='invalid')


def test_deck_metadata_invalid_font_raises():
    with pytest.raises(ValidationError):
        DeckMetadata(title='D', font='Comic Sans')


def test_deck_metadata_full_validates():
    meta = DeckMetadata(title='D', author='Me', theme='light', accent_color='#ff0000')
    assert meta.author == 'Me'
    assert meta.theme == 'light'
    assert meta.accent_color == '#ff0000'


@pytest.mark.parametrize('font', VALID_FONTS)
def test_deck_metadata_valid_fonts(font):
    meta = DeckMetadata(title='D', font=font)
    assert meta.font == font


def test_deck_metadata_rejects_unknown_field():
    with pytest.raises(ValidationError):
        DeckMetadata(title='D', bogus='x')


def test_deck_metadata_math_display_color_accepts_named_and_hex():
    meta = DeckMetadata(title='D', math_display_color='cyan')
    assert meta.math_display_color == 'cyan'
    meta2 = DeckMetadata(title='D', math_display_color='#0af')
    assert meta2.math_display_color == '#0af'


def test_deck_metadata_math_display_color_rejects_injection():
    with pytest.raises(ValidationError):
        DeckMetadata(title='D', math_display_color='red; x:1')


def test_content_slide_inherits_math_display_color_override():
    slide = ContentSlide(
        layout='content',
        title='T',
        math_display_color='hsl(180, 80%, 60%)',
    )
    assert slide.math_display_color == 'hsl(180, 80%, 60%)'


def test_slide_optional_title_and_content_scale():
    """Per-slide title_scale / content_scale override deck when set."""
    slide = ContentSlide(
        layout='content',
        title='T',
        title_scale=1.5,
        content_scale=1.25,
    )
    assert slide.title_scale == 1.5
    assert slide.content_scale == 1.25
    slide2 = ContentSlide(layout='content', title='T')
    assert slide2.title_scale is None
    assert slide2.content_scale is None


def test_figure_slide_optional_figure_scale():
    fig = FigureSlide(
        layout='figure',
        title='F',
        src='a.png',
        alt_text='x',
        figure_scale=0.8,
    )
    assert fig.figure_scale == 0.8


def test_deck_metadata_figure_scale_default():
    meta = DeckMetadata(title='D')
    assert meta.figure_scale == 1.0


def test_deck_metadata_figure_layout_debug_default():
    meta = DeckMetadata(title='D')
    assert meta.figure_layout_debug is False


# ---------------------------------------------------------------------------
# AnySlide discriminated union
# ---------------------------------------------------------------------------

def test_any_slide_routes_to_figure():
    data = {'layout': 'figure', 'title': 'T', 'src': 'x.png', 'alt_text': 'a'}
    slide = AnySlideAdapter.validate_python(data)
    assert isinstance(slide, FigureSlide)


def test_any_slide_routes_to_title():
    data = {'layout': 'title', 'title': 'Hello'}
    slide = AnySlideAdapter.validate_python(data)
    assert isinstance(slide, TitleSlide)


def test_any_slide_unknown_layout_raises():
    with pytest.raises(ValidationError):
        AnySlideAdapter.validate_python({'layout': 'unknown-layout', 'title': 'T'})


# ---------------------------------------------------------------------------
# Deck container
# ---------------------------------------------------------------------------

def test_deck_validates_with_mixed_slides():
    meta = DeckMetadata(title='My Deck')
    slides_data = [
        {'layout': 'title', 'title': 'Hello'},
        {'layout': 'content', 'title': 'Body'},
        {'layout': 'figure', 'title': 'Fig', 'src': 'x.png', 'alt_text': 'alt'},
    ]
    slides = [AnySlideAdapter.validate_python(d) for d in slides_data]
    deck = Deck(metadata=meta, slides=slides)
    assert len(deck.slides) == 3


def test_deck_metadata_date_uses_factory():
    """Ensure date defaults to today (not a static value set at import time)."""
    meta = DeckMetadata(title='D')
    assert meta.date == date.today()
