# PROCESS log — Smithfield warehousing & logistics sourcing

Solo entry, AI-Native Talent Hunt (SF), 2026-10-11. Deadline 15:30 PDT.
Human: Thomas Paras (decisions). AI: Claude Code (Opus 5.5) for research, analysis, drafting, build/packaging.
All times PDT.

## 13:56 — Kickoff
- Read the brief (pasted) + `warehouse_project.docx` (site data for DC1 and Plant 1). Docx kept out of the public repo (gitignored) since it is partner-provided material.
- Checked clock: 1h34m to deadline. Plan: research 15 min → options discussion → build 45 min → verify/package 15 min.
- Launched 3 parallel research sub-agents (web): (1) Smithfield/WH Group existing automation + new flagship plant, to steer away from what they already have; (2) Chinese high-reach pallet AGV suppliers vs. 10.5 m / ~1 t / -18 °C / cross-zone / North-America requirements; (3) Chinese AS/RS + cold-store suppliers for a greenfield plant, incl. any Shuanghui (WH Group China) references.
- No partner MCP/API exists for Smithfield/WH Group, so public sources only.

## 14:00 — First read of the site data (AI analysis, to be verified in the build)
- DC1: Supplier A does *horizontal-only* moves (dock staging → aisle P&D) in the chilled zone; reach trucks still do every putaway. So the AGV removes only the cheapest leg of the move — root cause of the 3.9-yr payback, not just traffic/WMS issues.
- DC1 fleet math: 10 AGVs × 4.5 pal/h = 45 pal/h vs chilled inbound 36 pal/h → ~80 % utilisation even before any freezer/outbound scope.
- Plant 1 inconsistency: 7 AGVs × 21 pal/h/unit = 147 pal/h vs demand 400 pal/day ÷ 16.5 h ≈ 24 pal/h (~16 % utilisation). 21 pal/h/unit over a 288.6 m route implies ~3.5 m/s average — implausible for a laden forklift AGV. Either 21 pal/h is the *fleet* rate (then capacity ≈ 346 pal/day < 400 demand) or the figure is wrong. Flag as "needs time study"; do not build ROI on it.
