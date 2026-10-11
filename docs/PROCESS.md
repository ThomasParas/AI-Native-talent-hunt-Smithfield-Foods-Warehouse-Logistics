# PROCESS log — Smithfield warehousing & logistics sourcing

Solo entry, AI-Native Talent Hunt (SF), 2026-10-11. Deadline 15:30 PDT.
Human: Thomas Paras (decisions). AI: Claude Code (Opus 5.5) for research, analysis, drafting, build/packaging.
All times PDT.

## 13:56 — Kickoff
- Read the brief (pasted) + `warehouse_project.docx` (site data for DC1 and Plant 1). Docx kept out of the public repo (gitignored) since it is partner-provided material.
- Checked clock: 1h34m to deadline. Plan: research 15 min → options discussion → build 45 min → verify/package 15 min.
- Launched 3 parallel research sub-agents (web): (1) Smithfield/WH Group existing automation + new flagship plant, to steer away from what they already have; (2) Chinese high-reach pallet AGV suppliers vs. 10.5 m / ~1 t / -18 °C / cross-zone / North-America requirements; (3) Chinese AS/RS + cold-store suppliers for a greenfield plant, incl. any Shuanghui (WH Group China) references.
- No partner MCP/API exists for Smithfield/WH Group, so public sources only.

## 13:58 — First read of the site data (AI analysis, to be verified in the build)
- DC1: Supplier A does *horizontal-only* moves (dock staging → aisle P&D) in the chilled zone; reach trucks still do every putaway. So the AGV removes only the cheapest leg of the move — root cause of the 3.9-yr payback, not just traffic/WMS issues.
- DC1 fleet math: 10 AGVs × 4.5 pal/h = 45 pal/h vs chilled inbound 36 pal/h → ~80 % utilisation even before any freezer/outbound scope.
- Plant 1 inconsistency: 7 AGVs × 21 pal/h/unit = 147 pal/h vs demand 400 pal/day ÷ 16.5 h ≈ 24 pal/h (~16 % utilisation). 21 pal/h/unit over a 288.6 m route implies ≥3.4 m/s average even with zero pick/drop time (5.2 m/s with 60 s handling) — implausible for a laden forklift AGV. Either 21 pal/h is the *fleet* rate (then capacity ≈ 346 pal/day < 400 demand) or the figure is wrong. Flag as "needs time study"; do not build ROI on it.

