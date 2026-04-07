import argparse
import json
import sys
from pathlib import Path

from vtt_polisher.parser import parse_vtt
from vtt_polisher.chunker import chunk_by_time, chunk_by_count
from vtt_polisher.llm import call_llm


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
        help="Claude model ID"
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

    all_corrections = []
    for ch in chunks:
        label = f"Chunk {ch['chunk_index']:03d} ({ch['chunk_start']} → {ch['chunk_end']}, {len(ch['cues'])} cues)"
        print(f"Processing {label}...", file=sys.stderr)
        try:
            corrections = call_llm(ch, model=args.model)
        except Exception as exc:
            print(f"  ERROR: {exc}", file=sys.stderr)
            corrections = []
        print(f"  → {len(corrections)} correction(s)", file=sys.stderr)
        all_corrections.extend(corrections)

    output_path = args.output or args.input.with_suffix(".corrections.json")
    output_path.write_text(json.dumps(all_corrections, indent=2, ensure_ascii=False))
    print(f"\nWrote {len(all_corrections)} total corrections to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
