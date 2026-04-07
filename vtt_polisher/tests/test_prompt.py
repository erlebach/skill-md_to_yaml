from vtt_polisher.prompt import SYSTEM_PROMPT, render_user_message

def test_system_prompt_contains_key_instructions():
    assert "CORRECTIONS = [" in SYSTEM_PROMPT

def test_render_user_message_contains_chunk_window():
    chunk = {
        "chunk_start": "00:00:00.000",
        "chunk_end": "00:08:00.000",
        "cues": [
            {
                "cue_id": "1",
                "start": "00:00:01.306",
                "end": "00:00:07.736",
                "start_sec": 1.306,
                "text": "499 DSL: Hello world.",
            }
        ],
    }
    msg = render_user_message(chunk)
    assert "00:00:00.000" in msg
    assert "00:08:00.000" in msg
    assert "00:00:01.306 --> 00:00:07.736" in msg
    assert "499 DSL: Hello world." in msg
