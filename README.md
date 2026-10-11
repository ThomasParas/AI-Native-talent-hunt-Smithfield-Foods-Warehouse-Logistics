# Smithfield Foods — Warehousing & Logistics Sourcing Package

Answer to the brief: **Supplier A cannot meet the network's needs** (it fails 4 of 7 knock-out gates in every scenario), and **no single supplier can cover every scenario on current evidence**.
Recommended combination:
- **VisionNav** is the single mobile-robot supplier for all 36 plants, 4 DCs and the new plant's horizontal flows. Award depends on a witnessed test.
- **Inform** supplies the new plant's −25 °C high-bay storage.
- A **supplier-neutral control layer owned by Smithfield** (WES + VDA 5050) ties them together.
- **Multiway** is a qualified second source for the 8.5 m plants.

## Deliverables (at the root of this zip)
| File | What it is |
|---|---|
| `supplier_evaluation_criteria.pdf` | Reusable evaluation tool with 7 knock-out gates per scenario and 15 weighted criteria across technical, commercial and risk. Each data point carries an evidence level (verified / claimed / unverified). Applied to Supplier A (unverified where the brief is silent), VisionNav, Multiway and Inform, with sources. |
| `logistics_solution.pdf` | Recommended suppliers and solutions for the retrofits and the new plant, why a single supplier is not feasible, how the suppliers combine, the DC1 payback model, the new-plant design basis and trade-offs, risks, and the roadmap. |
| `supplier_scorecard.xlsx` | The same scorecard with live formulas. Change a score or evidence level and the totals recalculate. |
| `tool/` | Source of the tool: `criteria.yaml` (gates, weights, scales), `suppliers/*.yaml` (one file per supplier), `score.py`, `payback.py`, renderers |
| `docs/` | `PROCESS.md` (timestamped decision and AI-usage log), `research/` (source notes with URLs) |

## Re-run the tool (for example, to score a new supplier)
Requires [uv](https://docs.astral.sh/uv/) and Playwright's Chromium (`uvx playwright install chromium` if it is missing).
1. Copy `tool/suppliers/2_visionnav.yaml` to `tool/suppliers/5_newsupplier.yaml` and edit the gates and scores. Each value needs an `evidence` level of `verified`, `claimed` or `unverified`.
2. From the folder that contains this README, run:

```bash
./build.sh
```

3. The regenerated PDFs, the XLSX and the `scores.json` / `payback.json` files appear in `build/`.

To model another site's payback, edit the `BASE` inputs in `tool/payback.py` (moves/h, chilled share, labour rate, AGV price).

## Honesty notes
- Supplier specs come from public sources (official pages first). Anything not published is scored 0 and listed as a gap. Totals are therefore conservative by design.
- The payback inputs (labour cost, AGV price, cycle times) are explicit assumptions, not quotes. The DC1 base case is ≈3.0 years, right at the <3-year standard, so the plan turns price and pilot throughput into award conditions. Plant payback is modelled by archetype.
- The research was AI-assisted (Claude Code with web-research sub-agents). The decisions were human (see `docs/PROCESS.md`).
