"""Parametrized tests for real-world deck YAML fixtures.

Discovers all files matching tests/fixtures/real_*.yaml and validates each
parses without errors via parse_deck_file().
"""
import pytest
from pathlib import Path

from schema.parser import parse_deck_file

FIXTURES_DIR = Path(__file__).parent / 'fixtures'
REAL_WORLD_FIXTURES = sorted(FIXTURES_DIR.glob('real_*.yaml'))


@pytest.mark.parametrize("deck_path", REAL_WORLD_FIXTURES, ids=lambda p: p.stem)
def test_real_world_deck_parses(deck_path):
    """Deck parses without errors and has slides + metadata title."""
    deck = parse_deck_file(deck_path)
    assert len(deck.slides) > 0, f"Expected slides in {deck_path.name}, got 0"
    assert deck.metadata.title, f"Expected non-empty title in {deck_path.name}"


@pytest.mark.parametrize("deck_path", REAL_WORLD_FIXTURES, ids=lambda p: p.stem)
def test_real_world_deck_layout_types_valid(deck_path):
    """Every slide has a non-None layout field."""
    deck = parse_deck_file(deck_path)
    for i, slide in enumerate(deck.slides):
        assert slide.layout is not None, (
            f"Slide {i} in {deck_path.name} has layout=None"
        )
