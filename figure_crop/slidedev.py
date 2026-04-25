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

from .cropper import (
    CropRect, cropped_path, image_size, perform_crop,
    pop_sidecar, resolve_original, write_sidecar,
)

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
  // Set to true after a crop/undo so the next version bump (our own recompile)
  // doesn't clobber the image we already swapped in.
  let _suppressNextReload = false;
  setInterval(() => {
    fetch('/__dev/version', { cache: 'no-store' })
      .then(r => r.text())
      .then(v => {
        if (_ver === null) { _ver = v; return; }
        if (v !== _ver) {
          _ver = v; // always consume the version bump
          if (_suppressNextReload) { _suppressNextReload = false; return; }
          sessionStorage.setItem('__dev_slide', mostVisibleSlideIdx());
          location.reload();
        }
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
  // Track the last image that was successfully cropped (for 'z' undo).
  let lastCropped = null; // {img, originalSrc}

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

  // Build the URL for the cropped file, derived from the original src URL.
  function croppedUrl(img, croppedFilename) {
    const u = new URL(img.dataset.originalSrc || img.src, location.href);
    const parts = u.pathname.split('/');
    parts[parts.length - 1] = croppedFilename;
    u.pathname = parts.join('/');
    u.search = '?v=' + Date.now(); // cache-bust so browser fetches fresh bytes
    return u.toString();
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
    showHint('drag to select · c to save · z to undo · Escape to cancel');
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
      showHint('drag handles to adjust · c to save · z to undo · Escape to cancel');
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

      // Scale display-pixel rect to natural image pixels.
      // If we're already viewing a cropped image, translate to original coordinates.
      const scaleX = img.naturalWidth  / img.clientWidth;
      const scaleY = img.naturalHeight / img.clientHeight;
      const offsetX = parseInt(img.dataset.cropX || '0', 10);
      const offsetY = parseInt(img.dataset.cropY || '0', 10);
      const px = Math.round(rect.x * scaleX) + offsetX;
      const py = Math.round(rect.y * scaleY) + offsetY;
      const pw = Math.round(rect.w * scaleX);
      const ph = Math.round(rect.h * scaleY);

      // Always send the original image URL so the server can locate it.
      const srcUrl = img.dataset.originalSrc || img.src;

      showHint('saving crop…');
      fetch('/__dev/crop', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({src: srcUrl, x: px, y: py, w: pw, h: ph}),
      }).then(r => r.json()).then(j => {
        if (j.error) { showHint('error: ' + j.error, 3000); return; }

        // Remember original src for future crops and undo.
        if (!img.dataset.originalSrc) img.dataset.originalSrc = img.src;

        // Store crop origin (in original image space) for next crop translation.
        img.dataset.cropX = String(px);
        img.dataset.cropY = String(py);

        // Immediately swap in the cropped image — no need to wait for reload.
        img.src = croppedUrl(img, j.cropped_file);

        lastCropped = {img, originalSrc: img.dataset.originalSrc};
        _suppressNextReload = true; // we already swapped the image; skip the recompile-triggered reload
        const histLen = j.history_len || '?';
        clearSelection();
        showHint(`crop ${histLen} saved · drag to refine · z to undo`, 4000);
      }).catch(err => showHint('fetch error: ' + err, 3000));
    }

    if (e.key === 'z') {
      if (!lastCropped) { showHint('nothing to undo', 1500); return; }
      const {img, originalSrc} = lastCropped;
      showHint('undoing crop…');
      fetch('/__dev/undo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({src: originalSrc}),
      }).then(r => r.json()).then(j => {
        if (j.error) { showHint('undo error: ' + j.error, 3000); return; }
        clearSelection();
        _suppressNextReload = true; // we already updated the image; skip the recompile-triggered reload
        if (j.history_len === 0) {
          // All crops undone — revert to original image.
          img.src = originalSrc + '?v=' + Date.now();
          img.removeAttribute('data-original-src');
          img.removeAttribute('data-crop-x');
          img.removeAttribute('data-crop-y');
          lastCropped = null;
          showHint('all crops undone', 3000);
        } else {
          // Previous crop restored — update img src (cache-bust) and crop offset.
          const pr = j.prev_rect;
          img.dataset.cropX = String(pr.x);
          img.dataset.cropY = String(pr.y);
          img.src = croppedUrl(img, j.cropped_file);
          showHint(`reverted to crop ${j.history_len}`, 3000);
        }
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

        def _resolve_src(self, body: dict):
            """Resolve a `src` URL from a POST body to a safe absolute Path.

            Returns (src_abs, error_response_dict_or_None).
            """
            src_url = body.get('src', '')
            src_path_rel = unquote(urlparse(src_url).path).lstrip('/')
            src_abs = (serve_root / src_path_rel).resolve()
            try:
                src_abs.relative_to(serve_root)
            except ValueError:
                return None, {'error': 'path outside serve root'}
            if not src_abs.is_file():
                return None, {'error': f'image not found: {src_path_rel}'}
            return resolve_original(src_abs), None

        def do_POST(self):
            endpoint = urlparse(self.path).path
            if endpoint == '/__dev/undo':
                body = self._read_json()
                src_abs, err = self._resolve_src(body)
                if err:
                    return self._json(400, err)
                if not src_abs.is_file():
                    return self._json(400, {'error': f'original not found: {src_abs.name}'})
                prev_rect = pop_sidecar(src_abs)
                cropped_name = cropped_path(src_abs).name
                if prev_rect is None:
                    # All crops undone — remove cropped file and revert YAML.
                    cp = cropped_path(src_abs)
                    if cp.exists():
                        cp.unlink()
                    print(f'slide_dev: undo → all crops removed for {src_abs.name}', flush=True)
                    self._json(200, {'ok': True, 'history_len': 0})
                    threading.Thread(
                        target=recompile,
                        args=(cropped_name, src_abs.name),
                        daemon=True,
                    ).start()
                else:
                    # Re-apply the previous crop.
                    out = perform_crop(src_abs, prev_rect)
                    # Read remaining history length.
                    sc = cropped_path(src_abs).with_suffix('.json')
                    try:
                        history_len = len(json.loads(sc.read_text()).get('history', []))
                    except Exception:
                        history_len = 1
                    print(f'slide_dev: undo → re-applied crop {history_len} for {src_abs.name}', flush=True)
                    self._json(200, {
                        'ok': True,
                        'history_len': history_len,
                        'cropped_file': out.name,
                        'prev_rect': prev_rect.to_dict(),
                    })
                    threading.Thread(
                        target=recompile,
                        args=(src_abs.name, out.name),
                        daemon=True,
                    ).start()
                return

            if endpoint != '/__dev/crop':
                self.send_error(404)
                return
            body = self._read_json()
            src_abs, err = self._resolve_src(body)
            if err:
                return self._json(400, err)
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
            try:
                history_len = len(json.loads(sc.read_text()).get('history', []))
            except Exception:
                history_len = 1
            print(f'slide_dev: cropped {src_abs.name} → {out.name}  sidecar → {sc.name}', flush=True)
            self._json(200, {'ok': True, 'cropped_file': out.name, 'history_len': history_len})
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
