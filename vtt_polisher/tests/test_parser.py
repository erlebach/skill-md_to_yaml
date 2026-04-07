import pytest
from pathlib import Path
from vtt_polisher.parser import parse_vtt, ts_to_seconds

FIXTURE = Path(__file__).parent / "fixtures" / "sample.vtt"

def test_ts_to_seconds():
    assert ts_to_seconds("00:01:30.500") == 90.5

def test_parse_returns_list_of_dicts():
    cues = parse_vtt(FIXTURE.read_text())
    assert len(cues) == 15

def test_first_cue_fields():
    cues = parse_vtt(FIXTURE.read_text())
    c = cues[0]
    assert c["start"] == "00:00:01.306"
    assert c["end"] == "00:00:07.736"
    assert c["cue_id"] == "1"
    assert c["start_sec"] == pytest.approx(1.306)
    assert "circle in the world" in c["text"]

def test_no_webvtt_header_in_cues():
    cues = parse_vtt(FIXTURE.read_text())
    for c in cues:
        assert "WEBVTT" not in c["text"]
