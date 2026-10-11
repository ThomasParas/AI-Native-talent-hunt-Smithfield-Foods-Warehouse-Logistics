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
- Added a "how we sourced" paragraph (18-supplier long list → desk screen → shortlist → RFQ/FAT/pilot) after re-reading the brief ("determine how to source alternative suppliers").
- Self-caught error: Plant 1 pallets are 1,000–1,500 kg, so the PLANT gate was raised from 1,134 kg to 1,500 kg; new-plant design load stays 1.5 t. Gate outcomes unchanged (were already UNVERIFIED for residual capacity).
- Package: `package.sh` → `dist/Smithfield_logistics_package.zip` (2 PDFs + XLSX + README + tool source + research notes + this log). Fresh-unzip test: unzipped into a clean scratch dir, ran `./build.sh` per README → identical payback output. Secrets scan of repo, history and zip: clean (no keys used in this project).
- Launched an independent "skeptical judge" sub-agent to review both PDFs against the brief and recompute numbers.

## 14:14 — Verification caught an XLSX bug
- Inspecting `supplier_scorecard.xlsx` showed data rows shifted by one (openpyxl `ws.cell()` lookups created cells before `append`), so formula totals summed blanks. Fixed with `get_column_letter`; recalculated the workbook with an independent formula engine (`formulas` lib): totals 14.62 / 34.30 / 29.76 / 35.36 = identical to score.py.

