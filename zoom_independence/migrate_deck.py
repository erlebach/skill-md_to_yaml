#!/usr/bin/env python3
"""
migrate_deck.py — Retrofit a scroll-snap, fluid-unit HTML slide deck into a
fixed-canvas (1280x720) deck that scales uniformly to fit any viewport.

What it does, mechanically:
  1. FREEZE fluid units in <style> blocks at the reference viewport:
       clamp(A px, B vw, C px) -> px value of B at 1280px wide, bounded [A, C]
       N vw -> N * 12.80 px        N vh -> N * 7.20 px
       N vmin -> N * 7.20 px       N vmax -> N * 12.80 px
       N in -> N * 96 px
     (Layout therefore never reflows; the only variable left is one scale factor.)
  2. WRAP <main> in a viewport-filling .deck-wrap and append override CSS that
     stacks every section[role="group"] as an absolutely-positioned layer.
     Inactive slides use visibility:hidden (NOT display:none) so Mermaid and
     MathML can still measure themselves at render time.
  3. RELOCATE #slide-counter outside <main> (a CSS transform on an ancestor
     hijacks position:fixed descendants) and ADD prev/next buttons (44px touch
     targets) for phones, where there is no keyboard.
  4. REPLACE the scrollIntoView navigation script with one that:
       - sizes via ResizeObserver on .deck-wrap (immune to the iOS Safari
         innerHeight/toolbar problem -- we measure the container, never the window)
       - navigates by keyboard, swipe, and buttons
       - scale = min(w/1280, h/720): always letterboxes, never crops, no floor.

Usage:
  python3 migrate_deck.py input.html [more.html ...]
  -> writes input-fixedcanvas.html next to each input (originals untouched)
"""

import re
import sys
from pathlib import Path

REF_W, REF_H = 1280.0, 720.0

NUM = r"-?\d*\.?\d+"

def _fmt(v: float) -> str:
    return f"{v:.4g}px"

def _to_px(n: float, unit: str) -> float:
    return n * 16.0 if unit == "rem" else n

def _freeze_clamp(m: re.Match) -> str:
    lo = _to_px(float(m.group(1)), m.group(2))
    mid_n, mid_u = float(m.group(3)), m.group(4)
    hi = _to_px(float(m.group(5)), m.group(6))
    ref = REF_W if mid_u in ("vw", "vmax") else REF_H
    mid = mid_n * ref / 100.0
    return _fmt(min(max(mid, lo), hi))

def freeze_css(css: str) -> str:
    # clamp(Apx, Bvw|vh|vmin|vmax, Cpx) -> single frozen px value
    css = re.sub(
        rf"clamp\(\s*({NUM})(px|rem)\s*,\s*({NUM})(vw|vh|vmin|vmax)\s*,\s*({NUM})(px|rem)\s*\)",
        _freeze_clamp, css)
    # bare viewport units
    css = re.sub(rf"({NUM})vw\b",   lambda m: _fmt(float(m.group(1)) * REF_W / 100), css)
    css = re.sub(rf"({NUM})vh\b",   lambda m: _fmt(float(m.group(1)) * REF_H / 100), css)
    css = re.sub(rf"({NUM})vmin\b", lambda m: _fmt(float(m.group(1)) * REF_H / 100), css)
    css = re.sub(rf"({NUM})vmax\b", lambda m: _fmt(float(m.group(1)) * REF_W / 100), css)
    # physical units
    css = re.sub(rf"(?<![\w.])({NUM})in\b", lambda m: _fmt(float(m.group(1)) * 96), css)
    # collapse any clamp() left fully static by the passes above
    def _collapse(m):
        lo = _to_px(float(m.group(1)), m.group(2))
        mid = _to_px(float(m.group(3)), m.group(4))
        hi = _to_px(float(m.group(5)), m.group(6))
        return _fmt(min(max(mid, lo), hi))
    css = re.sub(
        rf"clamp\(\s*({NUM})(px|rem)\s*,\s*({NUM})(px|rem)\s*,\s*({NUM})(px|rem)\s*\)",
        _collapse, css)
    return css

