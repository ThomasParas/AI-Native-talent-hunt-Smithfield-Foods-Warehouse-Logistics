"""Render build/logistics_solution.html from build/scores.json + build/payback.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
S = json.loads((ROOT.parent / "build/scores.json").read_text())
P = json.loads((ROOT.parent / "build/payback.json").read_text())
B, A, P1, I = P["base"], P["supplier_a"], P["plant1"], P["inputs"]
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
         "integration_usd": "Integration + site works"}


def fmt(param, v):
    return k(v) if "usd" in param else f"{v:g} pal/h"


sens_rows = "".join(
    f'<tr><td>{LABEL[s["param"]]}</td><td class="num">{fmt(s["param"], I[s["param"]])}</td>'
    f'<td class="num">{fmt(s["param"], s["good"])} → {s["payback_good"]} yrs</td>'
    f'<td class="num">{fmt(s["param"], s["bad"])} → {s["payback_bad"]} yrs</td></tr>' for s in P["sensitivity"])

single_rows = ""
for name, role in [("Supplier A", "—"), ("VisionNav", "mobile"), ("Multiway", "mobile"), ("Inform", "storage")]:
    g = SC[name]["gates"]
    single_rows += f"<tr><td><b>{name}</b></td><td>{role}</td>" + "".join(f"<td>{badge(g[s])}</td>" for s in ("PLANT", "DC", "NEW")) + f'<td class="num">{SC[name]["adjusted"]}</td></tr>'

ARCH = """
<svg viewBox="0 0 760 250" width="100%" xmlns="http://www.w3.org/2000/svg" font-size="11">
 <rect x="10" y="8" width="740" height="44" rx="6" fill="#1f3a5f"/>
 <text x="380" y="27" fill="#fff" text-anchor="middle" font-weight="700">CONTROL LAYER — owned by Smithfield</text>
 <text x="380" y="43" fill="#dfe7f1" text-anchor="middle">Corporate WMS → supplier-neutral WES/orchestrator → VDA 5050 to robot fleets · WCS messages to AS/RS · one dashboard, one KPI set</text>
 <rect x="10" y="66" width="360" height="118" rx="6" fill="#eef3f9" stroke="#1f3a5f"/>
 <text x="190" y="86" text-anchor="middle" font-weight="700" fill="#1f3a5f">MOBILE LAYER — VisionNav (single fleet)</text>
 <text x="22" y="106" fill="#1b2430">• 36 plants: reach AGVs ≤8.5 m (9.2 m mast), pallet AGVs</text>
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
<div class="box red"><b>Can Supplier A meet the network's needs? No.</b> It fails four of six knock-out gates in every scenario: 4 m lift against 8.5 m / 10.5 m, no 1 t pallet at height, no -18 °C, no cross-zone operation.
Its 3.9-year payback has a structural cause, not just an operational one: it automates only the horizontal leg (dock staging to aisle), while people still do every putaway with reach trucks.
Our back-calculation shows that scope replaces only ≈{A["positions_replaced"]} driver positions (≈{k(A["annual_savings"])}/yr), so better routes (4.5 → 6.2 pal/h) cannot bring payback under 3 years.</div>
<div class="box"><b>Recommendation: a combination of two suppliers, organised as two layers with one shared control layer.</b> A single supplier for every scenario is not feasible on current evidence: no Chinese mobile-robot supplier
can deliver the high-density -25 °C storage that a world-class greenfield plant needs, and the storage specialist has no high-reach forklift line or US service network for 40 brownfield sites.
<ol>
<li><b>VisionNav as the single mobile-robot supplier</b> for all 36 plants, 4 DCs and the new plant's horizontal flows. This keeps the company's single-supplier preference wherever vehicles are involved. Award depends on a witnessed test of 1,134 kg at 10.46 m and -18 °C, plus a UL 3100 plan.</li>
<li><b>Inform as the storage-system supplier for the new plant only:</b> a -25 °C high-bay frozen store with stacker cranes and a chilled four-way-shuttle buffer, designed in with Epstein (the design-build contractor).</li>
<li><b>A supplier-neutral control layer owned by Smithfield</b> (WES/orchestrator + VDA 5050), so the network runs as one system and no supplier controls the integration.</li>
</ol>
Multiway is a qualified second source for the 8.5 m plants, which keeps pricing competitive. Supplier A's existing 17 units stay on, or move to, ambient horizontal lanes, where they work well, and no new Supplier A units are bought.</div>
<div class="kpis">
<div class="kpi"><div class="v">3.9 → {B["payback_yrs"]} yrs</div><div class="l">DC1 payback, horizontal-only vs end-to-end (base case; range {lo}–{hi})</div></div>
<div class="kpi"><div class="v">{B["fleet"]} AGVs</div><div class="l">DC1 zone-dedicated fleet for {B["moves_h"]:.0f} moves/h (in + out)</div></div>
<div class="kpi"><div class="v">≤{k(B["max_landed_price_for_3yr"])}</div><div class="l">Landed price ceiling per AGV to stay under 3 yrs, used as the negotiation cap</div></div>
<div class="kpi"><div class="v">≈3.5×</div><div class="l">New-plant frozen storage density, 24 m AS/RS vs 10.5 m AGV racking</div></div>
</div>

