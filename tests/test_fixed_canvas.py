"""Fixed-canvas model assertions on compiled HTML (see plan 2026-06-11)."""
import sys
from pathlib import Path

import pytest

from schema.models import Deck, DeckMetadata, TitleSlide, ContentSlide, FigureSlide
from compiler import compile_deck


def _deck(*slides, **meta):
    m = dict(title='Fixed Canvas Test', theme='dark')
    m.update(meta)
    return Deck(metadata=DeckMetadata(**m), slides=list(slides))


def _compile(deck, tmp_path) -> str:
    out = tmp_path / 'out.html'
    compile_deck(deck, str(out))
    return out.read_text()
