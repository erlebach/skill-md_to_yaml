import math


def _seconds_to_ts(x: float) -> str:
    h = int(x // 3600)
    x %= 3600
    m = int(x // 60)
    x %= 60
    s = int(x)
    ms = int(round((x - s) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def chunk_by_time(cues: list[dict], window_seconds: float = 480) -> list[dict]:
    """Split cues into half-open time windows [k*w, (k+1)*w)."""
    if not cues:
        return []
    max_t = max(c["start_sec"] for c in cues)
    n = math.ceil((max_t + 0.001) / window_seconds)
    chunks = []
    for k in range(n):
        t0 = k * window_seconds
        t1 = (k + 1) * window_seconds
        members = [c for c in cues if t0 <= c["start_sec"] < t1]
        chunks.append({
            "chunk_index": k,
            "chunk_start": _seconds_to_ts(t0),
            "chunk_end": _seconds_to_ts(t1),
            "chunk_start_sec": t0,
            "chunk_end_sec": t1,
            "cues": members,
        })
    return chunks


def chunk_by_count(cues: list[dict], n: int = 10) -> list[dict]:
    """Split cues into fixed-size groups of n cues."""
    chunks = []
    for i in range(0, len(cues), n):
        group = cues[i : i + n]
        chunks.append({
            "chunk_index": i // n,
            "chunk_start": group[0]["start"],
            "chunk_end": group[-1]["end"],
            "chunk_start_sec": group[0]["start_sec"],
            "chunk_end_sec": group[-1]["start_sec"],
            "cues": group,
        })
    return chunks
