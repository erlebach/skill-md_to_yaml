from pathlib import Path
from vtt_polisher.parser import parse_vtt
from vtt_polisher.chunker import chunk_by_time, chunk_by_count

FIXTURE = Path(__file__).parent / "fixtures" / "sample.vtt"

def _cues():
    return parse_vtt(FIXTURE.read_text())

def test_chunk_by_time_covers_all_cues():
    cues = _cues()
    chunks = chunk_by_time(cues, window_seconds=480)
    all_cues = [c for ch in chunks for c in ch["cues"]]
    assert len(all_cues) == len(cues)

def test_chunk_by_time_no_overlap():
    cues = _cues()
    chunks = chunk_by_time(cues, window_seconds=480)
    seen = set()
    for ch in chunks:
        for c in ch["cues"]:
            key = c["start"]
            assert key not in seen
            seen.add(key)

def test_chunk_by_time_half_open_interval():
    cues = _cues()
    chunks = chunk_by_time(cues, window_seconds=60)
    for ch in chunks:
        t0 = ch["chunk_start_sec"]
        t1 = ch["chunk_end_sec"]
        for c in ch["cues"]:
            assert t0 <= c["start_sec"] < t1

def test_chunk_by_count():
    cues = _cues()
    chunks = chunk_by_count(cues, n=5)
    assert len(chunks) == 3  # 15 cues / 5 = 3
    assert len(chunks[0]["cues"]) == 5
    assert len(chunks[2]["cues"]) == 5

def test_chunk_by_count_last_chunk_partial():
    cues = _cues()
    chunks = chunk_by_count(cues, n=6)
    total = sum(len(ch["cues"]) for ch in chunks)
    assert total == 15
