"""Render build/logistics_solution.html from build/scores.json + build/payback.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
S = json.loads((ROOT.parent / "build/scores.json").read_text())
P = json.loads((ROOT.parent / "build/payback.json").read_text())
B, A, P1, I = P["base"], P["supplier_a"], P["plant1"], P["inputs"]
NPV = P["npv"]
ADV, SA, BE, BEP, PL = P["adverse"], P["sort_absorbed"], P["breakeven_agv_pal_h"], P["breakeven_plant_moves_h"], P["plants"]
SC = {r["short"]: r for r in S["results"]}
lo = min(min(s["payback_good"], s["payback_bad"]) for s in P["sensitivity"])
hi = max(max(s["payback_good"], s["payback_bad"]) for s in P["sensitivity"])


def m(x):
    return f"${x / 1e6:.2f}M"


def k(x):
    return f"${x / 1e3:,.0f}k"


def badge(v):
    return f'<span class="b {v}">{v}</span>'


LABEL = {"agv_landed_usd": "AGV landed price (DDP incl. tariffs)", "agv_pal_h": "AGV dock-to-rack cycles/h",
         "loaded_cost_usd": "Loaded labour cost / FTE", "manual_pal_h": "Manual reach-truck productivity",
         "integration_usd": "Integration + site works", "outbound_ratio": "Outbound moves per inbound (brief gives inbound only)", "project_pct": "Project contingency (brownfield)"}


def fmt(param, v):
    if param == "outbound_ratio":
        return f"{v:g}×"
    if param == "project_pct":
        return f"{v * 100:.0f} %"
    return k(v) if "usd" in param else f"{v:g} pal/h"


sens_rows = "".join(
    f'<tr><td>{LABEL[s["param"]]}</td><td class="num">{fmt(s["param"], I[s["param"]])}</td>'
    f'<td class="num">{fmt(s["param"], s["good"])} → {s["payback_good"]} yrs</td>'
    f'<td class="num">{fmt(s["param"], s["bad"])} → {s["payback_bad"]} yrs</td></tr>' for s in P["sensitivity"])

single_rows = ""
for name, role in [("Supplier A", "—"), ("VisionNav", "mobile"), ("Multiway", "mobile"), ("Inform", "storage")]:
    g = SC[name]["gates"]
    single_rows += f"<tr><td><b>{name}</b></td><td>{role}</td>" + "".join(f"<td>{badge(g[s])}</td>" for s in ("PLANT", "DC", "NEW")) + f'<td class="num">{SC[name]["adjusted"]}</td></tr>'


def flow_svg():
    """DC1 pallet flow, today vs phase 1, drawn from data (no images)."""
    col = {"M": ("#f3e3d3", "#b54708", "Manual"), "A": ("#dbe7f3", "#5b7fa6", "Supplier A AGV (chilled only)"),
           "N": ("#1f3a5f", "#1f3a5f", "New AGV (zone-dedicated)"), "C": ("#e3f1e8", "#1e7b4f", "Airlock conveyor")}
    steps = ["Unload truck", "Dock → staging", "Staging → aisle", "Putaway ≤10.46 m", "Retrieve → lane", "Load truck"]
    rows = [("Today", ["M", "M", "A", "M", "M", "M"], ["", "", "frozen: manual", "reach truck", "reach truck", ""]),
            ("Phase 1", ["M", "M", "N", "N", "N", "M"], ["", "+ zone sort", "frozen via airlock", "AGV", "AGV", ""])]
    w, gap, x0 = 108, 12, 92
    out = ['<svg viewBox="0 0 800 222" width="100%" xmlns="http://www.w3.org/2000/svg" font-size="10.5">']
    for i, s in enumerate(steps):
        out.append(f'<text x="{x0 + i * (w + gap) + w / 2}" y="14" text-anchor="middle" fill="#5b6675" font-weight="600">{s}</text>')
    for r, (label, kinds, notes) in enumerate(rows):
        y = 24 + r * 74
        out.append(f'<text x="8" y="{y + 30}" font-weight="700" fill="#1b2430">{label}</text>')
        for i, (kd, note) in enumerate(zip(kinds, notes)):
            fill, stroke, name = col[kd]
            x = x0 + i * (w + gap)
            txt = "#fff" if kd == "N" else "#1b2430"
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="46" rx="5" fill="{fill}" stroke="{stroke}"/>')
            out.append(f'<text x="{x + w / 2}" y="{y + 20}" text-anchor="middle" fill="{txt}" font-weight="700">{name.split(" (")[0]}</text>')
            if note:
                out.append(f'<text x="{x + w / 2}" y="{y + 36}" text-anchor="middle" fill="{txt}">{note}</text>')
            if i < len(kinds) - 1:
                out.append(f'<text x="{x + w + gap / 2}" y="{y + 27}" text-anchor="middle" fill="#5b6675">›</text>')
    # airlock conveyor callout in phase 1 row
    xc = x0 + 2 * (w + gap)
    out.append(f'<rect x="{xc - 6}" y="{24 + 74 + 50}" width="{w + 12}" height="17" rx="3" fill="#e3f1e8" stroke="#1e7b4f"/>')
    out.append(f'<text x="{xc + w / 2}" y="{24 + 74 + 61}" text-anchor="middle" font-size="8.5" fill="#1e7b4f">2 airlock conveyors into -18 °C</text>')
    lx = 92
    for kd in "MANC":
        fill, stroke, name = col[kd]
        out.append(f'<rect x="{lx}" y="196" width="12" height="12" rx="2" fill="{fill}" stroke="{stroke}"/><text x="{lx + 17}" y="206" fill="#1b2430">{name}</text>')
        lx += 172
    out.append("</svg>")
    return "".join(out)


ARCH = """
<svg viewBox="0 0 760 250" width="100%" xmlns="http://www.w3.org/2000/svg" font-size="11">
 <rect x="10" y="8" width="740" height="44" rx="6" fill="#1f3a5f"/>
 <text x="380" y="27" fill="#fff" text-anchor="middle" font-weight="700">CONTROL LAYER — owned by Smithfield</text>
 <text x="380" y="43" fill="#dfe7f1" text-anchor="middle">Corporate WMS → supplier-neutral WES/orchestrator → VDA 5050 to robot fleets · WCS messages to AS/RS · one dashboard, one KPI set</text>
 <rect x="10" y="66" width="360" height="118" rx="6" fill="#eef3f9" stroke="#1f3a5f"/>
 <text x="190" y="86" text-anchor="middle" font-weight="700" fill="#1f3a5f">MOBILE LAYER — VisionNav (single fleet)</text>
 <text x="22" y="106" fill="#1b2430">• Qualifying plants: reach AGVs to 8.5 m (9.2 m mast)</text>
 <text x="22" y="123" fill="#1b2430">• 4 DCs: high-reach AGVs to 10.46 m (11.2 m mast)</text>
 <text x="22" y="140" fill="#1b2430">• New plant: end-of-line, dock, packaging supply</text>
 <text x="22" y="157" fill="#1b2430">• Zone-dedicated vehicles (chilled / frozen / ambient)</text>
 <text x="22" y="174" fill="#5b6675">Second source: Multiway (plants, 8.5 m) · Legacy: Supplier A ambient</text>
 <rect x="390" y="66" width="360" height="118" rx="6" fill="#eef6f1" stroke="#1e7b4f"/>
 <text x="570" y="86" text-anchor="middle" font-weight="700" fill="#1e7b4f">STORAGE LAYER — Inform (new plant only)</text>
 <text x="402" y="106" fill="#1b2430">• -25 °C high-bay frozen store, ~24 m, stacker cranes</text>
 <text x="402" y="123" fill="#1b2430">• 0–2 °C chilled buffer: pallet four-way shuttles (1.5 t)</text>
 <text x="402" y="140" fill="#1b2430">• Conveyors + airlock P&amp;D stations between zones</text>
 <text x="402" y="157" fill="#1b2430">• Own WCS under Smithfield WES</text>
 <text x="402" y="174" fill="#5b6675">US install/service partner contracted through Epstein</text>
 <rect x="10" y="198" width="740" height="44" rx="6" fill="#fff4e8" stroke="#b54708"/>
 <text x="380" y="217" text-anchor="middle" font-weight="700" fill="#b54708">HAND-OFF RULE: vehicles never cross temperature zones</text>
 <text x="380" y="233" text-anchor="middle" fill="#1b2430">Pallets change zone on a conveyor through a rapid-roll airlock; AGVs pick/drop at P&amp;D stations on each side → no condensation/frost risk</text>