## 14:16–14:19 — Applied the skeptical-judge review (12 findings, all addressed)
- **Numbers got worse and we said so.** Costing the new dock-sort step (2.4 FTE) moved DC1 payback from 2.73 to **3.02 yrs** (2.73 if the sort is absorbed into the existing dock-to-staging move). Rather than tune assumptions, the plan now turns the model into **award gates**: DDP ≤ $184k/AGV and ≥ 9.2 pal/h at height proven in pilot. Added outbound-ratio sensitivity, a combined adverse case (5.45 yrs), the 6.2 pal/h observed-rate case (4.21 yrs) and a bottom-up cycle-time basis for 9 pal/h.
- **Plants (90 % of sites) now modelled** by archetype: Plant 1-type horizontal lanes 5.1 yrs (don't buy; redeploy Supplier A surplus at zero capex), freezer store 40 moves/h 3.4 yrs, 80 moves/h 2.5 yrs → qualification rule **≥ 52 moves/h**.
- Tool fixes: new **G7 brownfield-compatibility gate** (Inform now FAILs retrofits, consistent with the solution), **N/A-by-design** gate status (cross-zone handled by zone-dedicated fleets), VisionNav T1 3→2 and C1 → unverified (no price received; was circular), Multiway C1 → unverified.
- Added automation map (DC1 touches automated: ≈1/8 today → 4/8 phase 1 → 8/8 phase 2), indicative O1 vs O2 new-plant capex/footprint/envelope table (crane count corrected to ≈12–15, sized by throughput), explicit labelling of public-source facts and the Sioux Falls identification as an assumption, unified Plant 1 speed basis (one-way vs round-trip), Plant 1 ≥5 m building-height caveat, roadmap re-ordered with NRTL gate.
- Scores now: Supplier A 14.6 · VisionNav 28.7 · Multiway 25.6 · Inform 35.4 (storage role only; FAIL on retrofits).
- Declined: AI-generated imagery (Thomas asked about Nano Banana). Reason: generated pictures of equipment in a sourcing document could be mistaken for real supplier hardware; code-drawn diagrams + tables carry the evidence instead.

## 14:25 — Final verification (delivery checklist)
1. **Brief re-read vs artifacts** (scripted text check on both PDFs, NFKC-normalised): reusable tool ✓, technical + commercial + risk criteria ✓, Supplier A + 3 traceable suppliers with URLs ✓, per-supplier compliance + gaps ✓, Supplier A omissions marked UNVERIFIED ✓, retrofit + new-plant solutions ✓, single-supplier tested first ✓, combination + how combined ✓, new-plant basis + trade-offs ✓. Zip name exact; both PDFs at the zip root.
2. **Real run, repeated:** the pipeline is deterministic (no LLM calls at build time); three independent rebuilds produced identical scores/payback. README numbers match the recorded run (DC1 3.02 yrs; scores 14.6 / 28.7 / 25.6 / 35.4).
3. **Fresh-unzip test:** unzipped to a clean dir and ran `build.sh` → exit 0, identical `payback.json`, both PDFs regenerated. (An interactive `cd` into the scratch dir hung because of a local zsh hook; build.sh runs under bash and is unaffected.)
4. **Secrets:** no keys used anywhere in this project; scans of the repo, git history and zip contents are clean. `.env` is gitignored.
5. Killed the hung background shell **before** touching its directory; nothing was deleted while a job wrote to it.
6. Packaged with `package.sh`; extra uploads `dist/PROCESS.md` and `dist/repo-link.txt`.

## 14:27 — Second, substance-level red team (requested by Thomas)
- Launched a red-team sub-agent with a different brief from the first reviewer: attack the substance as a WH Group ops VP, rival consultant or cold-chain engineer would. Angles: a missed single-supplier candidate, whether VisionNav is the right pick, engineering realism (9 pal/h at 10.46 m, airlock retrofits, -25 °C), CFO questions, US-China governance, and first-2-minute judge impressions. Allowed up to 3 web spot-checks of load-bearing facts.

## 14:35 — Red-team fixes applied (10/10)
- **Single-supplier claim narrowed:** Hangcha (automated reach at MODEX 2026, US subsidiary + dealers), HELI and EP/Lingxi added to the screen as Q4 RFQ mobile-layer challengers; VisionNav claim reworded to "only shortlisted with a *published* >10.5 m mast". The two-layer conclusion rests on the storage layer, so a challenger can change the mobile-layer winner but not the architecture.
- **Labour:** savings relabelled as positions removed via attrition / avoided hires, not layoffs; labour-relations notice + retraining plan added to the Q4 roadmap.
- **Headline:** KPI now "<3.0 yrs once award gates met; base 3.02"; added lifetime view: NPV ≈$3.35M, IRR ≈27.8 % (8-yr life, battery swap yr 5, 10 % WACC, no residual).
- **Tariffs:** Section 232 robotics/industrial-machinery investigation (opened Sept 2025) added to R1 + risk table, with tariff-stack disclosure and a cap clause. Did not cite the agent's unverified claim about a June 2026 forklift 232 action.
- **Politics:** new risk row (ICTS / EO 13873, public optics of Chinese-owned company + Chinese connected robots; air-gapped fleet manager, code escrow, warm non-Chinese swap-in, government-affairs pre-brief).
- **Hikrobot rationale corrected:** Entity List restricts exports *to* listed parties; the real issue is NDAA §889 exposure for a USDA supplier + FCC Covered List.
- **Engineering:** freezer factor explained (human cold-stress breaks; AGV battery derate inside availability buffer) and the 9.2 pal/h gate must be proven inside -18 °C; DC airlock now two freezer-rated conveyors + manual bypass; contingency 20 % added to sensitivity (3.29 yrs).
- **New plant:** US-code gate (MH16.1, IBC, NFPA 13 in-rack at -25 °C, US PE stamp) + an explicit answer to the "Shuanghui used imported cranes" precedent (European crane vendor kept as benchmark bid).
- **Wording:** "zero capex" → "no new vehicle capex (relocation and re-commissioning only)"; phase-2 truck loading deferral explained.

## 14:40 — Fact spot-check of load-bearing claims (Firecrawl, official pages)
- VisionNav VNR20 mast options 8,300 / 9,200 / 10,200 / **11,200 mm** — confirmed on visionnav.com product page (verbatim).
- Inform four-way pallet shuttle **-25 °C to 45 °C, 1.0 / 1.5 / 2.0 t** — confirmed on inform-international.com (verbatim).
- Section 232 robotics & industrial machinery investigation **initiated 2 Sept 2025** — confirmed (bis.gov, Federal Register 90 FR 46382). Wording changed from "pending" to neutral + "current duty status to be confirmed by customs broker", since an outcome may have issued after spring 2026; citation added.

## 14:41 — Submission package frozen
- Final `dist/`: `Smithfield_logistics_package.zip` (2 PDFs at root + XLSX + README + tool + docs), `PROCESS.md`, `repo-link.txt`.
- AI usage summary: 6 sub-agents total (3 parallel web research, 1 consistency reviewer, 1 substance red team, plus spot-checks by the main agent); main agent built the scoring tool, payback model, renderers, packaging and verification. Human decisions: architecture choice (O5), supplier set (3 extra), declining AI imagery, applying both review rounds, scope stop at 14:41 to protect the buffer.
