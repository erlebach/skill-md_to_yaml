"""Pydantic v2 models for the YAML DSL schema.

Defines all 12 layout slide types, deck metadata, and the AnySlide discriminated union.
"""
from __future__ import annotations

from datetime import date as _date
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Base slide model
# ---------------------------------------------------------------------------

class SlideBase(BaseModel):
    """Base model shared by all slide layout types."""
    model_config = ConfigDict(extra='forbid')

    layout: str
    title: str
    notes: str | None = None
    body: str | None = Field(None, exclude=True)  # Markdown body, excluded from JSON Schema


# ---------------------------------------------------------------------------
# Layout-specific slide models (12 types)
# ---------------------------------------------------------------------------

class TitleSlide(SlideBase):
    """Deck opener: big title + optional subtitle + optional author."""
    layout: Literal['title']
    subtitle: str | None = None
    author: str | None = None


class HeroSlide(SlideBase):
    """Section opener within a deck: section title + optional description."""
    layout: Literal['hero']
    description: str | None = None


class ContentSlide(SlideBase):
    """Generic content slide: title + Markdown body."""
    layout: Literal['content']


class DividerSlide(SlideBase):
    """Visual section break: title only (rendered as full-bleed divider)."""
    layout: Literal['divider']


class FigureSlide(SlideBase):
    """Raster image slide (JPEG/PNG). alt_text is required for ADA compliance."""
    layout: Literal['figure']
    src: str
    alt_text: str


class DiagramSlide(SlideBase):
    """SVG/Mermaid diagram slide. alt_text is required for ADA compliance."""
    layout: Literal['diagram']
    alt_text: str


class ColumnContent(BaseModel):
    """Structured content for a two-column slide column."""
    model_config = ConfigDict(extra='forbid')

    type: Literal['figure', 'diagram']
    src: str | None = None       # path to image (for figure type)
    alt_text: str | None = None  # required for ADA; enforced by compiler
    source: str | None = None    # Mermaid diagram source code (for diagram type in two-column)


class TwoColumnSlide(SlideBase):
    """Two-column layout. Structured columns go in left/right; free text goes in body."""
    layout: Literal['two-column']
    left: ColumnContent | None = None
    right: ColumnContent | None = None
    proportion: Literal['50/50', '40/60', '60/40'] = '50/50'


class QuoteSlide(SlideBase):
    """Pull-quote slide: title (the quote) + optional attribution."""
    layout: Literal['quote']
    attribution: str | None = None


class ComparisonSlide(SlideBase):
    """Side-by-side comparison: title + Markdown body with <!-- split --> marker."""
    layout: Literal['comparison']


class CodeSlide(SlideBase):
    """Code block slide: title + fenced code in Markdown body. Language for syntax highlighting."""
    layout: Literal['code']
    language: str = 'text'
    line_numbers: bool = False


class StepsSlide(SlideBase):
    """Numbered steps slide: title + ordered list in Markdown body."""
    layout: Literal['steps']


class SummarySlide(SlideBase):
    """Summary/recap slide: visually distinct from content (e.g., checkmark bullets)."""
    layout: Literal['summary']


class TableSlide(SlideBase):
    """Data table with accessible markup."""
    layout: Literal['table']
    caption: str | None = None
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    row_headers: bool = False


# ---------------------------------------------------------------------------
# Discriminated union covering all 13 layout types
# ---------------------------------------------------------------------------

AnySlide = Annotated[
    Union[
        TitleSlide,
        HeroSlide,
        ContentSlide,
        DividerSlide,
        FigureSlide,
        DiagramSlide,
        TwoColumnSlide,
        QuoteSlide,
        ComparisonSlide,
        CodeSlide,
        StepsSlide,
        SummarySlide,
        TableSlide,
    ],
    Field(discriminator='layout'),
]


# ---------------------------------------------------------------------------
# Deck metadata and top-level deck container
# ---------------------------------------------------------------------------

VALID_FONTS = ('IBM Plex Sans', 'Inter', 'Fira Sans', 'Roboto', 'Source Sans 3')


class DeckMetadata(BaseModel):
    """Deck-level metadata from the first frontmatter block."""
    model_config = ConfigDict(extra='forbid')

    title: str
    author: str | None = None
    date: _date | None = Field(default_factory=_date.today)
    theme: Literal['dark', 'light'] = 'dark'
    accent_color: str | None = None
    font: str = 'IBM Plex Sans'

    @field_validator('font')
    @classmethod
    def validate_font(cls, v: str) -> str:
        if v not in VALID_FONTS:
            raise ValueError(
                f"font must be one of: {', '.join(VALID_FONTS)}. Got: {v!r}"
            )
        return v


class Deck(BaseModel):
    """Top-level deck container: metadata + ordered list of slides."""
    metadata: DeckMetadata
    slides: list[AnySlide]