<h2>1. Network requirements and the sourcing result</h2>
<p>Binding retrofit constraints (from the brief and DC1 data): stack to <b>8.5 m</b> in plants and <b>10.5 m</b> in DCs (top beam 10.46 m); pallets 544–907 kg, max <b>1,134 kg</b>, 40×48 in GMA grid-base;
chilled -2 °C and frozen <b>-18 °C</b>; mixed chilled and frozen truckloads; 20 h/day. Smithfield context: Olathe, KS is already a fully automated cold DC (Lineage, 18 cranes), so this plan does not re-pitch a generic automated DC.
It targets the 4 DCs and 36 plants that are still manual, and the Sioux Falls plant ($1.3B, production end-2028), whose warehouse design is still open.</p>
<table><tr><th>Supplier</th><th>Role</th><th>Plants</th><th>DCs</th><th>New plant</th><th>Risk-adj. score</th></tr>{single_rows}</table>
<p class="small">CONDITIONAL = no gate failed, but at least one is claimed or unverified and must be proven before award. Hikrobot was screened out (Hikvision subsidiary; US Entity List / FCC Covered List). Non-Chinese freezer AGVs (Dematic, Muratec) are kept only as a price/spec benchmark and fallback.</p>

<h3>Single-supplier test: why one supplier cannot cover all scenarios today</h3>
<table><tr><th>Candidate as sole supplier</th><th>Retrofits (40 sites)</th><th>New plant</th><th>Verdict</th></tr>
<tr><td>Supplier A</td><td>Fails height, load, freezer, cross-zone</td><td>Would force ≤4 m storage</td><td>{badge("FAIL")}</td></tr>
<tr><td>Multiway</td><td>Plants OK (9.5 m, -30 °C claimed); DCs fail: 700–750 kg at 9.5–11 m &lt; 1,134 kg</td><td>Only with ≤8.5 m racking</td><td>{badge("FAIL")} at DCs</td></tr>
<tr><td>Inform</td><td>Requires ripping out racks in 40 operating buildings; no high-reach forklift line; no US entity</td><td>Strong (-25 °C, 1–2 t shuttles, cranes)</td><td>{badge("FAIL")} on payback / disruption</td></tr>
<tr><td>VisionNav</td><td>Only Chinese reach AGV with &gt;10.5 m mast (11.2 m); US entity</td><td>Possible only as a 10.5 m AGV-racked store: ≈3.5× footprint, more freezer envelope, lower throughput</td><td>{badge("CONDITIONAL")}: mobile layer only</td></tr>
</table>
<p>The closest single-supplier design (O2: VisionNav everywhere, new plant limited to 10.5 m AGV racking) was evaluated and rejected for the new plant on density, energy and throughput grounds (section 4).
We keep the single-supplier principle where it creates the most value: <b>one mobile fleet, one service contract, one spare-parts pool and one training curriculum across all 41 sites</b>, because vehicles are where the 41-site scale sits.</p>

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
<li><b>Sort mixed trucks at the dock.</b> One manual step at receiving splits each mixed truck into chilled and frozen inbound lanes. This removes the mixed-load blocker that limited Supplier A's utilisation.</li>
<li><b>Zone-dedicated fleets plus airlock conveyors</b> instead of vehicles that cross zones. Frozen pallets enter the -18 °C zone on a short P&amp;D conveyor through a rapid-roll door. The cross-zone requirement is met by design, so it does not depend on an unproven vehicle claim.</li>
<li><b>Segregate traffic and run 5S</b> (the brief expects 4.5 → 6.2 pal/h from clear routes alone): AGV-only aisles, pallet-debris rules, marked crossings.</li>
<li><b>Integration:</b> a WES reads tasks from Accellos (now Körber) through the existing read-only access and confirms by scan, while write access or API rights are negotiated. Full read/write is a phase-2 exit criterion.</li>
<li><b>Supplier A's 10 DC1 units</b> move to ambient horizontal routes at plants, where Plant 1 shows they are stable.</li>
</ol>
<h3>3.2 DC1 payback model (tool/payback.py, all assumptions explicit)</h3>
<div class="cols"><div>
<table><tr><th>Item</th><th class="num">Base case</th></tr>
<tr><td>Dock↔rack moves/h (61 in + 61 out, 59 % chilled)</td><td class="num">{B["moves_h"]:.0f}</td></tr>
<tr><td>AGV fleet (9 pal/h each, +15 % availability buffer, zone-dedicated)</td><td class="num">{B["fleet"]}</td></tr>
<tr><td>Manual positions replaced (12 pal/h; ×0.8 in freezer)</td><td class="num">{B["manual_positions"]}</td></tr>
<tr><td>Net FTE redeployed (2.4 FTE/position − 2.4 supervisors)</td><td class="num">{B["fte_saved"]}</td></tr>
<tr><td>Capex (vehicles {k(I["agv_landed_usd"])} each + {m(I["integration_usd"])} integration, +10 % project)</td><td class="num">{m(B["capex"])}</td></tr>
<tr><td>Annual savings (labour, avoided reach trucks, damage)</td><td class="num">{m(B["annual_savings"])}</td></tr>
<tr><td>Annual opex (service 6 %, software)</td><td class="num">{m(B["annual_opex"])}</td></tr>
<tr><td><b>Simple payback</b></td><td class="num"><b>{B["payback_yrs"]} yrs</b></td></tr>
</table></div><div>
<table><tr><th>Sensitivity (one at a time)</th><th class="num">Base</th><th class="num">Favourable</th><th class="num">Adverse</th></tr>{sens_rows}</table>
<div class="box warn"><b>Honest read:</b> the base case meets the &lt;3-year standard, but the margin is thin.
The two biggest swings are AGV landed price (tariffs) and real cycle time at 10.5 m. Contract levers: a DDP tariff-inclusive price cap of <b>{k(B["max_landed_price_for_3yr"])}</b> per AGV,
and a guaranteed pal/h figure from vendor simulation, backed by liquidated damages.</div>
</div></div>
<p class="small">Assumptions marked in the model: outbound ≈ inbound; loaded labour {k(I["loaded_cost_usd"])}/FTE/yr; 2.4 FTE per 20 h/day position; reach truck {k(I["truck_cost_usd"])}/yr. Calibration check: Supplier A's 3.9-yr payback implies ≈{m(A["implied_all_in_capex"])} all-in (≈{k(A["implied_per_agv"])} per AGV), which is consistent with a horizontal-only Chinese AGV project.</p>

