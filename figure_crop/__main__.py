"""CLI entry point for figure_crop.

Subcommands
-----------
  crop  (default)  Interactive single-image crop editor.
  slide            Slide HTML dev server with in-browser crop + live reload.

Examples
--------
  uv run python -m figure_crop path/to/image.png
  uv run python -m figure_crop slide path/to/slides.html
  uv run python -m figure_crop slide path/to/slides.html --yaml src.yaml --port 8080
"""

from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path


# ---------------------------------------------------------------------------
# crop (single-image editor)
# ---------------------------------------------------------------------------

def _cmd_crop(args) -> int:
    from .server import CropContext, serve

    img = Path(args.image).resolve()
    if not img.exists():
        print(f'error: not found: {img}', file=sys.stderr)
        return 2
    if img.suffix.lower() not in {'.png', '.jpg', '.jpeg'}:
        print(f'error: unsupported extension: {img.suffix}', file=sys.stderr)
        return 2

    ctx = CropContext(
        figures_dir=img.parent,
        source_filename=img.name,
        write_captions=args.write_captions,
    )
    server = serve(ctx, port=args.port)
    host, port = server.server_address[:2]
    url = f'http://{host}:{port}/'
    print(f'figure_crop: editing  {img}')
    stem = img.stem
    ext = img.suffix.lower().replace('.jpeg', '.jpg')
    print(f'figure_crop: output → {img.with_name(stem + ".cropped" + ext)}')
    print(f'figure_crop: captions.yaml = {"ON" if args.write_captions else "OFF"}')
    print(f'figure_crop: open {url}')

    if not args.no_browser:
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        last = ctx.last_cropped_path
        if last is not None:
            print(f'figure_crop: last write → {last}')
        else:
            print('figure_crop: no crop was saved this session.')
        server.shutdown()
    return 0


# ---------------------------------------------------------------------------
# slide (dev server)
# ---------------------------------------------------------------------------

def _find_compile_sh(html_path: Path) -> Path | None:
    """Walk up from html_path to find .claude/skills/md_to_yaml/compile.sh."""
    rel = Path('.claude') / 'skills' / 'md_to_yaml' / 'compile.sh'
    for candidate in [html_path.parent, *html_path.parents]:
        p = candidate / rel
        if p.exists():
            return p.resolve()
    return None


def _cmd_slide(args) -> int:
    from .slidedev import serve
    import subprocess as _sp

    input_path = Path(args.html).resolve()

    # Accept a YAML file directly — derive the HTML path and compile first.
    if input_path.suffix.lower() in ('.yaml', '.yml'):
        yaml_path = input_path
        if not yaml_path.exists():
            print(f'error: not found: {yaml_path}', file=sys.stderr)
            return 2
        html_path = yaml_path.with_suffix('.html')
        compile_sh = Path(args.compile_script).resolve() if args.compile_script else _find_compile_sh(yaml_path)
        if compile_sh is None or not compile_sh.exists():
            print('error: could not locate compile.sh', file=sys.stderr)
            return 2
        print(f'slide_dev: compiling {yaml_path.name} …', flush=True)
        r = _sp.run(['bash', str(compile_sh), str(yaml_path), str(html_path)],
                    capture_output=True, text=True, cwd=str(yaml_path.parent))
        if r.returncode != 0:
            print(f'slide_dev: compile error:\n{r.stderr}', file=sys.stderr)
            return 1
        print(f'slide_dev: compiled  → {html_path.name}', flush=True)
    else:
        html_path = input_path
        if not html_path.exists():
            print(f'error: not found: {html_path}', file=sys.stderr)
            return 2
        if html_path.suffix.lower() != '.html':
            print(f'error: expected a .yaml or .html file, got {html_path.suffix}', file=sys.stderr)
            return 2
        yaml_path = Path(args.yaml).resolve() if args.yaml else html_path.with_suffix('.yaml')
        if not yaml_path.exists():
            print(f'error: YAML source not found: {yaml_path}', file=sys.stderr)
            print('      pass --yaml path/to/source.yaml explicitly', file=sys.stderr)
            return 2
        compile_sh = Path(args.compile_script).resolve() if args.compile_script else _find_compile_sh(html_path)
        if compile_sh is None or not compile_sh.exists():
            print('error: could not locate compile.sh', file=sys.stderr)
            return 2

    compile_sh = Path(args.compile_script).resolve() if args.compile_script else _find_compile_sh(html_path)
    if compile_sh is None or not compile_sh.exists():
        print('error: could not locate compile.sh', file=sys.stderr)
        print('      pass --compile-script path/to/compile.sh explicitly', file=sys.stderr)
        return 2

    server = serve(html_path, yaml_path, compile_sh, port=args.port)
    host, port = server.server_address[:2]
    url = f'http://{host}:{port}/'
    from .slidedev import _find_repo_root
    serve_root = _find_repo_root(html_path) or html_path.parent
    html_rel = html_path.resolve().relative_to(serve_root.resolve()).as_posix()
    print(f'slide_dev: html        {html_path}')
    print(f'slide_dev: yaml        {yaml_path}')
    print(f'slide_dev: compile     {compile_sh}')
    print(f'slide_dev: serve root  {serve_root}')
    print(f'slide_dev: open        {url}{html_rel}')
    print('slide_dev: drag on any image to select crop, press c to save and recompile.')

    if not args.no_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.shutdown()
    return 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='figure_crop', description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='cmd')

    # -- crop subcommand (also the default when no subcommand is given) ------
    p_crop = sub.add_parser('crop', help='Single-image interactive crop editor.')
    p_crop.add_argument('image', help='Path to the source image.')
    p_crop.add_argument('--port', type=int, default=0)
    p_crop.add_argument('--no-browser', action='store_true')
    p_crop.add_argument('--write-captions', action='store_true',
                        help='Update captions.yaml alongside the sidecar JSON.')

    # -- slide subcommand ----------------------------------------------------
    p_slide = sub.add_parser('slide', help='Slide HTML dev server with crop overlay.')
    p_slide.add_argument('html', help='Path to .yaml (compiles first) or already-compiled .html.')
    p_slide.add_argument('--yaml', default=None,
                         help='Source YAML (default: same stem as html).')
    p_slide.add_argument('--compile-script', default=None,
                         help='Path to compile.sh (auto-discovered by default).')
    p_slide.add_argument('--port', type=int, default=0)
    p_slide.add_argument('--no-browser', action='store_true')

    args = parser.parse_args(argv)

    # If no subcommand but first positional looks like an image, treat as crop.
    if args.cmd is None:
        if argv and not argv[0].startswith('-'):
            # Re-parse as crop subcommand
            return main(['crop'] + list(argv or []))
        parser.print_help()
        return 0

    if args.cmd == 'crop':
        return _cmd_crop(args)
    if args.cmd == 'slide':
        return _cmd_slide(args)

    parser.print_help()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
