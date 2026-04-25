"""Dev server: serve compiled slide HTML with an injected crop overlay.

Inject-at-serve means the HTML on disk is never modified by the overlay.
On crop-save the YAML src is patched to the cropped filename, the deck is
recompiled, and the browser reloads at the same slide position.

Workflow
--------
  1. Drag on any image in the slide to draw a crop rectangle (orange dashes).
  2. Press **c** to save: patches YAML, recompiles, page reloads in place.
  3. Press **Escape** to cancel the current selection without saving.

Usage
-----
  uv run python -m figure_crop slide path/to/slides.yaml [--port N]
  uv run python -m figure_crop slide path/to/slides.html [--yaml src.yaml] [--port N]
"""

from __future__ import annotations

import json
import mimetypes
import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .cropper import CropRect, image_size, perform_crop, resolve_original, write_sidecar

# ---------------------------------------------------------------------------
# Overlay JS — injected at serve time, never written to disk.
# ---------------------------------------------------------------------------

_OVERLAY_JS = r"""
(function () {
  'use strict';

  // -- scroll-position restore after reload ----------------------------------
  (function restoreScroll() {
    const idx = parseInt(sessionStorage.getItem('__dev_slide') || '-1', 10);
    if (idx < 0) return;
    sessionStorage.removeItem('__dev_slide');
    requestAnimationFrame(() => {
      const s = document.querySelectorAll('section')[idx];
      if (s) s.scrollIntoView({ behavior: 'instant' });
    });
  })();

  // -- version polling -------------------------------------------------------
  function mostVisibleSlideIdx() {
    let best = -1, bestVis = -1;
    document.querySelectorAll('section').forEach((s, i) => {
      const r = s.getBoundingClientRect();
      const vis = Math.min(r.bottom, window.innerHeight) - Math.max(r.top, 0);
      if (vis > bestVis) { bestVis = vis; best = i; }
    });
    return best;
  }
  let _ver = null;
  setInterval(() => {
    fetch('/__dev/version', { cache: 'no-store' })
      .then(r => r.text())
      .then(v => {
        if (_ver === null) { _ver = v; return; }
        if (v !== _ver) { sessionStorage.setItem('__dev_slide', mostVisibleSlideIdx()); location.reload(); }
      }).catch(() => {});
  }, 1000);

  // -- styles ----------------------------------------------------------------
  const sty = document.createElement('style');
  sty.textContent = `
    .__crop-box {
      position: absolute; box-sizing: border-box;
      border: 2px solid #f90; background: rgba(255,165,0,.06);
      cursor: move; pointer-events: all;
    }
    .__crop-handle {
      position: absolute; width: 10px; height: 10px;
      background: #f90; border: 1.5px solid #000;
      box-sizing: border-box; pointer-events: all; z-index: 2;
    }
    .__crop-handle[data-dir=nw]{left:-5px;top:-5px;cursor:nwse-resize}
    .__crop-handle[data-dir=n] {left:calc(50% - 5px);top:-5px;cursor:ns-resize}
    .__crop-handle[data-dir=ne]{right:-5px;top:-5px;cursor:nesw-resize}
    .__crop-handle[data-dir=e] {right:-5px;top:calc(50% - 5px);cursor:ew-resize}
    .__crop-handle[data-dir=se]{right:-5px;bottom:-5px;cursor:nwse-resize}
    .__crop-handle[data-dir=s] {left:calc(50% - 5px);bottom:-5px;cursor:ns-resize}
    .__crop-handle[data-dir=sw]{left:-5px;bottom:-5px;cursor:nesw-resize}
    .__crop-handle[data-dir=w] {left:-5px;top:calc(50% - 5px);cursor:ew-resize}
    .__crop-hint {
      position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%);
      background: rgba(0,0,0,.78); color: #fff; padding: 6px 16px;
      border-radius: 6px; font: 13px/1.5 system-ui,sans-serif;
      pointer-events: none; z-index: 99999;
    }
  `;
  document.head.appendChild(sty);

  // -- state -----------------------------------------------------------------
  // cs.rect is always {x, y, w, h} in display pixels relative to img top-left.
  let cs = null;
  let hintEl = null;

  function showHint(msg, ttl) {
    if (hintEl) hintEl.remove();
    hintEl = document.createElement('div');
    hintEl.className = '__crop-hint';
    hintEl.textContent = msg;
    document.body.appendChild(hintEl);
    if (ttl) setTimeout(() => { if (hintEl) { hintEl.remove(); hintEl = null; } }, ttl);
  }

  function clearSelection() {
    if (cs) { cs.box.remove(); cs = null; }
    if (hintEl) { hintEl.remove(); hintEl = null; }
  }

  // -- wire images -----------------------------------------------------------
  function wireImages() {
    document.querySelectorAll('section img').forEach(img => {
      if (img.dataset.cropWired) return;
      img.dataset.cropWired = '1';
      img.style.cursor = 'crosshair';
      img.addEventListener('pointerdown', onImgDown);
    });
  }
  wireImages();
  new MutationObserver(wireImages).observe(document.body, { childList: true, subtree: true });

  // -- helpers ---------------------------------------------------------------
  function imgRel(img, cx, cy) {
    const r = img.getBoundingClientRect();
    return [cx - r.left, cy - r.top];
  }

  function clampRect(img, r) {
    const W = img.clientWidth, H = img.clientHeight;
    let {x, y, w, h} = r;
    x = Math.max(0, Math.min(x, W - 2));
    y = Math.max(0, Math.min(y, H - 2));
    w = Math.max(2, Math.min(w, W - x));
    h = Math.max(2, Math.min(h, H - y));
    return {x, y, w, h};
  }

  function renderBox() {
    const {img, rect, box} = cs;
    box.style.left   = (img.offsetLeft + rect.x) + 'px';
    box.style.top    = (img.offsetTop  + rect.y) + 'px';
    box.style.width  = rect.w + 'px';
    box.style.height = rect.h + 'px';
  }

  // -- phase 1: initial draw -------------------------------------------------
  function onImgDown(e) {
    if (e.button !== 0) return;
    e.preventDefault();
    const img = e.currentTarget;
    clearSelection();

    const wrap = img.parentElement;
    if (getComputedStyle(wrap).position === 'static') wrap.style.position = 'relative';
    const box = document.createElement('div');
    box.className = '__crop-box';
    box.style.pointerEvents = 'none'; // transparent during initial draw
    wrap.appendChild(box);

    const [x0, y0] = imgRel(img, e.clientX, e.clientY);
    cs = { img, rect: {x: x0, y: y0, w: 0, h: 0}, box, _draw: {x0, y0} };

    img.setPointerCapture(e.pointerId);
    img.addEventListener('pointermove', onImgMove);
    img.addEventListener('pointerup', onImgUp, { once: true });
    showHint('drag to select · c to save · Escape to cancel');
  }

  function onImgMove(e) {
    if (!cs || !cs._draw) return;
    const [x1, y1] = imgRel(cs.img, e.clientX, e.clientY);
    const {x0, y0} = cs._draw;
    cs.rect = clampRect(cs.img, {
      x: Math.min(x0, x1), y: Math.min(y0, y1),
      w: Math.abs(x1 - x0),  h: Math.abs(y1 - y0),
    });
    renderBox();
  }

  function onImgUp(e) {
    if (!cs) return;
    cs.img.removeEventListener('pointermove', onImgMove);
    delete cs._draw;
    cs.box.style.pointerEvents = 'all';
    if (cs.rect.w > 4 && cs.rect.h > 4) {
      attachHandles();
      showHint('drag handles to adjust · c to save · Escape to cancel');
    }
  }

  // -- phase 2: handles & move -----------------------------------------------
  function attachHandles() {
    ['nw','n','ne','e','se','s','sw','w'].forEach(dir => {
      const h = document.createElement('div');
      h.className = '__crop-handle';
      h.dataset.dir = dir;
      h.addEventListener('pointerdown', onHandleDown);
      cs.box.appendChild(h);
    });
    cs.box.addEventListener('pointerdown', onBoxDown);
  }

  function onHandleDown(e) {
    if (e.button !== 0) return;
    e.stopPropagation();
    e.preventDefault();
    const dir = e.currentTarget.dataset.dir;
    const start = {x: e.clientX, y: e.clientY, rect: {...cs.rect}};
    e.currentTarget.setPointerCapture(e.pointerId);

    function onMove(ev) {
      const dx = ev.clientX - start.x, dy = ev.clientY - start.y;
      let {x, y, w, h} = start.rect;
      if (dir.includes('n')) { y += dy; h -= dy; }
      if (dir.includes('s')) { h += dy; }
      if (dir.includes('w')) { x += dx; w -= dx; }
      if (dir.includes('e')) { w += dx; }
      cs.rect = clampRect(cs.img, {x, y, w, h});
      renderBox();
    }
    function onUp() {
      e.currentTarget.removeEventListener('pointermove', onMove);
      e.currentTarget.removeEventListener('pointerup', onUp);
    }
    e.currentTarget.addEventListener('pointermove', onMove);
    e.currentTarget.addEventListener('pointerup', onUp);
  }

  function onBoxDown(e) {
    if (e.target !== cs.box) return; // ignore handle clicks that bubble
    if (e.button !== 0) return;
    e.preventDefault();
    const start = {x: e.clientX, y: e.clientY, rect: {...cs.rect}};
    cs.box.setPointerCapture(e.pointerId);

    function onMove(ev) {
      const dx = ev.clientX - start.x, dy = ev.clientY - start.y;
      cs.rect = clampRect(cs.img, {
        x: start.rect.x + dx, y: start.rect.y + dy,
        w: start.rect.w,      h: start.rect.h,
      });
      renderBox();
    }
    function onUp() {
      cs.box.removeEventListener('pointermove', onMove);
      cs.box.removeEventListener('pointerup', onUp);
    }
    cs.box.addEventListener('pointermove', onMove);
    cs.box.addEventListener('pointerup', onUp);
  }

  // -- keyboard --------------------------------------------------------------
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const tag = document.activeElement && document.activeElement.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;

    if (e.key === 'Escape') { clearSelection(); return; }

    if (e.key === 'c') {
      if (!cs) return;
      const {img, rect} = cs;
      if (rect.w < 4 || rect.h < 4) { showHint('selection too small', 2000); return; }
      const scaleX = img.naturalWidth  / img.clientWidth;
      const scaleY = img.naturalHeight / img.clientHeight;
      const px = Math.round(rect.x * scaleX), py = Math.round(rect.y * scaleY);
      const pw = Math.round(rect.w * scaleX), ph = Math.round(rect.h * scaleY);
      showHint('saving crop…');
      fetch('/__dev/crop', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({src: img.src, x: px, y: py, w: pw, h: ph}),
      }).then(r => r.json()).then(j => {
        if (j.error) { showHint('error: ' + j.error, 3000); return; }
        clearSelection();
        showHint('saved → ' + j.cropped_file + ' · recompiling…');
      }).catch(err => showHint('fetch error: ' + err, 3000));
    }
  });
})();
"""