<h3>3.3 Plants (36 sites; 8.5 m, ambient / chilled / frozen)</h3>
<ul>
<li><b>Mobile layer:</b> VisionNav reach AGVs with a 9.2 m mast for freezer putaway to 8.5 m, and pallet AGVs for production-to-store transfers. Multiway R20 (9.5 m, -30 °C claimed) is invited in every plant wave as second source; wave-level competition keeps VisionNav's network price honest.</li>
<li><b>Same design rules as the DCs:</b> zone-dedicated vehicles, airlock conveyors, AGV-only aisles, WES integration.</li>
<li><b>Plant 1, right-size first:</b> demand is {P1["demand_pal_h"]} pal/h (400 pal/day over 16.5 h), against a stated capacity of {P1["stated_capacity_pal_h"]} pal/h (7 × 21), which is {P1["stated_utilisation_pct"]} % utilisation.
21 pal/h per unit on a 288.6 m route would need an average speed of about 5 m/s, which is not credible. If 21 pal/h is the fleet rate, capacity is only {P1["if_21_is_fleet_rate_pal_day"]} pal/day, below demand.
A two-day time study settles it; at a realistic 8 pal/h, {P1["units_needed_at_8_pal_h"]} units suffice and 3 can move to other ambient lanes at no capex.</li>
<li><b>Wave order:</b> rank the 40 sites with the same payback model using each site's moves/h, freezer share and labour rate. Do the 4 DCs first (highest moves/h at height), then plants by freezer volume.</li>
</ul>

