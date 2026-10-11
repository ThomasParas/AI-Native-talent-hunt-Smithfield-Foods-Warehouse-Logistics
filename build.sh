#!/usr/bin/env bash
# Rebuild every deliverable from source data. Requires uv (Python 3.13) + Playwright Chromium.
set -euo pipefail
cd "$(dirname "$0")"
RUN="uv run -q --with pyyaml --with openpyxl --with playwright python"
mkdir -p build && cp tool/style.css build/
$RUN tool/score.py build
$RUN tool/payback.py > /dev/null
$RUN tool/render_eval.py
$RUN tool/render_solution.py
$RUN tool/pdf.py build/supplier_evaluation_criteria.html build/supplier_evaluation_criteria.pdf "Supplier evaluation criteria"
$RUN tool/pdf.py build/logistics_solution.html build/logistics_solution.pdf "Logistics solution"
