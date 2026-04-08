import argparse
import json
import sys
import time
from pathlib import Path

from vtt_polisher.parser import parse_vtt
from vtt_polisher.chunker import chunk_by_time, chunk_by_count
from vtt_polisher.llm import call_llm, make_ollama_client, stop_ollama_model


def main():
    parser = argparse.ArgumentParser(
        description="Polish a Zoom WebVTT transcript using Claude."
    )
    parser.add_argument("input", type=Path, help="Path to .vtt file")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output JSON path (default: <input>.corrections.json)"
    )
    parser.add_argument(
        "--chunk-mode", choices=["time", "count"], default="time",
        help="Chunking strategy (default: time)"
    )
    parser.add_argument(
        "--chunk-size", type=int, default=480, 
        help="Seconds per chunk (time mode) or cues per chunk (count mode). Default: 480"
    )
    parser.add_argument(
        "--model", default="claude-sonnet-4-6",
        help="Model ID (default: claude-sonnet-4-6)"
    )
    parser.add_argument(
        "--backend", choices=["anthropic", "ollama"], default="anthropic",
        help="LLM backend to use (default: anthropic)"
    )
    parser.add_argument(
        "--ollama-url", default="http://localhost:11434",
        help="Ollama base URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--no-stream", action="store_true",
        help="Disable streaming for Ollama backend (no real-time token output)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse and chunk only; do not call the API"
    )
    args = parser.parse_args()

    vtt_text = args.input.read_text(encoding="utf-8", errors="replace")
    cues = parse_vtt(vtt_text)
    print(f"Parsed {len(cues)} cues from {args.input.name}", file=sys.stderr)

    if args.chunk_mode == "time":
        chunks = chunk_by_time(cues, window_seconds=args.chunk_size)
    else:
        chunks = chunk_by_count(cues, n=args.chunk_size)
    print(f"Split into {len(chunks)} chunks ({args.chunk_mode} mode, size={args.chunk_size})", file=sys.stderr)

    if args.dry_run:
        for ch in chunks:
            print(f"  Chunk {ch['chunk_index']:03d}: {ch['chunk_start']} → {ch['chunk_end']}  ({len(ch['cues'])} cues)", file=sys.stderr)
        return

    ollama_client = make_ollama_client(args.ollama_url) if args.backend == "ollama" else None

    all_corrections = []
    for ch in chunks:
        t0 = time.time()
        label = f"Chunk {ch['chunk_index']:03d} ({ch['chunk_start']} → {ch['chunk_end']}, {len(ch['cues'])} cues)"
        print(f"Processing {label}...", file=sys.stderr)
        try:
            corrections = call_llm(ch, model=args.model, backend=args.backend, ollama_url=args.ollama_url, client=ollama_client, stream=not args.no_stream)
        except Exception as exc:
            print(f"  ERROR: {exc}", file=sys.stderr)
            corrections = []
        print(f"  → {len(corrections)} correction(s)", file=sys.stderr)
        print(f"  Duration: {time.time()-t0:.1f}s", file=sys.stderr, flush=True)
        for c in corrections:
            print(json.dumps(c, ensure_ascii=False), flush=True)
        all_corrections.extend(corrections)

    if ollama_client:
        print("Unloading model...", file=sys.stderr)
        stop_ollama_model(args.model, ollama_client)

    output_path = args.output or args.input.with_suffix(".corrections.json")
    output_path.write_text(json.dumps(all_corrections, indent=2, ensure_ascii=False))
    print(f"\nWrote {len(all_corrections)} total corrections to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