<h2 class="pb">4. New flagship plant (Sioux Falls): chosen design, basis and trade-offs</h2>
<p>The brief leaves storage height, load and temperature zones open. We chose them to fit the evidence on what suppliers can do and the goal of the world's most advanced plant, not the old facilities' parameters.</p>
<table><tr><th>Parameter</th><th>Chosen</th><th>Basis</th><th>Trade-off accepted</th></tr>
<tr><td>Frozen storage</td><td><b>-25 °C high-bay AS/RS, ≈24 m, stacker cranes</b> (Inform)</td><td>≈13 levels vs 7 at 10.5 m (×1.9) and deep lanes with no reach-truck aisles (≈0.6 vs 0.32 positions/m² per level, ×1.9), so ≈3.5× pallets per m² (indicative ±20 %). Smaller freezer envelope (≈55–60 % less surface per pallet at equal capacity). No people at -25 °C. In-group benchmark: Shuanghui Mianyang -18 °C store, 24 m, 15 cranes, ≈29,500 positions.</td><td>A second supplier; higher fixed capex and less layout flexibility than AGVs; crane redundancy needed (n+1 aisles)</td></tr>
<tr><td>Freezer set-point</td><td><b>-25 °C</b> (vs -18 °C in existing sites)</td><td>Longer frozen shelf life for export pork; Inform's pallet shuttle is rated -25 °C to +45 °C</td><td>Roughly 2–4 % more refrigeration energy per °C (rule of thumb, to be confirmed by the refrigeration designer)</td></tr>
<tr><td>Chilled buffer (0–2 °C)</td><td><b>Pallet four-way shuttles, 1.5 t class</b></td><td>Short dwell and high throughput; add shuttles as volume grows; no single-aisle failure point</td><td>Lower height than cranes</td></tr>
<tr><td>Design load</td><td><b>1.5 t per position</b></td><td>1,134 kg max pallet plus margin; matches Inform's 1.5 t shuttle class; also suits 1,000–1,500 kg plant pallets</td><td>Heavier racking and slab (DC1 benchmark ≥2 t/m²)</td></tr>
<tr><td>Zones</td><td><b>Ambient packaging · 0–2 °C chilled · -25 °C frozen · blast cells</b></td><td>Each zone has its own vehicles; blast cells feed the frozen store directly by conveyor</td><td>More P&amp;D stations and conveyors</td></tr>
<tr><td>Mobile layer</td><td><b>VisionNav</b> for end-of-line (palletiser → P&amp;D), dock loading and packaging supply</td><td>Same fleet, software, spares and training as the 40 retrofit sites</td><td>None vs alternatives</td></tr>
<tr><td>Pallet standard</td><td><b>40×48 in GMA, 4-way, inspected at infeed</b></td><td>Network compatibility with DCs and customers</td><td>Inform must prove GMA pallets on its rails (China standard is 1200×1000)</td></tr>
</table>
<div class="box"><b>Alternative considered: AGV-only new plant (single supplier).</b> A 10.5 m VisionNav-racked freezer would be about 3.5× larger in footprint for the same capacity.
For an illustrative 30,000-position frozen store, that is ≈13,600 m² vs ≈3,800 m², with roughly double the refrigerated envelope, people still working around -25 °C aisles, and 25–30 high-reach AGVs instead of 5–6 cranes.
This option is kept as a fallback if Inform fails its gates (UL listing, GMA pallets, US service). In that case the new plant reverts to a VisionNav-only design at 10.5 m.</div>

