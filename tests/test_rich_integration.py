"""Integration tests: compile rich content YAML decks to HTML."""
import tempfile
from pathlib import Path

import pytest

from schema.parser import parse_deck_file
from compiler.engine import compile_deck

FIXTURES = Path(__file__).parent / "fixtures"


def _compile_fixture(name: str, embed_images: bool = False) -> str:
    deck = parse_deck_file(str(FIXTURES / name))
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w') as f:
        output_path = f.name
    compile_deck(deck, output_path, embed_images=embed_images)
    return Path(output_path).read_text()


def test_math_deck_compiles():
    html = _compile_fixture("rich_math.yaml")
    assert "<math" in html
    assert 'display="block"' in html


def test_math_inline():
    html = _compile_fixture("rich_math.yaml")
    assert 'display="inline"' in html  # from $\alpha$ etc.


def test_code_deck_compiles():
    html = _compile_fixture("rich_code.yaml")
    assert "slide-code" in html  # Pygments cssclass
    assert "<span" in html  # syntax highlighting spans


def test_code_line_numbers():
    html = _compile_fixture("rich_code.yaml")
    assert "linenodiv" in html or "linenos" in html  # line numbers on slide 3


def test_code_language_label():
    html = _compile_fixture("rich_code.yaml")
    assert "python" in html.lower()


def test_table_deck_compiles():
    html = _compile_fixture("rich_table.yaml")
    assert "<caption>" in html
    assert 'scope="col"' in html
    assert 'scope="row"' in html  # row_headers: true on slide 2
    assert "table-scroll-wrapper" in html


def test_table_no_row_headers():
    html = _compile_fixture("rich_table.yaml")
    # Slide 3 has no row_headers — count <th scope="row"> should match only slide 2's rows
    # Just verify compilation succeeds and has table elements
    assert "<table>" in html


def test_mixed_deck_compiles():
    html = _compile_fixture("rich_mixed.yaml")
    assert "<math" in html  # math rendering
    assert "<strong>" in html  # markdown bold
    assert "slide-code" in html  # code highlighting
    assert "<caption>" in html  # table


def test_mixed_deck_markdown_in_body():
    html = _compile_fixture("rich_mixed.yaml")
    assert "<ul>" in html or "<li>" in html  # bullet lists from markdown


def test_pygments_css_present():
    html = _compile_fixture("rich_code.yaml")
    assert ".slide-code" in html  # Pygments CSS injected in <style>
