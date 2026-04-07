from vtt_polisher.llm import parse_corrections_from_response

GOOD_RESPONSE = '''CORRECTIONS = [
{"start": "00:00:01.306", "end": "00:00:07.736", "original": "499 DSL: Hello.", "suggested": "Hello.", "reason": "Removed speaker label."}
]'''

EMPTY_RESPONSE = "CORRECTIONS = [\n]"

MALFORMED_RESPONSE = "Sorry, I could not process this."

def test_parse_good_response():
    corrections = parse_corrections_from_response(GOOD_RESPONSE)
    assert len(corrections) == 1
    assert corrections[0]["start"] == "00:00:01.306"
    assert corrections[0]["suggested"] == "Hello."

def test_parse_empty_response():
    corrections = parse_corrections_from_response(EMPTY_RESPONSE)
    assert corrections == []

def test_parse_malformed_response_returns_empty():
    corrections = parse_corrections_from_response(MALFORMED_RESPONSE)
    assert corrections == []