OVERRIDE_CSS = """
    /* ====== fixed-canvas retrofit v2 (injected by migrate_deck.py) ====== */
    html, body { height: 100% !important; overflow: hidden !important;
                 overscroll-behavior: none; }
    .deck-wrap {
      position: fixed; inset: 0;
      overflow: hidden; background: var(--bg, #000);
    }
    /* Bulletproof centering: the element's center is pinned to the wrapper's
       center by arithmetic (50% offset minus half the fixed size). No grid,
       no flex, no alignment algorithm ever touches this oversized box --
       cross-engine alignment of overflowing boxes is where v1 broke. */
    .deck-wrap > main {
      position: absolute !important;
      left: 50% !important; top: 50% !important;
      margin: -360px 0 0 -640px !important;   /* half of 720 / half of 1280 */
      width: 1280px !important; height: 720px !important;
      overflow: hidden !important;
      scroll-snap-type: none !important;
      transform-origin: 50% 50%;
      flex: none !important;
    }
    /* Some generator variants nest sections inside an app-root div.
       A purely structural wrapper must not affect layout or clipping. */
    .deck-wrap main > div {
      position: static !important; width: 100% !important; height: 100% !important;
      margin: 0 !important; padding: 0 !important;
      overflow: visible !important; transform: none !important;
    }
    /* Target slides by what they ARE, not by DOM depth */
    .deck-wrap main section[aria-roledescription=slide] {
      position: absolute !important; inset: 0 !important;
      height: 100% !important; min-height: 0 !important;
      scroll-snap-align: none !important;
      visibility: hidden;           /* keeps layout: Mermaid/MathML can measure */
      overflow-y: auto;             /* safety valve if a slide overflows 720px */
    }
    .deck-wrap main section[aria-roledescription=slide].active { visibility: visible; }

    .deck-nav {
      position: fixed; bottom: 12px; left: 12px; z-index: 100;
      display: flex; gap: 8px;
    }
    .deck-nav button {
      min-width: 44px; min-height: 44px;
      font-size: 22px; line-height: 1;
      color: var(--text, #fff); background: var(--bg2, #222);
      border: 1px solid var(--border, #555); border-radius: 8px;
      cursor: pointer;
    }
    .deck-nav button:focus-visible { outline: 2px solid var(--accent, #fa0); outline-offset: 2px; }
    body > #slide-counter { position: fixed; bottom: 22px; right: 16px; z-index: 100;
      font: 600 14px sans-serif; color: var(--muted, #999); }
    /* Legacy in-deck chrome (footer nav / goto / view-scale): its controller was
       replaced, and transform re-anchors its fixed positioning into the canvas. */
    .deck-wrap main .slide-footer-nav,
    .deck-wrap main nav[id^="slide-footer"] { display: none !important; }

    #deck-hud {
      display: none;
      position: fixed; top: 8px; left: 8px; z-index: 999;
      font: 12px/1.5 monospace; color: #0f0; background: rgba(0,0,0,.8);
      padding: 8px 10px; border-radius: 6px; white-space: pre; pointer-events: none;
    }

    @media print {
      html, body { overflow: visible !important; height: auto !important; }
      .deck-wrap { position: static; }
      .deck-wrap > main { position: static !important; width: auto !important;
        height: auto !important; margin: 0 !important;
        overflow: visible !important; transform: none !important; }
      /* Some generator variants nest sections inside an app-root div.
       A purely structural wrapper must not affect layout or clipping. */
    .deck-wrap main > div {
      position: static !important; width: 100% !important; height: 100% !important;
      margin: 0 !important; padding: 0 !important;
      overflow: visible !important; transform: none !important;
    }
    /* Target slides by what they ARE, not by DOM depth */
    .deck-wrap main section[aria-roledescription=slide] {
        position: static !important; visibility: visible !important;
        height: auto !important; min-height: 0 !important;
        page-break-after: always; overflow: visible; }
      .deck-nav, #slide-counter, #deck-hud { display: none !important; }
    }
    /* Embedded math-glyph subset (DejaVu Sans, Bitstream Vera license).
       unicode-range limits it to glyphs IBM Plex Sans lacks, so every
       OS renders bra-kets and operators from these same bytes. */
    @font-face {
      font-family: 'Deck Math Glyphs';
      src: url(data:font/woff2;base64,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) format('woff2');
      unicode-range: U+2020, U+2032, U+210F, U+2192, U+2194, U+21A6, U+221A, U+2248, U+2260, U+2264, U+2265, U+2295, U+2297, U+22A5, U+22C5, U+27E8, U+27E9;
      font-display: block;
    }
    body, pre.mermaid svg text {
      font-family: 'IBM Plex Sans', 'Deck Math Glyphs', system-ui, sans-serif;
    }
    /* few-px text-metric drift between engines: spill, don't shear */
    pre.mermaid svg, pre.mermaid svg g { overflow: visible !important; }
    /* ====== end retrofit ====== */
"""