_OVERLAY_TAG = f'<script id="__dev-overlay">\n{_OVERLAY_JS}\n</script>'


def _inject(html: str) -> str:
    if '</body>' in html:
        return html.replace('</body>', _OVERLAY_TAG + '\n</body>', 1)
    return html + '\n' + _OVERLAY_TAG


# ---------------------------------------------------------------------------
# YAML patching
# ---------------------------------------------------------------------------

def _patch_yaml_src(yaml_path: Path, original_name: str, cropped_name: str) -> bool:
    """Replace `src: <original>` with `src: <cropped>` in the YAML file.

    Handles quoted and unquoted values. Returns True if the file was changed.
    """
    text = yaml_path.read_text(encoding='utf-8')
    # Match:  src: foo.png  /  src: "foo.png"  /  src: 'foo.png'
    pattern = r'(?m)^(\s*src:\s*["\']?)' + re.escape(original_name) + r'(["\']?\s*)$'
    new_text = re.sub(pattern,
                      lambda m: m.group(1) + cropped_name + m.group(2),
                      text)
    if new_text == text:
        return False
    yaml_path.write_text(new_text, encoding='utf-8')
    return True


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

def _find_repo_root(start: Path) -> Path | None:
    for p in [start, *start.parents]:
        if (p / 'pyproject.toml').exists():
            return p
    return None


