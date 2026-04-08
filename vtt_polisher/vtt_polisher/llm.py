"""
LLM backend abstraction for vtt_polisher.

Supported backends
------------------
anthropic
    Uses the Anthropic Python SDK (``anthropic`` package).  Requires the
    ``ANTHROPIC_API_KEY`` environment variable.  The model string must be a
    valid Anthropic model ID (e.g. ``claude-sonnet-4-6``).

ollama
    Calls Ollama's **native** ``/api/chat`` endpoint directly via ``httpx``
    rather than the OpenAI-compatible ``/v1/chat/completions`` endpoint.
    The native endpoint is used because it supports Ollama-specific parameters
    (``keep_alive``, ``think``, ``options.repeat_penalty``, etc.) that the
    OpenAI-compatible shim silently ignores.

Ollama streaming
----------------
Streaming is enabled by default (``stream=True`` in the request body).
Streaming serves two purposes:

1. Tokens are printed to stderr in real time so the user can see progress
   and detect runaway generation immediately.
2. The code can abort as soon as a complete ``CORRECTIONS = [...]`` block
   is detected in the accumulated output, avoiding the repetition loops that
   local models sometimes enter after producing a valid answer.

When streaming is disabled (``stream=False``), Ollama returns a single JSON
object with the complete response.  The code reads it with a plain ``POST``
and extracts ``message.content`` directly — no line-by-line iteration.

Repetition-loop mitigation
---------------------------
Local models occasionally repeat their answer verbatim in a loop.  Three
complementary safeguards are applied:

- ``repeat_penalty: 1.2`` — sampler-level penalty applied by Ollama for each
  token that already appears in the context.  This is the most general fix and
  works regardless of output format.
- ``num_predict: 2048`` — hard cap on output tokens.  Provides a backstop if
  ``repeat_penalty`` is insufficient.
- Early-exit on first complete ``CORRECTIONS`` block (streaming only) —
  format-specific but immediate; closes the connection as soon as a valid
  answer is in hand.

keep_alive
----------
Each ``/api/chat`` request carries ``keep_alive: "30m"``, which tells Ollama
to keep the model loaded for 30 minutes of idle time after the request
completes.  This is a native Ollama parameter and is reliably honoured on the
``/api/chat`` endpoint.  (It is silently ignored on the OpenAI-compatible
endpoint, which is one reason we don't use that endpoint.)

Call ``stop_ollama_model()`` when done to unload the model immediately instead
of waiting for the idle timer.  Call ``set_ollama_keep_alive()`` to extend the
timer mid-run if needed.
"""

import json
import re
import sys
import anthropic
import httpx
from vtt_polisher.prompt import SYSTEM_PROMPT, render_user_message

_BLOCK_RE = re.compile(r"CORRECTIONS\s*=\s*\[(.*?)\]", re.DOTALL)
_OBJ_RE = re.compile(r"\{[^{}]+\}", re.DOTALL)


def parse_corrections_from_response(text: str) -> list[dict]:
    """Extract correction dicts from the raw LLM response text.

    Expects the model to output a block of the form::

        CORRECTIONS = [
          {"start": ..., "end": ..., "original": ..., "suggested": ..., "reason": ...},
          ...
        ]

    Objects that fail JSON parsing are silently skipped so that a single
    malformed entry does not discard the rest.
    """
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


def make_ollama_client(ollama_url: str) -> httpx.Client:
    """Create a persistent httpx client pointed at an Ollama server.

    A single client is created once and reused across all chunks so that
    the model is not unloaded and reloaded between requests (which would
    add significant latency and cause the 'Stopping...' state in
    ``ollama ps``).

    The 600-second timeout is intentionally generous: a 26B MoE model
    processing a dense 10-cue chunk can take 2–3 minutes.
    """
    return httpx.Client(base_url=ollama_url, timeout=600.0)