NAV_JS = """
  (function () {
    var W = 1280, H = 720;
    var stage = document.querySelector('main[aria-roledescription="carousel"]') ||
                document.querySelector('main');
    var deck = stage.closest('.deck-wrap');
    var slides = Array.prototype.slice.call(stage.querySelectorAll('section[role=\"group\"]'));
    var counter = document.getElementById('slide-counter');
    var hud = document.getElementById('deck-hud');
    var idx = 0;

    // ---- measurement & scaling -------------------------------------------
    // Measure the clipping element itself. A fixed inset:0 box tracks the
    // layout viewport correctly on iOS even mid-toolbar-animation, unlike
    // window.innerHeight. Centering is done by CSS arithmetic (50% + negative
    // margin), so the ONLY job of JS is the scale factor.
    function fit() {
      var r = deck.getBoundingClientRect();
      var s = Math.min(r.width / W, r.height / H);
      stage.style.transform = 'scale(' + s + ')';
      if (hud && location.hash.indexOf('debug') !== -1) {
        hud.style.display = 'block';
        var vv = window.visualViewport;
        var NL = String.fromCharCode(10);
        hud.textContent = [
          'wrapper  : ' + r.width.toFixed(1) + ' x ' + r.height.toFixed(1),
          'inner    : ' + window.innerWidth + ' x ' + window.innerHeight,
          (vv ? 'visualVP : ' + vv.width.toFixed(1) + ' x ' + vv.height.toFixed(1) +
                '  scale ' + vv.scale.toFixed(2) +
                '  offset ' + vv.offsetLeft.toFixed(0) + ',' + vv.offsetTop.toFixed(0)
              : 'visualVP : n/a'),
          'fit scale: ' + s.toFixed(4),
          'slide    : ' + (idx + 1) + '/' + slides.length\n        ].join(NL);
      }
    }

    // ---- navigation -------------------------------------------------------
    function show(n) {
      idx = Math.max(0, Math.min(n, slides.length - 1));
      slides.forEach(function (el, i) { el.classList.toggle('active', i === idx); });
      if (counter) counter.textContent = (idx + 1) + ' / ' + slides.length;
      var s = slides[idx];
      if (!s.hasAttribute('tabindex')) s.setAttribute('tabindex', '-1');
      try { s.focus({ preventScroll: true }); } catch (e) {}
      fit();
    }

    document.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ' || e.key === 'PageDown') {
        e.preventDefault(); show(idx + 1);
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp') {
        e.preventDefault(); show(idx - 1);
      } else if (e.key === 'Home') { e.preventDefault(); show(0); }
      else if (e.key === 'End') { e.preventDefault(); show(slides.length - 1); }
    });

    var tx = null, ty = null;
    deck.addEventListener('touchstart', function (e) {
      var t = e.changedTouches[0]; tx = t.clientX; ty = t.clientY;
    }, { passive: true });
    deck.addEventListener('touchend', function (e) {
      if (tx === null) return;
      var t = e.changedTouches[0], dx = t.clientX - tx, dy = t.clientY - ty;
      tx = ty = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > 1.5 * Math.abs(dy)) show(idx + (dx < 0 ? 1 : -1));
    }, { passive: true });

    var bp = document.getElementById('deck-prev'), bn = document.getElementById('deck-next');
    if (bp) bp.addEventListener('click', function () { show(idx - 1); });
    if (bn) bn.addEventListener('click', function () { show(idx + 1); });

    // ---- re-fit on every geometry signal -----------------------------------
    if (window.ResizeObserver) new ResizeObserver(fit).observe(deck);
    window.addEventListener('resize', fit);
    window.addEventListener('orientationchange', function () { setTimeout(fit, 300); });
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', fit);
      window.visualViewport.addEventListener('scroll', fit);
    }
    window.addEventListener('pageshow', fit);                       // bfcache restore
    if (document.fonts && document.fonts.ready)
      document.fonts.ready.then(fit);                               // late font metrics
    setTimeout(fit, 500); setTimeout(fit, 1500);                    // toolbar settle

    fit();
    show(0);
  })();
"""

