"""CLI entry point: python -m compiler input.yaml output.html"""
import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile YAML slide deck to ADA-compliant HTML"
    )
    parser.add_argument("input", help="Input YAML deck file path")
    parser.add_argument("output", help="Output HTML file path")
    parser.add_argument(
        "--embed-images",
        action="store_true",
        default=False,
        help="Embed images as base64 data URIs",
    )
    parser.add_argument(
        "--include-skipped",
        action="store_true",
        default=False,
        help="Render slides marked skip: true (omitted by default)",
    )
    parser.add_argument(
        "--figure-layout-debug",
        action="store_true",
        default=False,
        help="Draw red debug borders on layout figure panel vs graphic (also: YAML figure_layout_debug: true)",
    )
    args = parser.parse_args()

    from schema.parser import parse_deck_file
    from compiler.engine import compile_deck  # noqa: F401 — created in Plan 03

    deck = parse_deck_file(args.input)
    compile_deck(
        deck,
        args.output,
        embed_images=args.embed_images,
        include_skipped=args.include_skipped,
        figure_layout_debug=args.figure_layout_debug,
    )


if __name__ == "__main__":
    main()
