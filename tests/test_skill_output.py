"""Tests validating LLM-generated YAML output meets schema and design constraints.

Covers LLM-02 (design constraints) and LLM-03 (schema validation).
"""
import pytest
from pathlib import Path
from schema.parser import parse_deck_file
from compiler.validators import validate_deck

FIXTURE = Path(__file__).parent / "fixtures" / "skill_output_sample.yaml"


def test_fixture_validates():
    """Fixture parses successfully and contains at least 10 slides."""
    deck = parse_deck_file(str(FIXTURE))
    assert len(deck.slides) >= 10


def test_layout_variety():
    """No 3+ consecutive slides share the same layout type."""
    deck = parse_deck_file(str(FIXTURE))
    layouts = [s.layout for s in deck.slides]
    for i in range(len(layouts) - 2):
        assert not (layouts[i] == layouts[i + 1] == layouts[i + 2]), (
            f"3+ consecutive '{layouts[i]}' at positions {i}-{i+2}"
        )


def test_alt_text_present():
    """All diagram and figure slides have non-empty alt_text."""
    deck = parse_deck_file(str(FIXTURE))
    for i, slide in enumerate(deck.slides):
        if slide.layout in ("diagram", "figure"):
            assert hasattr(slide, "alt_text") and slide.alt_text, (
                f"Slide {i + 1} ({slide.layout}) missing alt_text"
            )


def test_all_layout_types_variety():
    """Fixture uses at least 6 different layout types to demonstrate variety."""
    deck = parse_deck_file(str(FIXTURE))
    unique_layouts = set(s.layout for s in deck.slides)
    assert len(unique_layouts) >= 6, (
        f"Only {len(unique_layouts)} unique layouts: {unique_layouts}"
    )


def test_validate_deck_no_errors():
    """validate_deck() returns empty errors list (no ADA or design violations)."""
    deck = parse_deck_file(str(FIXTURE))
    errors, warnings = validate_deck(deck)
    assert len(errors) == 0, f"Validation errors: {errors}"


def test_no_body_in_frontmatter():
    """Fixture parses without body-in-frontmatter error (parse_deck_file would raise if it had one)."""
    deck = parse_deck_file(str(FIXTURE))
    assert deck is not None


def test_bad_yaml_body_in_frontmatter(tmp_path):
    """YAML with 'body:' field in slide frontmatter raises an error."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text(
        "---\n"
        "title: Test\n"
        "author: Test\n"
        "date: 2026-01-01\n"
        "theme: dark\n"
        "---\n"
        "\n"
        "---\n"
        "layout: content\n"
        "title: Bad Slide\n"
        "body: This should not be here\n"
        "---\n"
    )
    with pytest.raises((ValueError, Exception)):
        parse_deck_file(str(bad_yaml))


def test_bad_yaml_unknown_layout(tmp_path):
    """YAML with an unknown layout value raises a validation error."""
    bad_yaml = tmp_path / "bad2.yaml"
    bad_yaml.write_text(
        "---\n"
        "title: Test\n"
        "author: Test\n"
        "date: 2026-01-01\n"
        "theme: dark\n"
        "---\n"
        "\n"
        "---\n"
        "layout: bullet-list\n"
        "title: Unknown Layout\n"
        "---\n"
        "- item 1\n"
    )
    with pytest.raises(Exception):
        parse_deck_file(str(bad_yaml))