NAV_HTML = """
  <div class="deck-nav">
    <button id="deck-prev" type="button" aria-label="Previous slide">&#8249;</button>
    <button id="deck-next" type="button" aria-label="Next slide">&#8250;</button>
  </div>
  <div id="deck-hud" aria-hidden="true"></div>
"""



MERMAID_RE = re.compile(
    r"<script type=\"module\">\s*import mermaid from\s*'([^']+)';.*?</script>",
    re.S)

def _mermaid_block(m):
    url = m.group(1)
    theme_m = re.search(r"theme:\s*'(\w+)'", m.group(0))
    theme = theme_m.group(1) if theme_m else "dark"
    return (
        '<script type="module">\n'
        f"    import mermaid from '{url}';\n"
        "    // htmlLabels:false renders labels as native SVG <text>.\n"
        "    // Default foreignObject labels break in WebKit (iOS) when any\n"
        "    // ancestor has a CSS transform -- our scaled stage does.\n"
        "    mermaid.initialize({\n"
        "      startOnLoad: false,\n"
        f"      theme: '{theme}',\n"
        "      htmlLabels: false,\n"
        "      fontFamily: '\"IBM Plex Sans\", \"Deck Math Glyphs\", sans-serif',\n"
        "      flowchart: { htmlLabels: false, useMaxWidth: true, padding: 24 }\n"
        "    });\n"
        "    // Render only after fonts load so label widths are measured\n"
        "    // with the real typeface, not a fallback.\n"
        "    if (document.fonts && document.fonts.ready) {\n"
        "      try { await document.fonts.ready; } catch (e) {}\n"
        "    }\n"
        "    await mermaid.run();\n"
        "  </script>")

def migrate(html: str) -> str:
    # 1. Freeze fluid units inside every <style> block.
    def style_repl(m):
        return m.group(1) + freeze_css(m.group(2)) + m.group(3)
    html = re.sub(r"(<style[^>]*>)(.*?)(</style>)", style_repl, html, flags=re.S)

    # 2. Append override CSS before </head>.
    html = html.replace("</head>", f"<style>{OVERRIDE_CSS}</style>\n</head>", 1)

    # 3. Pull #slide-counter out of <main> (transform ancestors break fixed pos).
    counter_m = re.search(
        r'<(div|span) id="slide-counter"[^>]*>.*?</\1>\s*', html, flags=re.S)
    if counter_m:                      # remove native counter (avoids duplicate id)
        html = html.replace(counter_m.group(0), "", 1)
    counter_html = ('<div id="slide-counter" aria-live="polite" '
                    'aria-atomic="true"></div>')

    # 4. Wrap <main> in .deck-wrap.
    html = re.sub(r"(<main\b)", r'<div class="deck-wrap">\n  \1', html, count=1)
    html = html.replace("</main>", "</main>\n  </div>", 1)

    # 5. Insert counter + nav buttons after the deck wrapper.
    insertion = "\n  " + counter_html + NAV_HTML
    html = html.replace("</main>\n  </div>", "</main>\n  </div>" + insertion, 1)

    # 6. Replace the scrollIntoView navigation script with the new controller.
    html = re.sub(
        r"<script>\s*\(function\(\)\s*\{.*?scrollIntoView.*?\}\)\(\);\s*</script>",
        "<script>" + NAV_JS + "</script>",
        html, count=1, flags=re.S)

    # 7. Patch Mermaid init: SVG-native labels + font-ready deferral.
    html = MERMAID_RE.sub(_mermaid_block, html, count=1)

    return html


MIGRATED_MARKER = "fixed-canvas retrofit"

def main(paths):
    for p in map(Path, paths):
        text = p.read_text(encoding="utf-8")
        if MIGRATED_MARKER in text or 'class="deck-wrap"' in text:
            print(f"  {p.name}: already migrated, skipped")
            continue
        out = p.with_name(p.stem + "-fixedcanvas" + p.suffix)
        out.write_text(migrate(text), encoding="utf-8")
        print(f"  {p.name}  ->  {out.name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: migrate_deck.py file.html [file2.html ...]")
    main(sys.argv[1:])
