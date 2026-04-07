import json
import re
import anthropic
from vtt_polisher.prompt import SYSTEM_PROMPT, render_user_message

_BLOCK_RE = re.compile(r"CORRECTIONS\s*=\s*\[(.*?)\]", re.DOTALL)
_OBJ_RE = re.compile(r"\{[^{}]+\}", re.DOTALL)


def parse_corrections_from_response(text: str) -> list[dict]:
    m = _BLOCK_RE.search(text)
    if not m:
        return []
    block = m.group(1).strip()
    if not block:
        return []
    corrections = []
    for obj_m in _OBJ_RE.finditer(block):
        try:
            obj = json.loads(obj_m.group(0))
            corrections.append(obj)
        except json.JSONDecodeError:
            pass
    return corrections


def call_llm(chunk: dict, model: str = "claude-sonnet-4-6") -> list[dict]:
    """Send one chunk to Claude and return parsed corrections."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": render_user_message(chunk)}],
    )
    raw = message.content[0].text
    return parse_corrections_from_response(raw)
