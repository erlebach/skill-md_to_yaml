"""Tiny stdlib HTTP server hosting the crop editor."""

from __future__ import annotations

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .cropper import (
    CropRect,
    get_existing_crop,
    image_size,
    perform_crop,
    read_sidecar,
    remove_crop,
    remove_sidecar,
    sidecar_path,
    upsert_crop,
    write_sidecar,
)

STATIC_DIR = Path(__file__).parent / "static"


class CropContext:
    def __init__(
        self,
        figures_dir: Path,
        source_filename: str,
        write_captions: bool = False,
    ):
        self.figures_dir = figures_dir.resolve()
        self.source_filename = source_filename
        self.source_path = self.figures_dir / source_filename
        self.write_captions = write_captions
        self.last_cropped_path: Path | None = None
        if not self.source_path.exists():
            raise FileNotFoundError(self.source_path)


def make_handler(ctx: CropContext):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return  # quiet

        # --- routing ---------------------------------------------------------
        def do_GET(self):
            url = urlparse(self.path)
            path = url.path
            if path == "/" or path == "/index.html":
                return self._serve_static("editor.html", "text/html; charset=utf-8")
            if path == "/api/state":
                return self._serve_state()
            if path == "/image":
                return self._serve_image()
            if path.startswith("/static/"):
                name = path[len("/static/") :]
                ctype, _ = mimetypes.guess_type(name)
                return self._serve_static(name, ctype or "application/octet-stream")
            self.send_error(404)

        def do_POST(self):
            url = urlparse(self.path)
            if url.path == "/api/crop":
                return self._handle_crop()
            if url.path == "/api/uncrop":
                return self._handle_uncrop()
            if url.path == "/api/closing":
                last = ctx.last_cropped_path
                if last is not None:
                    print(f"figure_crop: editor closed. Last write: {last}", flush=True)
                else:
                    print("figure_crop: editor closed. No crop was saved.", flush=True)
                return self._json(200, {"ok": True})
            self.send_error(404)

        # --- handlers --------------------------------------------------------
        def _serve_state(self):
            sw, sh = image_size(ctx.source_path)
            # Sidecar JSON is the canonical source of truth. captions.yaml is
            # only consulted as a fallback if there is no sidecar yet (e.g.,
            # editing an old deck where captions.yaml has the only metadata).
            existing = read_sidecar(ctx.source_path)
            source_of_state = "sidecar"
            if existing is None:
                existing = get_existing_crop(ctx.figures_dir, ctx.source_filename)
                source_of_state = "captions" if existing else "default"
            payload = {
                "source_filename": ctx.source_filename,
                "source_size": {"w": sw, "h": sh},
                "rect": (
                    {"x": existing.x, "y": existing.y, "w": existing.w, "h": existing.h}
                    if existing
                    else {"x": 0, "y": 0, "w": sw, "h": sh}
                ),
                "has_existing_crop": existing is not None,
                "state_source": source_of_state,
                "sidecar_path": str(sidecar_path(ctx.source_path)),
            }
            self._json(200, payload)

        def _serve_image(self):
            data = ctx.source_path.read_bytes()
            ctype, _ = mimetypes.guess_type(ctx.source_path.name)
            self.send_response(200)
            self.send_header("Content-Type", ctype or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _serve_static(self, name: str, ctype: str):
            p = STATIC_DIR / name
            if not p.exists():
                self.send_error(404)
                return
            data = p.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _handle_crop(self):
            body = self._read_json()
            try:
                rect = CropRect(
                    int(body["x"]), int(body["y"]), int(body["w"]), int(body["h"])
                )
            except (KeyError, TypeError, ValueError) as e:
                return self._json(400, {"error": f"bad rect: {e}"})
            try:
                out = perform_crop(ctx.source_path, rect)
                sw, sh = image_size(ctx.source_path)
                # Always write the sidecar JSON — it is the canonical store.
                sc = write_sidecar(ctx.source_path, rect, (sw, sh))
                entry = None
                if ctx.write_captions:
                    entry = upsert_crop(
                        ctx.figures_dir, ctx.source_filename, rect, (sw, sh)
                    )
            except (FileNotFoundError, ValueError) as e:
                return self._json(400, {"error": str(e)})
            ctx.last_cropped_path = out
            print(
                f"figure_crop: wrote {out}  "
                f"({rect.w}x{rect.h} from {sw}x{sh})",
                flush=True,
            )
            print(f"figure_crop: sidecar {sc}", flush=True)
            self._json(
                200,
                {
                    "ok": True,
                    "cropped_file": out.name,
                    "cropped_path": str(out),
                    "sidecar_path": str(sc),
                    "entry": entry,
                    "wrote_captions": ctx.write_captions,
                },
            )

        def _handle_uncrop(self):
            sidecar_changed = remove_sidecar(ctx.source_path)
            captions_changed = (
                remove_crop(ctx.figures_dir, ctx.source_filename)
                if ctx.write_captions
                else False
            )
            self._json(
                200,
                {
                    "ok": True,
                    "changed": sidecar_changed or captions_changed,
                    "sidecar_removed": sidecar_changed,
                    "captions_changed": captions_changed,
                },
            )

        # --- helpers ---------------------------------------------------------
        def _read_json(self) -> dict:
            n = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(n) if n else b"{}"
            try:
                return json.loads(raw or b"{}")
            except json.JSONDecodeError:
                return {}

        def _json(self, code: int, payload: dict):
            data = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return Handler


def serve(ctx: CropContext, host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), make_handler(ctx))
    return server
