"""Tests for JSON Schema generation from Pydantic models."""
from __future__ import annotations

import json
import pytest
import jsonschema

from schema.json_schema import generate_schema, write_schema

# All 12 layout model class names that must appear in $defs
EXPECTED_SLIDE_DEFS = {
    'TitleSlide', 'HeroSlide', 'ContentSlide', 'DividerSlide',
    'FigureSlide', 'DiagramSlide', 'TwoColumnSlide', 'QuoteSlide',
    'ComparisonSlide', 'CodeSlide', 'StepsSlide', 'SummarySlide',
}


def test_schema_generates():
    """generate_schema() returns a dict with $defs and properties."""
    schema = generate_schema()
    assert '$defs' in schema
    assert 'properties' in schema


def test_schema_has_all_layout_types():
    """All 12 slide type models appear in $defs."""
    schema = generate_schema()
    defs = set(schema['$defs'].keys())
    for expected in EXPECTED_SLIDE_DEFS:
        assert expected in defs, f"Missing $defs entry: {expected}"


def test_schema_has_metadata():
    """DeckMetadata model appears in $defs."""
    schema = generate_schema()
    assert 'DeckMetadata' in schema['$defs']


def test_schema_write_file(tmp_path):
    """write_schema() creates a valid JSON file."""
    out = tmp_path / 'test.json'
    result_path = write_schema(out)
    assert result_path == out
    assert out.exists()
    # Must be valid JSON
    content = json.loads(out.read_text(encoding='utf-8'))
    assert '$defs' in content


def test_schema_validates_valid_deck():
    """A well-formed deck dict validates against the generated JSON Schema."""
    schema = generate_schema()
    valid_deck = {
        'metadata': {'title': 'My Deck'},
        'slides': [
            {'layout': 'title', 'title': 'Hello World'},
            {'layout': 'figure', 'title': 'A Figure', 'src': 'img.png', 'alt_text': 'Alt'},
        ],
    }
    # Should not raise
    jsonschema.validate(instance=valid_deck, schema=schema)


def test_schema_rejects_invalid():
    """A deck missing required field raises jsonschema.ValidationError."""
    schema = generate_schema()
    invalid_deck = {
        'metadata': {},  # missing required 'title'
        'slides': [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_deck, schema=schema)


def test_schema_contains_title_and_figure_defs():
    """Spot-check: TitleSlide and FigureSlide exist in $defs."""
    schema = generate_schema()
    assert 'TitleSlide' in schema['$defs']
    assert 'FigureSlide' in schema['$defs']
