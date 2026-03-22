---
phase: 04
plan: 01
status: complete
started: 2026-03-22
completed: 2026-03-22
---

## Summary

Created the `/md_to_yaml` Claude Code skill file and deduplicated layout rules document for LLM consumption.

## What Was Built

1. **layout_rules_llm.md** (285 lines) — Extracted layout selection guidance from layout_rules.md, removing all rendering details (fonts, colors, CSS). Contains: foundation principles, 12 layout usage rules, decision tree, content-to-layout mapping, variety rules, and structure guidance.

2. **SKILL.md** (212 lines, at `~/.claude/skills/md_to_yaml/`) — Complete skill instructions for YAML DSL generation covering: source detection, flavor selection, layout planning, YAML generation with few-shot examples, validation with retry loop (3 attempts), layout variety checking, and HTML compilation.

## Key Files

### key-files.created
- `/Users/erlebach/.claude/skills/md_to_yaml/SKILL.md`
- `layout_rules_llm.md`

## Deviations

- SKILL.md is outside the git repo (at `~/.claude/skills/`) so it was not included in the git commit. This is expected — Claude Code skills live in the user's home directory.

## Self-Check: PASSED
- layout_rules_llm.md: 285 lines, 0 rendering details, all 12 layouts present
- SKILL.md: 212 lines, contains parse_deck_file, python3 -m compiler, layout_rules_llm, accessibility-core, retry loop
