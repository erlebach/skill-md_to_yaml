#!/bin/bash
set -euo pipefail

YAML_FILES=(
	tests/fixtures/aria_compliance_v2.yaml
	tests/fixtures/aria_compliance_v3.yaml
	tests/fixtures/aria_compliance.yaml
	tests/fixtures/deck_metadata_minimal.yaml
	# invalid_missing_alt.yaml and invalid_unknown_field.yaml are negative-test
	# fixtures: they MUST fail validation, so they are excluded here.
	tests/fixtures/layout_test.yaml
	tests/fixtures/minimal_deck.yaml
	tests/fixtures/real_clustering_ch8_tutorial.yaml
	tests/fixtures/real_density_clustering.yaml
	tests/fixtures/real_prototype_clustering_tutorial.yaml
	tests/fixtures/real_quantum_transformers_impl.yaml
	tests/fixtures/real_quixer_implementation.yaml
	tests/fixtures/rich_code.yaml
	tests/fixtures/rich_math.yaml
	tests/fixtures/rich_mixed.yaml
	tests/fixtures/rich_table.yaml
	tests/fixtures/skill_output_sample.yaml
	tests/fixtures/two_column_variants.yaml
	tests/fixtures/valid_deck.yaml
)

for yaml_file in "${YAML_FILES[@]}"; do
	html_file="$(basename "${yaml_file%.yaml}.html")"
	echo "Compiling $yaml_file → $html_file"
	PYTHONPATH=.claude/skills/md_to_yaml uv run python -m compiler "$yaml_file" --embed-images "$html_file"
done

echo "✓ All files compiled successfully"
