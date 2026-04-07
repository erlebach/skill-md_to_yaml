import re
from typing import Optional

_TS_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})")
_ARROW_RE = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}\.\d{3})")


def ts_to_seconds(ts: str) -> float:
    m = _TS_RE.match(ts)
    h, mn, s, ms = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return h * 3600 + mn * 60 + s + ms / 1000.0


def parse_vtt(text: str) -> list[dict]:
    """Parse WebVTT text into a list of cue dicts."""
    blocks = re.split(r"\n[ \t]*\n", text.strip())
    cues = []
    for block in blocks:
        lines = [l for l in block.splitlines() if l.strip()]
        if not lines or lines[0].strip() == "WEBVTT":
            continue

        cue_id: Optional[str] = None
        idx = 0

        # optional numeric or string cue id
        if idx < len(lines) and "-->" not in lines[idx]:
            cue_id = lines[idx].strip()
            idx += 1

        if idx >= len(lines) or "-->" not in lines[idx]:
            continue

        m = _ARROW_RE.match(lines[idx].strip())
        if not m:
            continue
        start, end = m.group(1), m.group(2)
        idx += 1

        text_body = "\n".join(lines[idx:])
        cues.append({
            "cue_id": cue_id,
            "start": start,
            "end": end,
            "start_sec": ts_to_seconds(start),
            "text": text_body,
        })
    return cues
