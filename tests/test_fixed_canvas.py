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


@pytest.mark.xfail(reason='section-level 100vh/100vw removed in Task 1.2', strict=True)
def test_no_fluid_units_in_output(tmp_path):
    """Compiled CSS must contain no clamp()/vw/vh/in fluid units. [FC-01]"""
    import re
    html = _compile(_deck(
        TitleSlide(layout='title', title='T', subtitle='S'),
        ContentSlide(layout='content', title='C', body='- a\n- b'),
    ), tmp_path)
    style = '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', html, re.S))
    assert 'clamp(' not in style
    assert not re.search(r'\b\d*\.?\d+vw\b', style)
    assert not re.search(r'\b\d*\.?\d+vh\b', style)
    assert not re.search(r'\b\d*\.?\d+vmin\b', style)
    assert not re.search(r'\b\d*\.?\d+vmax\b', style)
    assert not re.search(r'(?<![\w.])\d*\.?\d+in\b', style)
