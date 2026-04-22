"""Pydantic v2 models for the YAML DSL schema.

Defines all layout slide types, deck metadata, and the AnySlide discriminated union.
"""
from __future__ import annotations

from datetime import date as _date
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Guardrail: reject obvious injection in CSS `color` values for display math
def _check_math_display_color(v: str | None) -> str | None:
    """Normalize and validate an optional ``math_display_color`` string."""
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    if len(s) > 120:
        raise ValueError("math_display_color: max 120 characters")
    if ";" in s or "{" in s or "}" in s or "<" in s or "url(" in s.lower() or chr(92) in s:
        raise ValueError(
            "math_display_color: use a short CSS color (e.g. cyan, #0af, rgb(0, 200, 200));"
            " semicolons, angle brackets, backslashes, and url() are not allowed."
        )
    return s

# ---------------------------------------------------------------------------
# Base slide model
# ---------------------------------------------------------------------------

class SlideBase(BaseModel):
    """Base model shared by all slide layout types."""
    model_config = ConfigDict(extra='forbid')

    layout: str
    title: str
    subtitle: str | None = None
    notes: str | None = None
    skip: bool = False  # If True, slide is validated but excluded from compiled HTML
    math_display_scale: float | None = Field(
        default=None,
        ge=0.75,
        le=2.0,
        description='Override deck math_display_scale for this slide (None = inherit).',
    )
    math_display_center: bool | None = Field(
        default=None,
        description='Override deck math_display_center for this slide (None = inherit).',
    )
    math_display_color: str | None = Field(
        default=None,
        description='Override deck math_display_color for this slide (None = inherit).',
    )
    body: str | None = Field(None, exclude=True)  # Markdown body, excluded from JSON Schema

    @field_validator('math_display_color')
    @classmethod
    def _v_slide_math_color(cls, v: str | None) -> str | None:
        return _check_math_display_color(v)


# ---------------------------------------------------------------------------
# Layout-specific slide models
# ---------------------------------------------------------------------------

class TitleSlide(SlideBase):
    """Deck opener: big title + optional subtitle + optional author."""
    layout: Literal['title']
    author: str | None = None


class HeroSlide(SlideBase):
    """Section opener within a deck: section title + optional description."""
    layout: Literal['hero']
    description: str | None = None


class ContentSlide(SlideBase):
    """Presentation content slide: title + Markdown body (md_to_yaml default)."""
    layout: Literal['content']


class TranscribeSlide(SlideBase):
    """Dense transcription slide: same body pipeline as content; transcribe CSS in HTML."""

    layout: Literal['transcribe']


class DividerSlide(SlideBase):
    """Visual section break: title only (rendered as full-bleed divider)."""
    layout: Literal['divider']


class FigureSlide(SlideBase):
    """Image/diagram slide. Extension determines rendering: .jpg/.png/.gif/.webp → <img>, .svg → inline SVG, .mmd → Mermaid. alt_text required."""
    layout: Literal['figure']
    src: str
    alt_text: str


class FigureWideSlide(SlideBase):
    """Wide-figure layout: full-width figure + two text columns below.

    Front matter holds figure metadata only (src, alt_text, caption, proportion).
    Body Markdown is parsed by the engine into summary, left-column, and
    right-column sections delimited by level-2 headings.
    """
    layout: Literal['figure-wide']
    src: str
    alt_text: str
    caption: str | None = None
    proportion: Literal['50/50', '40/60', '60/40'] = '50/50'


class DiagramSlide(SlideBase):
    """SVG/Mermaid diagram slide. alt_text is required for ADA compliance."""
    layout: Literal['diagram']
    alt_text: str


class ColumnContent(BaseModel):
    """Structured content for a two-column slide column."""
    model_config = ConfigDict(extra='forbid')

    type: Literal['figure', 'diagram']
    src: str | None = None       # path to image/diagram; extension determines rendering (.jpg/.png → <img>, .svg → inline SVG, .mmd → Mermaid)
    alt_text: str | None = None  # required for ADA; enforced by compiler
    source: str | None = None    # inline Mermaid source (legacy; prefer src with .mmd file)


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


class TableCell(BaseModel):
    """A table cell with optional colspan (for spanning header rows)."""
    model_config = ConfigDict(extra='forbid')
    text: str
    colspan: int = 1


class TableSlide(SlideBase):
    """Data table with accessible markup."""
    layout: Literal['table']
    caption: str | None = None
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str | TableCell]] = Field(default_factory=list)
    row_headers: bool = False


class ProofSlide(SlideBase):
    """Proof or derivation slide (Mathematical flavor).

    Identical rendering to ContentSlide; distinguished layout type for
    future visual differentiation and slide-count statistics.
    """
    layout: Literal['proof']


# ---------------------------------------------------------------------------
# Discriminated union covering all layout types
# ---------------------------------------------------------------------------

AnySlide = Annotated[
    Union[
        TitleSlide,
        HeroSlide,
        ContentSlide,
        TranscribeSlide,
        DividerSlide,
        FigureSlide,
        FigureWideSlide,
        DiagramSlide,
        TwoColumnSlide,
        QuoteSlide,
        ComparisonSlide,
        CodeSlide,
        StepsSlide,
        SummarySlide,
        TableSlide,
        ProofSlide,
    ],
    Field(discriminator='layout'),
]


# ---------------------------------------------------------------------------
# Deck metadata and top-level deck container
# ---------------------------------------------------------------------------

VALID_FONTS = ('IBM Plex Sans', 'Inter', 'Fira Sans', 'Roboto', 'Source Sans 3')


class DeckMetadata(BaseModel):
    """Deck-level metadata from the first frontmatter block.

    Attributes:
        flavor: If ``'transcript'``, HTML uses dense left-aligned styling for
            ``content`` and ``table`` slides (transcript / transcribe_to_html).
            Omitted for standard presentation decks.
    """
    model_config = ConfigDict(extra='forbid')

    title: str
    author: str | None = None
    date: _date | None = Field(default_factory=_date.today)
    theme: Literal['dark', 'light'] = 'dark'
    accent_color: str | None = None
    font: str = 'IBM Plex Sans'
    macros: str | None = None  # path to color-macro YAML file (relative to deck YAML)
    title_font_size: str = '2.4rem'
    title_top_margin: str = '0.5rem'
    flavor: Literal['transcript'] | None = None
    math_display_scale: float = Field(
        1.0,
        ge=0.75,
        le=2.0,
        description='Multiplier for $$...$$ display math font size vs slide body.',
    )
    math_display_center: bool = Field(
        True,
        description='If True, display math is centered; if False, aligned with body text.',
    )
    math_display_color: str | None = Field(
        default=None,
        description='Optional CSS color for $$...$$ (display / block) math in slide bodies and tables.',
    )

    @field_validator('math_display_color')
    @classmethod
    def _v_deck_math_color(cls, v: str | None) -> str | None:
        return _check_math_display_color(v)

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