def call_llm(
    chunk: dict,
    # model and backend are fallbacks; always overridden by CLI args in practice
    model: str = "claude-sonnet-4-6",
    backend: str = "anthropic",
    ollama_url: str = "http://localhost:11434",
    client: httpx.Client | None = None,
    stream: bool = True,
) -> list[dict]:
    """Send one VTT chunk to the configured LLM and return parsed corrections.

    Parameters
    ----------
    chunk:
        A chunk dict produced by ``chunk_by_time`` or ``chunk_by_count``,
        containing keys ``chunk_index``, ``chunk_start``, ``chunk_end``,
        and ``cues``.
    model:
        Model identifier.  For ``anthropic`` backend: an Anthropic model ID.
        For ``ollama`` backend: the tag shown in ``ollama list``
        (e.g. ``gemma4:26b``).
    backend:
        ``"anthropic"`` or ``"ollama"``.
    ollama_url:
        Base URL of the Ollama server (default: ``http://localhost:11434``).
        Ignored when ``backend="anthropic"``.
    client:
        A pre-created ``httpx.Client`` from ``make_ollama_client()``.  If
        ``None`` a new client is created for this call only (not recommended
        for batch processing — create one client and pass it to every call).
    stream:
        Ollama only.  When ``True`` (default), tokens are streamed and printed
        to stderr in real time, and generation stops as soon as a complete
        ``CORRECTIONS`` block is detected.  When ``False``, Ollama waits until
        generation is complete before returning the full response — simpler but
        gives no progress feedback and cannot early-exit on repetition loops.
    """
    user_message = render_user_message(chunk)

    if backend == "ollama":
        if client is None:
            client = make_ollama_client(ollama_url)

        request_body = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            # Disable internal chain-of-thought for models that support it
            # (e.g. gemma4). Reduces latency significantly.
            "think": False,
            # Keep the model loaded for 30 minutes of idle time after this
            # request completes.  Prevents Ollama from unloading between chunks.
            "keep_alive": "30m",
            "stream": stream,
            "options": {
                "temperature": 0,
                # Hard cap on output tokens — backstop against infinite loops.
                "num_predict": 2048,
                # Sampler-level repetition penalty.  Values above 1.0 reduce the
                # probability of tokens that already appear in the context.
                # 1.2 is a mild but effective deterrent against the repetition
                # loops that local models sometimes enter after producing a
                # valid answer.
                "repeat_penalty": 1.2,
            },
        }

        if stream:
            parts = []
            corrections_done = False
            with client.stream("POST", "/api/chat", json=request_body) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    obj = json.loads(line)
                    token = obj.get("message", {}).get("content", "")
                    if token:
                        parts.append(token)
                        print(token, end="", file=sys.stderr, flush=True)
                        # Early exit: stop reading as soon as a complete
                        # CORRECTIONS block has arrived.  This prevents the
                        # connection from staying open during a repetition loop.
                        if not corrections_done:
                            if _BLOCK_RE.search("".join(parts)):
                                corrections_done = True
                                break
                    if obj.get("done"):
                        break
            print(file=sys.stderr)
            raw = "".join(parts)
        else:
            # Non-streaming: Ollama returns a single JSON object.
            response = client.post("/api/chat", json=request_body)
            response.raise_for_status()
            raw = response.json()["message"]["content"]

    else:
        api_client = anthropic.Anthropic()
        message = api_client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = message.content[0].text

    return parse_corrections_from_response(raw)


def stop_ollama_model(model: str, client: httpx.Client) -> None:
    """Unload a model from Ollama immediately.

    Equivalent to ``ollama stop <model>`` on the command line.
    Uses ``keep_alive: 0`` on the ``/api/generate`` endpoint, which tells
    Ollama to release the model from GPU/RAM without waiting for the idle timer.
    """
    client.post("/api/generate", json={"model": model, "keep_alive": 0})


def set_ollama_keep_alive(model: str, client: httpx.Client, keep_alive: str) -> None:
    """Extend the keep_alive timer for an already-loaded model.

    Useful when processing is taking longer than the original keep_alive window.
    The timer resets from the moment this call completes.

    Parameters
    ----------
    keep_alive:
        Duration string accepted by Ollama, e.g. ``"30m"``, ``"2h"``, ``"1h30m"``.
    """
    client.post("/api/generate", json={"model": model, "keep_alive": keep_alive})
