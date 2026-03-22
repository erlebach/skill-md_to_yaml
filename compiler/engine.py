"""Compiler engine: validate-then-render pipeline."""
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from schema.models import Deck
from compiler.validators import validate_deck

TEMPLATES_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
    keep_trailing_newline=True,
)


def compile_deck(deck: Deck, output_path: str) -> None:
    """Validate deck and render to a self-contained HTML file.

    Errors (missing alt_text, bad contrast) halt with exit code 1.
    Warnings (layout variety, bullet limits) print to stderr but produce output.
    """
    errors, warnings = validate_deck(deck)

    for w in warnings:
        print(w, file=sys.stderr)

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)

    html = _render(deck)
    Path(output_path).write_text(html, encoding="utf-8")


def _render(deck: Deck) -> str:
    """Render deck to HTML string using Jinja2 templates."""
    template = _env.get_template("base.html.j2")
    return template.render(deck=deck, total=len(deck.slides))
