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


def test_fixed_canvas_structure(tmp_path):
    """Stage is a fixed-size canvas; slides are absolute layers; no scroll-snap. [FC-02]"""
    html = _compile(_deck(
        TitleSlide(layout='title', title='T'),
        ContentSlide(layout='content', title='C', body='text'),
    ), tmp_path)
    style = html
    assert 'scroll-snap-type' not in style          # scroll model removed
    assert 'scrollIntoView' not in style            # nav rewritten (Task 1.3)
    assert '--deck-canvas-w: 1280' in style
    assert '--deck-canvas-h: 720' in style
    # stage center-pinned by arithmetic
    assert 'margin: -360px 0 0 -640px' in style or 'margin:-360px 0 0 -640px' in style
    # slides are visibility-toggled layers
    assert '.active' in style
    # printing/PDF export lays slides out statically (migrate_deck.py print block)
    assert 'page-break-after: always' in style


def test_controller_is_fixed_canvas(tmp_path):
    """Controller toggles .active, measures the clip via ResizeObserver, supports touch. [FC-03]"""
    html = _compile(_deck(
        TitleSlide(layout='title', title='T'),
        ContentSlide(layout='content', title='C', body='text'),
    ), tmp_path)
    assert 'ResizeObserver' in html
    assert "classList.toggle('active'" in html or 'classList.toggle("active"' in html
    assert 'touchstart' in html and 'touchend' in html
    assert '--deck-fit-scale' in html
    assert 'scrollIntoView' not in html
    assert 'deck-hud' in html          # #debug instrumentation (migrate_deck.py HUD)


def test_autofit_present(tmp_path):
    """An autofit routine shrinks any slide whose content exceeds the canvas. [FC-04]"""
    html = _compile(_deck(
        TitleSlide(layout='title', title='A very long title that would overflow', subtitle='And a subtitle'),
    ), tmp_path)
    assert 'autofitAll' in html
    assert 'scrollWidth' in html               # width overflow handled, not just height
    assert 'style.zoom' in html


def test_mermaid_svg_labels(tmp_path):
    """Mermaid uses SVG-native labels and defers behind fonts.ready. [FC-05]"""
    from schema.models import DiagramSlide
    html = _compile(_deck(
        DiagramSlide(layout='diagram', title='D', alt_text='a graph',
                     body='graph TD\n  A[Start] --> B[End]'),
    ), tmp_path)
    assert 'htmlLabels: false' in html
    assert 'htmlLabels: true' not in html
    assert 'fonts.ready' in html
    # a fonts.ready gate must sit between mermaid.initialize() and the actual
    # `await mermaid.run()` call, so labels measure with the real typeface
    run_pos = html.index('await mermaid.run()')
    gate_pos = html.rindex('fonts.ready', 0, run_pos)
    assert gate_pos > html.index('mermaid.initialize')


def test_mermaid_sizes_against_canvas(tmp_path):
    """Mermaid runtime sizing uses canvas constants, not window.innerHeight. [FC-06]"""
    from schema.models import DiagramSlide
    html = _compile(_deck(
        DiagramSlide(layout='diagram', title='D', alt_text='a graph', body='graph TD\n A-->B'),
    ), tmp_path)
    # the sizing helpers must reference the canvas height/width, and must not
    # measure the live window for diagram available-space
    assert 'CANVAS_H' in html and 'CANVAS_W' in html
    assert 'window.innerHeight - SLIDE_PAD' not in html
    assert 'document.documentElement.clientWidth' not in html
    # rect measurements are converted out of the transformed viewport space
    assert 'deckFitScale' in html


def test_bounds_audit_emitted(tmp_path):
    """The compiled page exposes the slide-boundary audit hook. [FC-09a]"""
    html = _compile(_deck(TitleSlide(layout='title', title='T')), tmp_path)
    assert '__mdToYamlAuditBounds' in html
    assert 'visibleRect' in html


def test_no_element_crosses_slide_boundary(tmp_path):
    """No element's visible box crosses its slide's 1280x720 rect. [FC-09b]"""
    pytest.importorskip('playwright.sync_api')
    from playwright.sync_api import sync_playwright
    from schema.models import CodeSlide, SummarySlide
    out = tmp_path / 'audit.html'
    compile_deck(_deck(
        TitleSlide(layout='title', title='A deliberately long stress title for the canvas',
                   subtitle='Subtitle that wraps across the fixed slide width'),
        ContentSlide(layout='content', title='Dense content',
                     body='\n'.join('- bullet point %d with some longer text' % i for i in range(14))),
        CodeSlide(layout='code', title='Code', language='python',
                  body='\n'.join('print(%d)' % i for i in range(40))),
        SummarySlide(layout='summary', title='Summary', body='- Done\n- Really done'),
    ), str(out))
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 720})   # fit scale == 1
        page.goto(out.as_uri())
        page.wait_for_function('() => !!window.__mdToYamlAuditBounds')
        page.wait_for_timeout(700)        # fonts.ready re-runs autofit; let it settle
        violations = page.evaluate('window.__mdToYamlAuditBounds(1.5)')
        browser.close()
    assert violations == [], f'elements crossing slide bounds: {violations}'
