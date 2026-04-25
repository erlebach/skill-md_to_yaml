"""Crop logic and captions.yaml read/write."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
from PIL import Image

CAPTIONS_FILENAME = "captions.yaml"
CROPPED_SUFFIX = ".cropped"
JPEG_EXTS = {".jpg", ".jpeg"}
PNG_EXTS = {".png"}


@dataclass(frozen=True)
class CropRect:
    x: int
    y: int
    w: int
    h: int

    def as_box(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def to_dict(self) -> dict[str, int]:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h}


def normalize_ext(ext: str) -> str:
    """Lowercase + collapse .jpeg → .jpg for the derived file name."""
    e = ext.lower()
    if e == ".jpeg":
        return ".jpg"
    return e


def cropped_path(source: Path) -> Path:
    """foo.PNG -> foo.cropped.png, foo.jpeg -> foo.cropped.jpg."""
    ext = normalize_ext(source.suffix)
    return source.with_name(source.stem + CROPPED_SUFFIX + ext)


def save_kwargs_for(ext: str) -> tuple[str, dict]:
    e = ext.lower()
    if e in PNG_EXTS:
        return ("PNG", {"optimize": True})
    if e in JPEG_EXTS or e == ".jpg":
        return ("JPEG", {"quality": 95, "subsampling": 0})
    raise ValueError(f"Unsupported image extension: {ext}")


def perform_crop(source: Path, rect: CropRect) -> Path:
    """Open source, crop, write <stem>.cropped.<ext> next to it. Returns cropped path."""
    if not source.exists():
        raise FileNotFoundError(source)
    out = cropped_path(source)
    with Image.open(source) as im:
        sw, sh = im.size
        if not _rect_inside(rect, sw, sh):
            raise ValueError(
                f"Crop rect {rect.to_dict()} out of bounds for image {sw}x{sh}"
            )
        cropped = im.crop(rect.as_box())
        fmt, kw = save_kwargs_for(out.suffix)
        if fmt == "JPEG" and cropped.mode in ("RGBA", "P"):
            cropped = cropped.convert("RGB")
        cropped.save(out, fmt, **kw)
    return out


def _rect_inside(r: CropRect, w: int, h: int) -> bool:
    return (
        r.x >= 0
        and r.y >= 0
        and r.w > 0
        and r.h > 0
        and r.x + r.w <= w
        and r.y + r.h <= h
    )


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as im:
        return im.size


# --- captions.yaml -----------------------------------------------------------


def captions_path(figures_dir: Path) -> Path:
    return figures_dir / CAPTIONS_FILENAME


def load_captions(figures_dir: Path) -> dict:
    p = captions_path(figures_dir)
    if not p.exists():
        return {"images": []}
    with p.open() as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("images", [])
    return data


def save_captions(figures_dir: Path, data: dict) -> None:
    p = captions_path(figures_dir)
    with p.open("w") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def find_entry(data: dict, filename: str) -> dict | None:
    for entry in data.get("images", []):
        if entry.get("file") == filename:
            return entry
    return None


def upsert_crop(
    figures_dir: Path,
    source_filename: str,
    rect: CropRect,
    source_size: tuple[int, int],
) -> dict:
    """Update captions.yaml entry for source_filename with crop metadata.

    Returns the updated entry.
    """
    data = load_captions(figures_dir)
    entry = find_entry(data, source_filename)
    if entry is None:
        entry = {"file": source_filename, "caption": "", "alt_text": ""}
        data["images"].append(entry)
    sw, sh = source_size
    entry["crop"] = {
        "source_size": {"w": sw, "h": sh},
        "rect": rect.to_dict(),
        "cropped_file": cropped_path(Path(source_filename)).name,
    }
    save_captions(figures_dir, data)
    return entry


def get_existing_crop(figures_dir: Path, source_filename: str) -> CropRect | None:
    data = load_captions(figures_dir)
    entry = find_entry(data, source_filename)
    if not entry:
        return None
    crop = entry.get("crop")
    if not crop or "rect" not in crop:
        return None
    r = crop["rect"]
    return CropRect(int(r["x"]), int(r["y"]), int(r["w"]), int(r["h"]))


def remove_crop(figures_dir: Path, source_filename: str) -> bool:
    """Delete the crop block (and the cropped file). Returns True if anything changed."""
    data = load_captions(figures_dir)
    entry = find_entry(data, source_filename)
    changed = False
    if entry and "crop" in entry:
        cropped_name = entry["crop"].get("cropped_file")
        del entry["crop"]
        save_captions(figures_dir, data)
        changed = True
        if cropped_name:
            cf = figures_dir / cropped_name
            if cf.exists():
                cf.unlink()
    return changed
