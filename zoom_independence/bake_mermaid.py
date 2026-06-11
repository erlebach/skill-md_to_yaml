#!/usr/bin/env python3
"""
bake_mermaid.py — Pre-render Mermaid diagrams in HTML slide decks to static
inline SVG, making the pages deterministic and self-contained.

Why: runtime Mermaid lays out text per-browser. Engines disagree about glyph
widths (especially |⟩, ⊗, Greek), so nodes clip in one browser and balloon in
another. Baking renders ONCE, freezing all coordinates; every browser then
paints identical geometry. It also removes the jsDelivr CDN dependency.

Setup (one time, on a machine with normal network access):
  npm install -g @mermaid-js/mermaid-cli      # provides `mmdc` + headless Chromium

Usage:
  python3 bake_mermaid.py deck1.html deck2.html ...
  -> writes deck1-baked.html etc. (originals untouched)

Recommended pipeline:  bake first, then migrate:
  python3 bake_mermaid.py deck.html
  python3 migrate_deck.py deck-baked.html
(Order doesn't strictly matter; migrate's Mermaid patch no-ops once baked.)
"""

import html as htmlmod
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Mirrors the runtime config in migrate_deck.py so baked and unbaked decks match.
MERMAID_CONFIG = {
    "theme": "dark",
    "fontFamily": '"IBM Plex Sans", sans-serif',
    "htmlLabels": False,
    "flowchart": {"htmlLabels": False, "useMaxWidth": True, "padding": 24},
}

PRE_RE = re.compile(r'<pre class="mermaid"[^>]*>(.*?)</pre>', re.S)
CDN_RE = re.compile(r'<script type="module">\s*import mermaid.*?</script>\s*', re.S)


def render_one(source: str, workdir: Path, n: int) -> str:
    mmd = workdir / f"d{n}.mmd"
    svg = workdir / f"d{n}.svg"
    cfg = workdir / "config.json"
    cfg.write_text(json.dumps(MERMAID_CONFIG), encoding="utf-8")
    mmd.write_text(source, encoding="utf-8")
    subprocess.run(
        ["mmdc", "-i", str(mmd), "-o", str(svg),
         "-c", str(cfg), "-b", "transparent", "-q"],
        check=True)
    out = svg.read_text(encoding="utf-8")
    out = out[out.index("<svg"):]                    # drop any XML prolog
    # The wrapping <div role="img" aria-label="..."> in the deck carries the
    # accessible description; hide the raw SVG tree from assistive tech so
    # node labels aren't read out twice.
    out = out.replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)
    return out


def bake(path: Path) -> None:
    src = path.read_text(encoding="utf-8")
    if not PRE_RE.search(src):
        print(f"  {path.name}: no Mermaid blocks, skipped")
        return

    workdir = Path(tempfile.mkdtemp(prefix="bake_mermaid_"))
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        # contents are HTML-escaped in the deck; strip stray tags, unescape
        diagram = htmlmod.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        return render_one(diagram, workdir, count)

    out = PRE_RE.sub(repl, src)
    out = CDN_RE.sub("", out)                        # loader no longer needed

    dest = path.with_name(path.stem + "-baked" + path.suffix)
    dest.write_text(out, encoding="utf-8")
    print(f"  {path.name}: {count} diagram(s) baked -> {dest.name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: bake_mermaid.py deck.html [deck2.html ...]")
    for arg in sys.argv[1:]:
        bake(Path(arg))
