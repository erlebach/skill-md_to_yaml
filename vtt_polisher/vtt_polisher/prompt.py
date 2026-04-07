SYSTEM_PROMPT = """\
You are an expert caption editor for academic lectures.

You will receive a chunk of WebVTT captions and a time window.

## Inclusion rule (half-open interval)
Process a cue if and only if: start >= chunk_start AND start < chunk_end.

## Your goals
- Fix spelling mistakes and obvious speech-recognition errors.
- Remove speaker label prefixes like "499 DSL:" from the suggested text.
- Preserve technical terms, proper names, math, and domain-specific jargon.
- Preserve the speaker's meaning and tone.
- Do NOT change timestamps, merge/split cues, or invent content.

## Output format
Begin with exactly: CORRECTIONS = [
Then output one JSON object per line (no trailing comma on the last item):
{"start": "<start_ts>", "end": "<end_ts>", "original": "<exact original text>", "suggested": "<corrected text>", "reason": "<short explanation>"}
End with exactly: ]

Omit cues that need no change. If all cues are acceptable, output:
CORRECTIONS = [
]
"""


def render_user_message(chunk: dict) -> str:
    lines = [
        f"Chunk: {chunk['chunk_start']} → {chunk['chunk_end']}",
        "",
    ]
    for c in chunk["cues"]:
        if c["cue_id"] is not None:
            lines.append(str(c["cue_id"]))
        lines.append(f"{c['start']} --> {c['end']}")
        lines.append(c["text"])
        lines.append("")
    return "\n".join(lines)