## 13:59 — Partner research back (sub-agent 1, web; sources in docs/research/partner.md)
- Smithfield already runs a fully automated cold DC: Olathe, KS, built/operated with Lineage (18 AS/RS cranes, 62k pallet positions, opened 2022). → Do NOT pitch "an automated cold DC" generically; the brief's 4 DCs to upgrade are plausibly the other DCs (10-K lists 5 DCs: IN, KS, MD, NE, NC; one 3PL-operated).
- 10-K FY2025: 38 US processing facilities, 5 DCs (brief says 36 + 4 — scope is a subset; we use the brief's numbers).
- New flagship plant = Sioux Falls, SD (announced 2026-02-16, up to $1.3B, ~1.1M sq ft, Epstein design-build, production end-2028). No public warehouse/cold-store design → the design window is open, matches the brief.
- Messaging: Smithfield frames automation as *redeploying* labour, safety, higher-skill roles — we adopt that framing.

## 14:03 — Supplier research back (sub-agents 2 & 3; notes in docs/research/)
- Key AI finding: no Chinese supplier *publicly verifies* all DC gates (≥1,134 kg at 10.5 m + -18 °C + cross-zone + UL 3100/B56.5). Closest mobile: VisionNav VNR20 (11.2 m mast, US entity; residual & cold unverified) and Multiway R-series (-30 °C + temp-switching claim, but 9.5 m / 750 kg at height).
- Storage-layer candidates for the greenfield: Inform (SSE 603066; -25 °C pallet four-way shuttle, stacker cranes, AGV/RGV, Thailand plant for US market) and BZKJ (turnkey -25 °C poultry store).
- Compliance red flag surfaced: Hikrobot is a Hikvision subsidiary (US Entity List / FCC Covered List) → excluded on governance grounds.
- Shuanghui (WH Group China) Mianyang -18 °C high-bay store used imported (likely European) cranes — no Chinese reference inside the group.
- Built tool/criteria.yaml (6 knock-out gates per scenario + 15 weighted criteria, evidence multipliers verified 1.0 / claimed 0.7 / unverified 0) and tool/score.py (JSON + live-formula XLSX).

## 14:05 — Decision (Thomas)
- Presented 6 options (A-expand, VisionNav-only, Multiway-only, Inform-only, move/store split, non-Chinese benchmark) with criteria: gate fit, payback <3 yr, single-supplier preference, evidence strength, US deployability risk. Two finalists pitched with risks.
- **Thomas chose O5**: VisionNav = single mobile-robot layer for all 41 sites + new plant; Inform = automated storage layer for the new plant; neutral WES/VDA 5050 integration layer; Multiway as qualified second source for plants. Path to single-supplier (mobile) kept via witnessed-test gate.
- Score Supplier A + VisionNav + Multiway + Inform (3 extra, brief minimum is 2).

## 14:07 — Scoring + payback model run (tool/score.py, tool/payback.py)
- Risk-adjusted scores (/100): Supplier A 14.6 (FAIL all scenarios), VisionNav 34.3, Multiway 29.8 (FAIL at DCs on load-at-height), Inform 35.4. Scores look low by design: unverified = 0 and claimed = ×0.7, so the gap to 100 is the RFQ work list.
- DC1 end-to-end payback (17 zone-dedicated high-reach AGVs, 122 moves/h): base 2.73 yrs; sensitivity 2.2–3.4 yrs. Break-even landed price ≈ $210k/AGV for <3 yrs → becomes a negotiation ceiling.
- Supplier A back-solve: horizontal-only chilled scope replaces ~1.8 positions (~$294k/yr) → 3.9-yr payback implies ~$1.15M all-in. Even at 6.2 pal/h the savings pool is capped → structural, not operational.
- Plant 1: demand 24 pal/h vs stated 147 pal/h capacity (16 % util.) → ~4 units suffice; redeploy 3 units.

## 14:08–14:12 — Build (AI drafting, human-directed architecture)
- Rendered both PDFs from data (HTML → headless Chromium) via `build.sh`; the numbers in the prose are pulled from `scores.json` / `payback.json`, so text and model cannot drift.
- Design calls made while drafting: (1) cross-zone requirement solved by *process design* (zone-dedicated vehicles + airlock conveyors) instead of trusting unproven vehicle claims; (2) dock-side sort of mixed chilled/frozen trucks; (3) new plant at -25 °C / ~24 m crane AS/RS, ≈3.5× density vs 10.5 m AGV racking (indicative), with AGV-only design kept as fallback; (4) Smithfield owns the control layer (WES + VDA 5050) so two suppliers still run as one system.
- Added a "how we sourced" paragraph (16-supplier long list → desk screen → shortlist → RFQ/FAT/pilot) after re-reading the brief ("determine how to source alternative suppliers").
- Self-caught error: Plant 1 pallets are 1,000–1,500 kg, so the PLANT gate was raised from 1,134 kg to 1,500 kg; new-plant design load stays 1.5 t. Gate outcomes unchanged (were already UNVERIFIED for residual capacity).
- Package: `package.sh` → `dist/Smithfield_logistics_package.zip` (2 PDFs + XLSX + README + tool source + research notes + this log). Fresh-unzip test: unzipped into a clean scratch dir, ran `./build.sh` per README → identical payback output. Secrets scan of repo, history and zip: clean (no keys used in this project).
- Launched an independent "skeptical judge" sub-agent to review both PDFs against the brief and recompute numbers.