def make_handler(
    html_path: Path,
    yaml_path: Path,
    compile_sh: Path,
    version_box: list,
    lock: threading.Lock,
):
    serve_root = (_find_repo_root(html_path) or html_path.parent).resolve()
    html_rel = '/' + html_path.resolve().relative_to(serve_root).as_posix()

    def recompile(original_name: str, cropped_name: str):
        patched = _patch_yaml_src(yaml_path, original_name, cropped_name)
        if patched:
            print(f'slide_dev: YAML patched: {original_name} → {cropped_name}', flush=True)
        else:
            print(f'slide_dev: warning — "{original_name}" not found in YAML src fields', flush=True)

        result = subprocess.run(
            ['bash', str(compile_sh), str(yaml_path), str(html_path)],
            capture_output=True,
            text=True,
            cwd=str(yaml_path.parent),
        )
        if result.returncode != 0:
            print(f'slide_dev: compile error:\n{result.stderr}', flush=True)
        else:
            print(f'slide_dev: recompiled {html_path.name}', flush=True)
        with lock:
            version_box[0] += 1

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return

        def do_GET(self):
            p = urlparse(self.path).path

            if p == '/':
                self.send_response(302)
                self.send_header('Location', html_rel)
                self.end_headers()
                return

            if p == html_rel:
                html = html_path.read_text(encoding='utf-8')
                data = _inject(html).encode('utf-8')
                self._send(200, 'text/html; charset=utf-8', data)
                return

            if p == '/__dev/version':
                with lock:
                    v = str(version_box[0])
                self._send(200, 'text/plain', v.encode())
                return

            rel = unquote(p.lstrip('/'))
            candidate = (serve_root / rel).resolve()
            try:
                candidate.relative_to(serve_root)
            except ValueError:
                self.send_error(403)
                return
            if not candidate.is_file():
                self.send_error(404)
                return
            data = candidate.read_bytes()
            ctype, _ = mimetypes.guess_type(candidate.name)
            self._send(200, ctype or 'application/octet-stream', data)

        def do_POST(self):
            if urlparse(self.path).path != '/__dev/crop':
                self.send_error(404)
                return
            body = self._read_json()
            src_url = body.get('src', '')
            src_path_rel = unquote(urlparse(src_url).path).lstrip('/')
            src_abs = (serve_root / src_path_rel).resolve()
            try:
                src_abs.relative_to(serve_root)
            except ValueError:
                return self._json(400, {'error': 'path outside serve root'})
            if not src_abs.is_file():
                return self._json(400, {'error': f'image not found: {src_path_rel}'})
            # Always crop from the original, never from a previously cropped file.
            src_abs = resolve_original(src_abs)
            if not src_abs.is_file():
                return self._json(400, {'error': f'original not found: {src_abs.name}'})
            try:
                rect = CropRect(
                    int(body['x']), int(body['y']), int(body['w']), int(body['h'])
                )
                out = perform_crop(src_abs, rect)
                sw, sh = image_size(src_abs)
                sc = write_sidecar(src_abs, rect, (sw, sh))
            except (KeyError, TypeError, ValueError, FileNotFoundError) as exc:
                return self._json(400, {'error': str(exc)})
            print(f'slide_dev: cropped {src_abs.name} → {out.name}  sidecar → {sc.name}', flush=True)
            self._json(200, {'ok': True, 'cropped_file': out.name})
            threading.Thread(
                target=recompile,
                args=(src_abs.name, out.name),
                daemon=True,
            ).start()

        def _read_json(self) -> dict:
            n = int(self.headers.get('Content-Length', '0'))
            raw = self.rfile.read(n) if n else b'{}'
            try:
                return json.loads(raw or b'{}')
            except json.JSONDecodeError:
                return {}

        def _send(self, code: int, ctype: str, data: bytes):
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(data)

        def _json(self, code: int, payload: dict):
            self._send(code, 'application/json', json.dumps(payload).encode())

    return Handler


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def serve(
    html_path: Path,
    yaml_path: Path,
    compile_sh: Path,
    host: str = '127.0.0.1',
    port: int = 0,
) -> ThreadingHTTPServer:
    version_box = [0]
    lock = threading.Lock()
    handler = make_handler(html_path, yaml_path, compile_sh, version_box, lock)
    server = ThreadingHTTPServer((host, port), handler)
    return server
