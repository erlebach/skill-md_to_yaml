#!/usr/bin/env bash
# compile_to_html.sh — Compile a YAML slide deck to ADA-compliant HTML.
#
# USAGE
#   compile_to_html.sh INPUT.yaml OUTPUT.html [OPTIONS]
#
# ARGUMENTS
#   INPUT.yaml    Path to the YAML slide deck (relative to current directory or absolute)
#   OUTPUT.html   Destination HTML file (created or overwritten)
#
# OPTIONS
#   --embed-images      Inline all images as base64 data URIs (produces a fully
#                       self-contained HTML file with no external image dependencies)
#   --include-skipped   Render slides marked  skip: true  (omitted by default)
#
# EXAMPLES
#   compile_to_html.sh deck.yaml deck.html
#   compile_to_html.sh slides/talk.yaml slides/talk.html --embed-images
#   compile_to_html.sh talk.yaml talk.html --embed-images --include-skipped
#
# NOTES
#   Relative paths resolve from the directory where you run the script ($PWD).
#   The compiler lives at:
#     $HOME/src/2026/claude-code/n8n/md_to_yaml/.claude/skills/md_to_yaml
set -euo pipefail

# If the --help argument is found, print out the comments above
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  awk '/^set -/{exit} NR>1{sub(/^# ?/,""); print}' "$0"
  exit 0
fi

# Specify full path to skill folder
# SKILL_DIR="$HOME/src/2026/claude-code/n8n/md_to_yaml/.claude/skills/md_to_yaml"
SKILL_DIR="$HOME/src/2026/claude-code/n8n/md_to_yaml/standalone/skills/md_to_yaml"
export PYTHONPATH="$SKILL_DIR"
exec python3 -m compiler "$@"
