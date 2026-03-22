"""Integration tests for the compiler engine (COMP-01 through COMP-06, ADA-02 through ADA-05)."""
import subprocess
import sys
from pathlib import Path

import pytest

from schema.models import (
    Deck, DeckMetadata, TitleSlide, ContentSlide, HeroSlide, DividerSlide,
    FigureSlide, DiagramSlide, TwoColumnSlide, QuoteSlide, ComparisonSlide,
    CodeSlide, StepsSlide, SummarySlide, ColumnContent,
)
from compiler import compile_deck


def _minimal_deck(**meta_overrides):
    meta_kwargs = dict(title='Test Deck', theme='dark')
    meta_kwargs.update(meta_overrides)
    return Deck(
        metadata=DeckMetadata(**meta_kwargs),
        slides=[
            TitleSlide(layout='title', title='Hello', subtitle='World'),
            ContentSlide(layout='content', title='Slide 2', body='Some text'),
        ],
    )


def test_compile_produces_html(tmp_path):
    """compile_deck() writes a valid HTML file. [COMP-01]"""
    out = tmp_path / 'out.html'
    compile_deck(_minimal_deck(), str(out))
    assert out.exists()
    content = out.read_text()
    assert '<!DOCTYPE html>' in content
    assert '</html>' in content


def test_all_layout_types_render(tmp_path):
    """Every layout type renders a <section> with correct heading ID. [COMP-02]"""
    slides = [
        TitleSlide(layout='title', title='T'),
        HeroSlide(layout='hero', title='H'),
        ContentSlide(layout='content', title='C', body='text'),
        DividerSlide(layout='divider', title='D'),
        FigureSlide(layout='figure', title='F', src='img.png', alt_text='An image'),
        DiagramSlide(layout='diagram', title='Dg', alt_text='A diagram'),
        TwoColumnSlide(layout='two-column', title='TC'),
        QuoteSlide(layout='quote', title='Q'),
        ComparisonSlide(layout='comparison', title='Cmp', body='A <!-- split --> B'),
        CodeSlide(layout='code', title='Cd', body='print("hi")', language='python'),
        StepsSlide(layout='steps', title='St', body='1. Step one'),
        SummarySlide(layout='summary', title='S', body='- Done'),
    ]
    deck = Deck(metadata=DeckMetadata(title='All Layouts', theme='dark'), slides=slides)
    out = tmp_path / 'all.html'
    compile_deck(deck, str(out))
    content = out.read_text()
    for i in range(1, 13):
        assert f'id="slide-{i}-heading"' in content


def test_deterministic_output(tmp_path):
    """Same input produces byte-identical output. [COMP-03]"""
    deck = _minimal_deck()
    out1 = tmp_path / 'a.html'
    out2 = tmp_path / 'b.html'
    compile_deck(deck, str(out1))
    compile_deck(deck, str(out2))
    assert out1.read_text() == out2.read_text()


def test_cli_invocation(tmp_path):
    """CLI entry point compiles YAML to HTML. [COMP-04]"""
    yaml_content = """\
---
title: CLI Test
theme: dark
---
layout: title
title: Hello
---
"""
    input_yaml = tmp_path / 'input.yaml'
    input_yaml.write_text(yaml_content)
    output_html = tmp_path / 'output.html'
    result = subprocess.run(
        [sys.executable, '-m', 'compiler', str(input_yaml), str(output_html)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert output_html.exists()


def test_css_vars_embedded(tmp_path):
    """CSS custom properties are embedded in output. [COMP-05]"""
    out = tmp_path / 'out.html'
    compile_deck(_minimal_deck(), str(out))
    content = out.read_text()
    assert '--bg' in content
    assert '--accent' in content
    assert '--text' in content


def test_keyboard_js_embedded(tmp_path):
    """Keyboard navigation JS is embedded. [COMP-06]"""
    out = tmp_path / 'out.html'
    compile_deck(_minimal_deck(), str(out))
    content = out.read_text()
    for key in ('ArrowRight', 'ArrowLeft', 'Home', 'End'):
        assert key in content


def test_aria_carousel_markup(tmp_path):
    """ARIA carousel role is present. [ADA-02]"""
    out = tmp_path / 'out.html'
    compile_deck(_minimal_deck(), str(out))
    content = out.read_text()
    assert 'aria-roledescription="carousel"' in content


def test_skip_link_present(tmp_path):
    """Skip link for keyboard users exists. [ADA-03]"""
    out = tmp_path / 'out.html'
    compile_deck(_minimal_deck(), str(out))
    content = out.read_text()
    assert 'skip-link' in content
    assert '#main-content' in content


def test_aria_labelledby(tmp_path):
    """Each slide section has aria-labelledby linked to heading. [ADA-04]"""
    out = tmp_path / 'out.html'
    compile_deck(_minimal_deck(), str(out))
    content = out.read_text()
    assert 'aria-labelledby="slide-1-heading"' in content
    assert 'id="slide-1-heading"' in content
    assert 'aria-labelledby="slide-2-heading"' in content
    assert 'id="slide-2-heading"' in content


def test_cli_error_exit_code(tmp_path):
    """CLI exits 1 when validation errors occur (bad contrast)."""
    yaml_content = """\
---
title: Bad Contrast
theme: light
accent_color: "#f0a500"
---
layout: title
title: Fail
---
"""
    input_yaml = tmp_path / 'bad.yaml'
    input_yaml.write_text(yaml_content)
    output_html = tmp_path / 'out.html'
    result = subprocess.run(
        [sys.executable, '-m', 'compiler', str(input_yaml), str(output_html)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1


# ---------------------------------------------------------------------------
# Real-world fixture tests
# ---------------------------------------------------------------------------

REAL_FIXTURES = sorted(Path('tests/fixtures').glob('real_*.yaml'))


def test_real_fixtures_exist():
    """All 5 real-world YAML fixtures are present."""
    assert len(REAL_FIXTURES) == 5


@pytest.mark.parametrize("fixture", REAL_FIXTURES, ids=lambda p: p.stem)
def test_real_fixture_compiles(fixture, tmp_path):
    """Real-world fixture compiles to valid HTML with ARIA structure."""
    from schema.parser import parse_deck_file
    deck = parse_deck_file(str(fixture))
    out = tmp_path / f"{fixture.stem}.html"
    compile_deck(deck, str(out))
    assert out.exists()
    content = out.read_text()
    assert '<!DOCTYPE html>' in content
    assert 'aria-roledescription="carousel"' in content
    assert 'class="skip-link"' in content
    # Each slide renders a <section role="group"> — count section tags with role
    import re
    assert len(re.findall(r'<section[^>]*role="group"', content)) == len(deck.slides)


def test_real_fixture_deterministic(tmp_path):
    """First real fixture produces identical output on repeated compilation."""
    from schema.parser import parse_deck_file
    fixture = REAL_FIXTURES[0]
    deck = parse_deck_file(str(fixture))
    out1 = tmp_path / 'a.html'
    out2 = tmp_path / 'b.html'
    compile_deck(deck, str(out1))
    compile_deck(deck, str(out2))
    assert out1.read_text() == out2.read_text()
