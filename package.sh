#!/usr/bin/env bash
# Build deliverables from source, then assemble dist/Smithfield_logistics_package.zip (+ extra uploads).
set -euo pipefail
cd "$(dirname "$0")"
./build.sh
STAGE=dist/stage
rm -rf dist && mkdir -p "$STAGE/tool/suppliers" "$STAGE/docs/research"
cp build/supplier_evaluation_criteria.pdf build/logistics_solution.pdf build/supplier_scorecard.xlsx README.md build.sh "$STAGE/"
cp tool/*.py tool/*.yaml tool/style.css "$STAGE/tool/"
cp tool/suppliers/*.yaml "$STAGE/tool/suppliers/"
cp docs/PROCESS.md "$STAGE/docs/" && cp docs/research/*.md "$STAGE/docs/research/"
(cd "$STAGE" && zip -qrX ../Smithfield_logistics_package.zip .)
cp docs/PROCESS.md repo-link.txt dist/
rm -rf "$STAGE"
unzip -l dist/Smithfield_logistics_package.zip
ls -la dist