</svg>"""

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Logistics Solution</title>
<link rel="stylesheet" href="style.css"></head><body>
<h1>Warehousing &amp; Logistics Solution</h1>
<div class="sub">Which suppliers and solutions for 36 plant retrofits, 4 DC retrofits and the new flagship plant, and why</div>
<div class="meta">Global Solution Manager, China sourcing · Smithfield Foods North America · 2026-10-11 · Companion: supplier_evaluation_criteria.pdf</div>

<h2>Executive summary</h2>
<div class="box red"><b>Can Supplier A meet the network's needs? No.</b> It fails four of seven knock-out gates in every scenario: 4 m lift against 8.5 m / 10.5 m, no 1 t pallet at height, no -18 °C, no cross-zone operation.
Its 3.9-year payback has a structural cause, not just an operational one: it automates only the horizontal leg (dock staging to aisle), while people still do every putaway with reach trucks.
On our assumptions (manual horizontal move ≈20 pal/h), that scope replaces only ≈{A["positions_replaced"]} driver positions (≈{k(A["annual_savings"])}/yr). Faster AGVs on clearer routes (4.5–5 → 6.2 pal/h) therefore cannot fix the payback; only a larger scope can.</div>
<div class="box"><b>Recommendation: a combination of two suppliers, organised as two layers with one shared control layer.</b> A single supplier for every scenario is not feasible on current evidence: no Chinese mobile-robot supplier
can deliver the high-density -25 °C storage that a world-class greenfield plant needs, and the storage specialist has no high-reach forklift line or US service network for 40 brownfield sites.
<ol>
<li><b>VisionNav as the single mobile-robot supplier</b> for every site that gets new vehicles (the 4 DCs, qualifying plants among the 36) and the new plant's horizontal flows. This keeps the company's single-supplier preference wherever vehicles are involved. Award depends on witnessed tests (1,134 kg at 10.46 m for DCs, 1,500 kg at 8.5 m for plants, at -18 °C) plus a UL 3100 plan.</li>
<li><b>Inform as the storage-system supplier for the new plant only:</b> a -25 °C high-bay frozen store with stacker cranes and a chilled four-way-shuttle buffer, designed in with Epstein (the design-build contractor).</li>
<li><b>A supplier-neutral control layer owned by Smithfield</b> (WES/orchestrator + VDA 5050), so the network runs as one system and no supplier controls the integration.</li>
</ol>
<b>The economics are at the threshold, so the award is gated on them.</b> End-to-end automation at DC1 models at ≈{B["payback_yrs"]} years (≈{SA["payback_yrs"]} if the dock sort fits into the existing dock-to-staging move) against the &lt;3-year standard.
We therefore turn the model into award conditions: a DDP price of ≤{k(B["max_landed_price_for_3yr"])} per AGV and ≥{BE:g} pal/h at height proven in the pilot.
The DC1 business case is also positive on a lifetime basis: NPV {m(NPV["npv_usd"])}, IRR {NPV["irr_pct"]} % over {NPV["life_yrs"]} years. Labour savings come from attrition and avoided hires in high-turnover cold-store roles, not layoffs. Plants qualify site by site. Only freezer stores with ≥{BEP} dock/storage moves/h clear 3 years; low-volume plants receive Supplier A's surplus units, with no new vehicle capex (relocation and re-commissioning only).
Core suppliers are just two. Multiway is a second source invited to compete for plant waves, the non-Chinese benchmark is a fallback only, and Supplier A gets no new orders.</div>
<div class="kpis">
<div class="kpi"><div class="v">3.9 → &lt;3.0 yrs</div><div class="l">DC1 payback once award gates are met; base case {B["payback_yrs"]} ({SA["payback_yrs"]} if dock sort absorbed); NPV {m(NPV["npv_usd"])}, IRR {NPV["irr_pct"]} % over {NPV["life_yrs"]} yrs</div></div>
<div class="kpi"><div class="v">{B["fleet"]} AGVs</div><div class="l">DC1 zone-dedicated fleet for {B["moves_h"]:.0f} moves/h (in + out)</div></div>
<div class="kpi"><div class="v">≤{k(B["max_landed_price_for_3yr"])} · ≥{BE:g}/h</div><div class="l">Award gates: DDP price per AGV and pilot pal/h at height for &lt;3 yrs</div></div>
<div class="kpi"><div class="v">≥{BEP} moves/h</div><div class="l">Plant qualification threshold (8.5 m freezer store, in + out)</div></div>
</div>

<h2>1. Network requirements and the sourcing result</h2>
<p>Binding retrofit constraints (from the brief and DC1 data): stack to <b>8.5 m</b> in plants and <b>10.5 m</b> in DCs (top beam 10.46 m); DC pallets 544–907 kg, max <b>1,134 kg</b>, plant pallets up to <b>1,500 kg</b> (Plant 1), 40×48 in GMA grid-base;
chilled -2 °C and frozen <b>-18 °C</b>; mixed chilled and frozen truckloads; 20 h/day. Smithfield context (public sources: Lineage 2022 press release, FY2025 10-K): Olathe, KS is already a fully automated cold DC (Lineage, 18 cranes), so this plan does not re-pitch a generic automated DC.
It targets the 4 DCs and 36 plants named in the brief. <i>Assumption:</i> the unnamed new flagship plant is the publicly announced Sioux Falls, SD facility (Smithfield press release 2026-02-16: up to $1.3B, production end-2028; Epstein design-build per ENR 2026-06-30). The design below does not depend on that identification.</p>
<p><b>How we sourced the alternatives.</b> (1) <i>Long list</i>, 18 independently traceable Chinese suppliers across two solution types. Mobile robots: VisionNav, Multiway, Hikrobot, Geek+, Quicktron, Mooe, Jaten, Standard Robots, Youibot, Hangcha, HELI, EP/Lingxi. Automated storage (AS/RS, four-way shuttle, conveyors): Inform, BZKJ, KSEC, Kede, Zikoo, Siasun.
(2) <i>Desk screen</i> against the knock-out gates using official datasheets first. Out: Geek+ (120 mm lift, −10 °C), Quicktron (3.5 m), Hikrobot (4.5 m, no cold rating, Hikvision-affiliate compliance exposure), and others with no high-reach or cold specs. <b>Hangcha</b> (automated pantograph reach truck shown at MODEX 2026, with a US subsidiary and dealer service network), <b>HELI</b> and <b>EP/Lingxi</b> publish no automated high-reach freezer specs yet. They are invited to the Q4 2026 RFQ as mobile-layer challengers. Hangcha in particular could beat VisionNav on North American service. That would change <i>who</i> wins the mobile layer, not the two-layer conclusion, which rests on the storage layer.
(3) <i>Shortlist and score</i>: VisionNav, Multiway, Inform (supplier_evaluation_criteria.pdf). (4) <i>RFQ → witnessed factory test → DC1 pilot</i> before any award (section 6).
We also checked for an in-group reference: Shuanghui's (WH Group China) Mianyang −18 °C high-bay store used imported equipment, so there is no Chinese supplier reference inside the group yet.</p>
<table><tr><th>Supplier</th><th>Role</th><th>Plants</th><th>DCs</th><th>New plant</th><th>Risk-adj. score</th></tr>{single_rows}</table>
<p class="small">CONDITIONAL = no gate failed, but at least one is claimed or unverified and must be proven before award. Hikrobot was screened out: as a Hikvision affiliate, its camera-guided vehicles create NDAA FY2019 §889 exposure for a supplier to USDA programmes, plus Hikvision is on the FCC Covered List. Non-Chinese freezer AGVs (Dematic, Muratec) are kept only as a price/spec benchmark and fallback.</p>

<h3>Single-supplier test: why one supplier cannot cover all scenarios today</h3>
<table><tr><th>Candidate as sole supplier</th><th>Retrofits (40 sites)</th><th>New plant</th><th>Verdict</th></tr>
<tr><td>Supplier A</td><td>Fails height, load, freezer, cross-zone</td><td>Would force ≤4 m storage</td><td>{badge("FAIL")}</td></tr>
<tr><td>Multiway</td><td>Plants: height OK (9.5 m, -30 °C claimed), 1,500 kg at 8.5 m unproven (R16: 750 kg at 9.5 m); DCs fail: 700–750 kg at 9.5–11 m &lt; 1,134 kg</td><td>Only with ≤8.5 m racking</td><td>{badge("FAIL")} at DCs</td></tr>
<tr><td>Inform</td><td>Requires ripping out racks in 40 operating buildings; no high-reach forklift line; no US entity</td><td>Strong (-25 °C, 1–2 t shuttles, cranes)</td><td>{badge("FAIL")} on payback / disruption</td></tr>
<tr><td>VisionNav</td><td>Only shortlisted reach AGV with a <i>published</i> &gt;10.5 m mast option (11.2 m) for existing selective racks; US entity</td><td>Possible only as a 10.5 m AGV-racked store: ≈3.5× footprint, more freezer envelope, lower throughput</td><td>{badge("CONDITIONAL")}: mobile layer only</td></tr>
</table>
<p>The closest single-supplier design (O2: VisionNav everywhere, new plant limited to 10.5 m AGV racking) was evaluated and rejected for the new plant on density, energy and throughput grounds (section 4).
We keep the single-supplier principle where it creates the most value: <b>one mobile fleet, one service contract, one spare-parts pool and one training curriculum across all 41 sites</b>, because vehicles are where the 41-site scale sits.
Inform could also run the new plant's horizontal moves with its own AGV/RGVs, making the new plant single-supplier on its own. We give those moves to VisionNav instead, so the flagship uses the same fleet, spares and skills as the other 40 sites.
Inform's scope stops at the conveyor P&amp;D stations.</p>

<h2>2. Target architecture: how the suppliers combine</h2>
{ARCH}
<table><tr><th>Interface</th><th>Rule</th><th>Owner</th></tr>
<tr><td>Physical hand-off</td><td>Inform conveyors end at pick-and-drop (P&amp;D) stations; VisionNav AGVs pick and drop only at P&amp;D. Each P&amp;D has a pallet-presence sensor and a scanner.</td><td>Inform up to the P&amp;D; VisionNav beyond</td></tr>
<tr><td>Zone crossing</td><td>Only conveyors cross temperature boundaries, through rapid-roll airlocks. AGVs are zone-dedicated, so there is no condensation or frost failure mode.</td><td>Inform (new plant); site works contractor (retrofits)</td></tr>
<tr><td>Task dispatch</td><td>WMS → WES → VDA 5050 (AGVs) / WCS telegrams (AS/RS). Status flows back to the WMS in real time, which fixes the DC1 gap where the Accellos interface is read-only.</td><td>Smithfield IT + neutral integrator</td></tr>
<tr><td>Safety</td><td>ANSI/ITSDF B56.5 risk assessment per site; NRTL field evaluation (UL 3100 / UL 583) before go-live; AGV-only aisles with marked human crossings.</td><td>Each supplier; Smithfield EHS signs off</td></tr>
<tr><td>Service</td><td>VisionNav: one North American service contract, US parts depot, ≤4 h remote / ≤24 h on-site. Inform: US installation and service partner with a resident technician at the new plant.</td><td>Contracted SLAs with liquidated damages</td></tr>
<tr><td>Cyber</td><td>Fleet managers and WCS on-premises; no mandatory cloud in China; remote access through Smithfield-controlled jump host; SBOM; IEC 62443 mapping.</td><td>Smithfield IT security</td></tr>
</table>

<h2>3. Existing facilities: retrofit solution</h2>
<h3>3.1 Distribution centers (template: DC1; 10.5 m, -2 / -18 °C)</h3>
<ol>
<li><b>Automate the whole move, not one leg.</b> High-reach AGVs move each pallet from the dock lane to its rack slot (up to 10.46 m) and from the rack to the outbound lane. This removes the reach-truck putaway that dominates labour cost. Truck unloading and loading stay manual in phase 1.</li>
<li><b>Sort mixed trucks at the dock.</b> Receiving workers already move pallets from the dock to staging; that move now drops them into separate chilled and frozen lanes. This removes the mixed-load blocker that limited Supplier A's utilisation. The model conservatively costs it as an extra {I["dock_sort_fte"]} FTE.</li>
<li><b>Zone-dedicated fleets plus airlock conveyors</b> instead of vehicles that cross zones. Frozen pallets enter the -18 °C zone on <b>two</b> freezer-rated P&amp;D conveyors (in and out, ≥60 pal/h each) through rapid-roll doors, with heated-floor and frost-heave protection, queue lanes on both sides, and the existing door kept as a manual bypass. The frozen dock sort drops pallets straight onto the conveyor infeed. If the $1.1M integration allowance proves light, the $1.6M case is in the sensitivity table (3.37 yrs). The cross-zone requirement is met by design, so it does not depend on an unproven vehicle claim.</li>
<li><b>Segregate traffic and run 5S</b> (the brief expects 4.5 → 6.2 pal/h from clear routes alone): AGV-only aisles, pallet-debris rules, marked crossings.</li>
<li><b>Integration:</b> a WES reads tasks from Accellos (now Körber) through the existing read-only access and confirms by scan, while write access or API rights are negotiated. Full read/write is a phase-2 exit criterion.</li>
<li><b>Supplier A's 10 DC1 units</b> move to ambient horizontal routes at plants, where Plant 1 shows they are stable.</li>
</ol>
<h3>Automation map: pallet touches at DC1</h3>
{flow_svg()}
<table><tr><th>Touch (each pallet)</th><th>Today</th><th>Phase 1 (this plan)</th><th>Phase 2 (2028+)</th></tr>
<tr><td>Unload truck → dock</td><td>Manual</td><td>Manual</td><td>Automated truck unloading (AGV-based; vendor capability to verify)</td></tr>
<tr><td>Dock → staging lane (+ zone sort)</td><td>Manual</td><td>Manual (sort folded into this move)</td><td>Conveyorised dock with scan-and-divert</td></tr>
<tr><td>Staging → rack aisle</td><td>Supplier A AGV (chilled only)</td><td><b>AGV</b> (chilled + frozen)</td><td>AGV</td></tr>
<tr><td>Putaway to ≤10.46 m</td><td>Manual reach truck</td><td><b>AGV</b></td><td>AGV</td></tr>
<tr><td>Retrieval → outbound lane</td><td>Manual reach truck</td><td><b>AGV</b></td><td>AGV</td></tr>
<tr><td>Load truck</td><td>Manual</td><td>Manual</td><td>Automated truck loading (deferred: trailer and load variability; business case after the phase-1 pilot)</td></tr>
<tr><td><b>Automated touches</b></td><td><b>≈1 of 8</b> (chilled inbound only)</td><td><b>4 of 8</b> (the 4 forklift-heavy touches)</td><td><b>8 of 8</b></td></tr>
</table>
<h3>3.2 DC1 payback model (tool/payback.py, all assumptions explicit)</h3>
<div class="cols"><div>
<table><tr><th>Item</th><th class="num">Base case</th></tr>
<tr><td>Dock↔rack moves/h (61 in + 61 out, 59 % chilled)</td><td class="num">{B["moves_h"]:.0f}</td></tr>
<tr><td>AGV fleet (9 pal/h each, +15 % availability buffer, zone-dedicated)</td><td class="num">{B["fleet"]}</td></tr>
<tr><td>Manual positions replaced (12 pal/h; ×0.8 in freezer)</td><td class="num">{B["manual_positions"]}</td></tr>
<tr><td>Net positions removed through attrition and avoided hires, not layoffs (2.4 FTE/position − 2.4 supervisors − 2.4 dock sort)</td><td class="num">{B["fte_saved"]}</td></tr>
<tr><td>Capex (vehicles {k(I["agv_landed_usd"])} each + {m(I["integration_usd"])} integration, +10 % project)</td><td class="num">{m(B["capex"])}</td></tr>
<tr><td>Annual savings (labour, avoided reach trucks, damage)</td><td class="num">{m(B["annual_savings"])}</td></tr>
<tr><td>Annual opex (service 6 %, software)</td><td class="num">{m(B["annual_opex"])}</td></tr>
<tr><td><b>Simple payback</b></td><td class="num"><b>{B["payback_yrs"]} yrs</b></td></tr>
<tr><td>NPV / IRR ({NPV["life_yrs"]}-yr life, battery swap yr 5, {NPV["wacc_pct"]:.0f} % WACC, no residual)</td><td class="num">{m(NPV["npv_usd"])} / {NPV["irr_pct"]} %</td></tr>
</table></div><div>
<table><tr><th>Sensitivity (one at a time)</th><th class="num">Base</th><th class="num">Favourable</th><th class="num">Adverse</th></tr>{sens_rows}</table>
<div class="box warn"><b>Honest read:</b> the base case sits on the 3-year line ({B["payback_yrs"]} yrs). A combined adverse case ($240k AGV, 7 pal/h, outbound 0.5×) gives <b>{ADV["payback_yrs"]} yrs</b>.
At the 6.2 pal/h observed for horizontal moves in today's mixed traffic, payback would be ≈{P["at_observed_6_2"]["payback_yrs"]} yrs. Why we model 9 pal/h: bottom-up, one dock-to-rack cycle is ≈100 m each way at 1.5 m/s, lift and lower to 10 m, and ≈60 s of positioning, about 260 s or ≈14 cycles/h theoretical. We apply ×0.65 for traffic and charging. The ×0.8 freezer factor is applied to people only, because it models cold-stress warm-up breaks; AGV battery derating in the freezer sits inside the 15 % availability buffer. That is why the ≥9.2 pal/h gate must be proven <b>inside the -18 °C zone</b>, not only in the chilled zone.
So these numbers become award conditions: DDP price ≤<b>{k(B["max_landed_price_for_3yr"])}</b> per AGV and ≥<b>{BE:g} pal/h</b> per AGV proven in the pilot, backed by liquidated damages.</div>
</div></div>
<p class="small">Assumptions marked in the model: outbound ≈ inbound; loaded labour {k(I["loaded_cost_usd"])}/FTE/yr; 2.4 FTE per 20 h/day position; reach truck {k(I["truck_cost_usd"])}/yr. Inference, not data: if a manual horizontal move runs at ≈20 pal/h, Supplier A's 3.9-yr payback implies ≈{m(A["implied_all_in_capex"])} all-in (≈{k(A["implied_per_agv"])} per AGV). This is plausible for a horizontal-only project; Smithfield's actual capex should replace it.</p>

<h3>3.3 Plants (36 sites; 8.5 m, ambient / chilled / frozen)</h3>
<ul>
<li><b>Mobile layer:</b> VisionNav reach AGVs with a 9.2 m mast for freezer putaway to 8.5 m, and pallet AGVs for production-to-store transfers. Multiway R20 (9.5 m, -30 °C claimed) is invited in every plant wave as second source; wave-level competition keeps VisionNav's network price honest.</li>
<li><b>Same design rules as the DCs:</b> zone-dedicated vehicles, airlock conveyors, AGV-only aisles, WES integration.</li>
<li><b>Not every plant should be automated now.</b> The same model was run for plant archetypes (assumptions in tool/payback.py):
<table><tr><th>Archetype</th><th class="num">AGVs</th><th class="num">FTE redeployed</th><th class="num">Capex</th><th class="num">Payback</th></tr>
{"".join(f'<tr><td>{n}</td><td class="num">{v["fleet"]}</td><td class="num">{v["fte_saved"]}</td><td class="num">{m(v["capex"])}</td><td class="num"><b>{v["payback_yrs"]} yrs</b></td></tr>' for n, v in PL.items())}
</table>
<b>Rule:</b> a plant qualifies for new high-reach AGVs when its 8.5 m freezer store handles ≥{BEP} moves/h (in + out). Low-volume, horizontal-only plants like Plant 1 (≈5 yrs with new capex) get Supplier A's surplus units, with no new vehicle capex (relocation, re-mapping and re-commissioning only). The brief's figure that 7 AGVs replaced only 2 operators at Plant 1 confirms that low-volume transfer lanes do not pay back new vehicles.</li>
<li><b>Building check per site:</b> Plant 1's building is listed at ≥5 m, below the 8.5 m stacking requirement. A clear-height survey per site sets the mast (8.3 / 9.2 m) and identifies sites where 8.5 m storage exists only in separate freezer buildings.</li>
<li><b>Plant 1, right-size first:</b> demand is {P1["demand_pal_h"]} pal/h (400 pal/day over 16.5 h), against a stated capacity of {P1["stated_capacity_pal_h"]} pal/h (7 × 21), which is {P1["stated_utilisation_pct"]} % utilisation.
21 pal/h per unit means a ≈171 s cycle. If 288.6 m is one way, that needs ≥3.4 m/s even with zero pick/drop time; if it is the round trip, 1.7–2.6 m/s. Laden forklift AGVs typically run 1–1.5 m/s, so neither reading is credible. If 21 pal/h is the fleet rate, capacity is only {P1["if_21_is_fleet_rate_pal_day"]} pal/day, below demand.
A two-day time study settles it; at a realistic 8 pal/h, {P1["units_needed_at_8_pal_h"]} units suffice and 3 can move to other ambient lanes with no new vehicle capex.</li>
<li><b>Wave order:</b> rank the 40 sites with the same payback model using each site's moves/h, freezer share and labour rate. Do the 4 DCs first (highest moves/h at height), then plants by freezer volume.</li>
</ul>

<h2>4. New flagship plant (assumed Sioux Falls): chosen design, basis and trade-offs</h2>
<p>The brief leaves storage height, load and temperature zones open. We chose them to fit the evidence on what suppliers can do and the goal of the world's most advanced plant, not the old facilities' parameters.</p>
<table><tr><th>Parameter</th><th>Chosen</th><th>Basis</th><th>Trade-off accepted</th></tr>
<tr><td>Frozen storage</td><td><b>-25 °C high-bay AS/RS, ≈24 m, stacker cranes</b> (Inform)</td><td>≈13 levels vs 7 at 10.5 m (×1.9) and deep lanes with no reach-truck aisles (≈0.6 vs 0.32 positions/m² per level, ×1.9), so ≈3.5× pallets per m² (indicative ±20 %). Smaller freezer envelope (≈55–60 % less surface per pallet at equal capacity). No people at -25 °C. In-group benchmark (2013 trade press): Shuanghui Mianyang -18 °C store, 24 m, 15 cranes, ≈29,500 positions.</td><td>A second supplier; higher fixed capex and less layout flexibility than AGVs; crane redundancy needed (n+1 aisles)</td></tr>
<tr><td>Freezer set-point</td><td><b>-25 °C</b> (vs -18 °C in existing sites)</td><td>Longer frozen shelf life for export pork; Inform's pallet shuttle is rated -25 °C to +45 °C</td><td>Roughly 2–4 % more refrigeration energy per °C (rule of thumb, to be confirmed by the refrigeration designer)</td></tr>
<tr><td>Chilled buffer (0–2 °C)</td><td><b>Pallet four-way shuttles, 1.5 t class</b></td><td>Short dwell and high throughput; add shuttles as volume grows; no single-aisle failure point</td><td>Lower height than cranes</td></tr>
<tr><td>Design load</td><td><b>1.5 t per position</b></td><td>Covers the 1,134 kg DC max and 1,000–1,500 kg plant pallets; matches Inform's 1.5 t shuttle class</td><td>Heavier racking and slab (DC1 benchmark ≥2 t/m²)</td></tr>
<tr><td>Zones</td><td><b>Ambient packaging · 0–2 °C chilled · -25 °C frozen · blast cells</b></td><td>Each zone has its own vehicles; blast cells feed the frozen store directly by conveyor</td><td>More P&amp;D stations and conveyors</td></tr>
<tr><td>Mobile layer</td><td><b>VisionNav</b> for end-of-line (palletiser → P&amp;D), dock loading and packaging supply</td><td>Same fleet, software, spares and training as the 40 retrofit sites</td><td>None vs alternatives</td></tr>
<tr><td>Pallet standard</td><td><b>40×48 in GMA, 4-way, inspected at infeed</b></td><td>Network compatibility with DCs and customers</td><td>Inform must prove GMA pallets on its rails (China standard is 1200×1000)</td></tr>
</table>
<h3>Alternative considered: AGV-only new plant (single supplier), indicative comparison for a 30,000-position frozen store</h3>
<table><tr><th></th><th>O1: 24 m crane AS/RS (recommended)</th><th>O2: 10.5 m AGV-racked (single supplier)</th></tr>
<tr><td>Footprint</td><td>≈3,850 m²</td><td>≈13,400 m² (≈3.5×)</td></tr>
<tr><td>Refrigerated envelope</td><td>≈14,000 m²</td><td>≈33,000 m² (≈2.4× heat ingress)</td></tr>
<tr><td>Handling equipment</td><td>≈12–15 cranes, sized by throughput (Shuanghui: 15 for 29,500)</td><td>≈16–30 freezer high-reach AGVs</td></tr>
<tr><td>Building (assumed $5,500/m² high-bay vs $3,000/m² freezer)</td><td>≈$21M</td><td>≈$40M</td></tr>
<tr><td>Storage equipment (assumed)</td><td>≈$22M (cranes, racking, conveyors)</td><td>≈$8M (racking $120/position + AGVs)</td></tr>
<tr><td><b>Indicative capex (±40 %)</b></td><td><b>≈$43M</b></td><td><b>≈$48M</b></td></tr>
<tr><td>Operations</td><td>No people or vehicles in -25 °C storage; highest throughput per m²</td><td>One supplier network-wide; flexible layout; more vehicles in freezer aisles</td></tr>
</table>
<div class="box">At order-of-magnitude level the capex is comparable, so the decision rests on footprint, refrigeration energy and operations, all of which favour O1. The 2.4× envelope drives permanent energy cost.
All figures are assumptions to be replaced by Epstein and Inform estimates at design freeze. <b>The in-group precedent:</b> Shuanghui's Mianyang store used imported cranes. We still shortlist Inform because of price, its -25 °C pallet-shuttle line and its Thailand plant for US supply, but it must clear the same factory test and US-code gate a European crane vendor would. A European crane vendor is kept as the benchmark bid.
This option is kept as a fallback if Inform fails its gates (UL listing, GMA pallets, US service). In that case the new plant reverts to a VisionNav-only design at 10.5 m.</div>

<h2>5. Risks and mitigations</h2>
<table><tr><th>Risk</th><th>Mitigation</th></tr>
<tr><td>VisionNav's load at 10.46 m and its -18 °C rating are unpublished (gates G2/G3 CONDITIONAL)</td><td>Witnessed factory test (1,134 kg at 10.46 m; 72 h at -18 °C) before any network award. Fallback: Multiway for plants plus a non-Chinese freezer reach AGV (Dematic/Muratec) for DCs.</td></tr>
<tr><td>No UL 3100 / B56.5 listing found for any Chinese candidate</td><td>Contractual NRTL certification plan with dates; NRTL field evaluation at the first site; no go-live without it.</td></tr>
<tr><td>US tariffs on China-made industrial trucks (Section 301 on HTS 8427) plus the Section 232 national-security action on robotics and industrial machinery (investigation initiated 2 Sept 2025, 90 FR 46382; current duty status to be confirmed by the customs broker); payback is very sensitive to landed price</td><td>Show the tariff stack in every quote (FOB + 301 + 232 + freight = DDP). Contract clause: the supplier absorbs any increase above the {k(B["max_landed_price_for_3yr"])} cap, or the award re-opens. Customs-broker ruling; ask about Inform's Thailand and VisionNav's non-China assembly options.</td></tr>
<tr><td>Regulatory and political: a Chinese-owned US food processor deploying Chinese connected robots at 41 critical food-supply sites invites Commerce ICTS review (EO 13873) and public scrutiny. WH Group ownership helps sourcing leverage in China but amplifies that scrutiny.</td><td>Air-gapped, on-prem fleet manager; US-hosted software build with code escrow; a qualified non-Chinese VDA 5050 swap-in (Dematic/Muratec) kept warm; government-affairs pre-brief before award.</td></tr>
<tr><td>Cybersecurity scrutiny of China-connected equipment</td><td>On-prem fleet manager and WCS; no outbound cloud by default; SBOM; Smithfield-controlled remote access; pen-test before go-live.</td></tr>
<tr><td>VisionNav is venture-funded and unlisted (rolling out to 41 sites)</td><td>Audited financials, source-code and spares escrow, parent guarantee, VDA 5050 so another fleet can be swapped in.</td></tr>
<tr><td>Inform has no US entity</td><td>Contract through Epstein with a named US installation and service partner; resident technician; critical spares on site.</td></tr>
<tr><td>Two suppliers make operations less unified</td><td>Smithfield owns the control layer (WES + VDA 5050), so operators see one system, one KPI set and one ticket queue.</td></tr>
</table>

<h2>6. Roadmap and award gates</h2>
<table><tr><th>When</th><th>Action</th><th>Gate to pass</th></tr>
<tr><td>Q4 2026 (next 90 days)</td><td>RFQs: VisionNav (network), Hangcha / HELI / EP (mobile-layer challengers), Multiway (plants), Dematic/Muratec (benchmark). Labour-relations notice and redeployment plan (union consultation where sites are represented; drivers retrained as AGV technicians / dock-sort leads). Inform design-in RFQ with Epstein. Plant 1 time study. DC1 5S and traffic segregation. WES selection. Customs ruling.</td><td>Complete load charts, cold ratings, UL plan, DDP prices</td></tr>
<tr><td>Q1 2027</td><td>Witnessed factory tests in China (-18 °C chamber; 1,134 kg at 10.46 m and 1,500 kg at 8.5 m); Inform GMA-pallet test</td><td>G1–G5 PASS (G4 N/A by design)</td></tr>
<tr><td>Q2 2027</td><td>DC1 pilot: chilled + frozen fleets, dock sort, airlock P&amp;D, WES live (8 weeks)</td><td>≥{BE:g} pal/h per AGV at height, ≥98 % availability, NRTL sign-off, payback &lt;3 yrs re-modelled</td></tr>
<tr><td>1H 2027</td><td>New plant: Inform design-in and storage design freeze aligned with groundbreaking</td><td>Inform G5/G6 evidence; US code compliance stamped by a US PE through Epstein: ANSI MH16.1 (RMI) racking, IBC snow and seismic for a 24 m high-bay, NFPA 13 / FM in-rack dry sprinklers at -25 °C</td></tr>
<tr><td>H2 2027 (after pilot sign-off)</td><td>DCs 2–4; plant wave 1 (qualifying plants only, VisionNav vs Multiway competed)</td><td>Pilot sign-off + NRTL clearance; site payback &lt;3 yrs</td></tr>
<tr><td>2028</td><td>New plant: install and commission storage + mobile layers</td><td>FAT; SAT before production start (end-2028)</td></tr>
<tr><td>2028–2029</td><td>Plant waves 2–3; Supplier A units retired at end of life</td><td>Network KPIs on the shared WES dashboard</td></tr>
</table>
<p class="small">Sources and research notes: supplier_evaluation_criteria.pdf (per-supplier source lists). Smithfield context: Smithfield FY2025 10-K; Lineage/Smithfield Olathe press release (2022); Smithfield Sioux Falls announcement (2026-02-16); ENR (Epstein selection, 2026-06-30). Section 232 robotics investigation: bis.gov Section 232 page; Federal Register 2025-18749. Shuanghui Mianyang store: news.soo56.com (2013). Labour, price and productivity figures are explicit assumptions in tool/payback.py and must be replaced with RFQ and time-study data.</p>
</body></html>"""

(ROOT.parent / "build/logistics_solution.html").write_text(html)
print("wrote build/logistics_solution.html")