<h2>5. Risks and mitigations</h2>
<table><tr><th>Risk</th><th>Mitigation</th></tr>
<tr><td>VisionNav's load at 10.46 m and its -18 °C rating are unpublished (gates G2/G3 CONDITIONAL)</td><td>Witnessed factory test (1,134 kg at 10.46 m; 72 h at -18 °C) before any network award. Fallback: Multiway for plants plus a non-Chinese freezer reach AGV (Dematic/Muratec) for DCs.</td></tr>
<tr><td>No UL 3100 / B56.5 listing found for any Chinese candidate</td><td>Contractual NRTL certification plan with dates; NRTL field evaluation at the first site; no go-live without it.</td></tr>
<tr><td>US tariffs on China-made industrial trucks; payback is very sensitive to landed price</td><td>DDP tariff-inclusive pricing with a {k(B["max_landed_price_for_3yr"])} cap; customs-broker ruling; ask about Inform's Thailand and VisionNav's non-China assembly options.</td></tr>
<tr><td>Cybersecurity scrutiny of China-connected equipment</td><td>On-prem fleet manager and WCS; no outbound cloud by default; SBOM; Smithfield-controlled remote access; pen-test before go-live.</td></tr>
<tr><td>VisionNav is venture-funded and unlisted (rolling out to 41 sites)</td><td>Audited financials, source-code and spares escrow, parent guarantee, VDA 5050 so another fleet can be swapped in.</td></tr>
<tr><td>Inform has no US entity</td><td>Contract through Epstein with a named US installation and service partner; resident technician; critical spares on site.</td></tr>
<tr><td>Two suppliers make operations less unified</td><td>Smithfield owns the control layer (WES + VDA 5050), so operators see one system, one KPI set and one ticket queue.</td></tr>
</table>

<h2>6. Roadmap and award gates</h2>
<table><tr><th>When</th><th>Action</th><th>Gate to pass</th></tr>
<tr><td>Q4 2026 (next 90 days)</td><td>RFQs: VisionNav (network), Multiway (plants), Dematic/Muratec (benchmark). Inform design-in RFQ with Epstein. Plant 1 time study. DC1 5S and traffic segregation. WES selection. Customs ruling.</td><td>Complete load charts, cold ratings, UL plan, DDP prices</td></tr>
<tr><td>Q1 2027</td><td>Witnessed factory tests in China (-18 °C chamber, 1,134 kg at 10.46 m); Inform GMA-pallet test</td><td>G1–G5 PASS</td></tr>
<tr><td>Q2 2027</td><td>DC1 pilot: chilled + frozen fleets, dock sort, airlock P&amp;D, WES live (8 weeks)</td><td>≥ simulated pal/h, ≥98 % availability, NRTL sign-off, payback &lt;3 yrs re-modelled</td></tr>
<tr><td>H2 2027</td><td>DCs 2–4; plant wave 1 (top 8 by payback, VisionNav vs Multiway competed)</td><td>Wave payback &lt;3 yrs</td></tr>
<tr><td>1H 2027 → end-2028</td><td>Sioux Falls: storage design freeze aligned with groundbreaking; install and commission 2028</td><td>Design review; FAT; SAT before production start</td></tr>
<tr><td>2028–2029</td><td>Plant waves 2–3; Supplier A units retired at end of life</td><td>Network KPIs on the shared WES dashboard</td></tr>
</table>
<p class="small">Sources and research notes: supplier_evaluation_criteria.pdf (per-supplier source lists). Smithfield context: Smithfield FY2025 10-K; Lineage/Smithfield Olathe press release (2022); Smithfield Sioux Falls announcement (2026-02-16); ENR (Epstein selection, 2026-06-30). Shuanghui Mianyang store: news.soo56.com (2013). Labour, price and productivity figures are explicit assumptions in tool/payback.py and must be replaced with RFQ and time-study data.</p>
</body></html>"""

(ROOT.parent / "build/logistics_solution.html").write_text(html)
print("wrote build/logistics_solution.html")
