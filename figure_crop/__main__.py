"""CLI: uv run python -m figure_crop <path/to/figures_dir/image.png>"""

from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path

from .server import CropContext, serve


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="figure_crop", description=__doc__)
    p.add_argument("image", help="Path to the source image (inside its figures dir).")
    p.add_argument("--port", type=int, default=0, help="Port (0 = pick free).")
    p.add_argument("--no-browser", action="store_true", help="Do not auto-open browser.")
    args = p.parse_args(argv)

    img = Path(args.image).resolve()
    if not img.exists():
        print(f"error: not found: {img}", file=sys.stderr)
        return 2
    if img.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        print(f"error: unsupported extension: {img.suffix}", file=sys.stderr)
        return 2

    ctx = CropContext(figures_dir=img.parent, source_filename=img.name)
    server = serve(ctx, port=args.port)
    host, port = server.server_address[:2]
    url = f"http://{host}:{port}/"
    print(f"figure_crop: editing {img}")
    print(f"figure_crop: open {url}")

    if not args.no_browser:
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nfigure_crop: bye")
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
