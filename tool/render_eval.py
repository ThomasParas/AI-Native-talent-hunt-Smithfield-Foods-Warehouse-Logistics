"""Render build/supplier_evaluation_criteria.html from build/scores.json (run score.py first)."""
import json
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent
D = json.loads((ROOT.parent / "build/scores.json").read_text())
C, R = D["criteria"], D["results"]
SUPS = {s["short"]: s for s in (__import__("yaml").safe_load(p.read_text()) for p in sorted((ROOT / "suppliers").glob("*.yaml")))}
ROLE = {
    "Supplier A": "Legacy: keep existing units on ambient horizontal lanes only; no new orders",
    "VisionNav": "Recommended mobile layer (all 41 sites + new plant), award gated on witnessed test",
    "Multiway": "Qualified second source for 8.5 m plants; excluded at DCs (load at height)",
    "Inform": "Recommended storage layer for the new plant (-25 °C AS/RS); not for brownfield retrofit",
}


SHORT = {"pass": "PASS", "fail": "FAIL", "claimed": "CLM", "unverified": "UNV"}


def badge(v, short=False):
    v = str(v)
    label = SHORT.get(v, v.upper()) if short else v.upper()
    return f'<span class="b {e(v)}">{e(label)}</span>'


def criteria_table():
    rows = []
    for g in C["groups"]:
        sub = sum(c["w"] for c in g["criteria"])
        rows.append(f'<tr><td colspan="4"><b>{e(g["name"])}</b> — {sub} points</td></tr>')
        for c in g["criteria"]:
            rows.append(f'<tr><td>{c["id"]}</td><td><b>{e(c["name"])}</b></td><td class="num">{c["w"]}</td><td>{e(c["scale"])}</td></tr>')
    return "<table><tr><th>ID</th><th>Criterion</th><th>Weight</th><th>Scoring guide (0–5)</th></tr>" + "".join(rows) + "</table>"


def gates_table():
    rows = "".join(f'<tr><td>{g["id"]}</td><td><b>{e(g["name"])}</b></td><td>{e(g["test"])}</td></tr>' for g in C["gates"])
    return f"<table><tr><th>ID</th><th>Gate</th><th>Pass test</th></tr>{rows}</table>"


def scen_table():
    rows = ""
    for k, s in C["scenarios"].items():
        h = f'{s["height_m"]} m' if s["height_m"] else "design variable"
        rows += f'<tr><td><b>{k}</b></td><td>{e(s["name"])}</td><td>{h}</td><td>{s["load_kg"]:,} kg</td><td>{s["min_temp_c"]} °C</td><td>{"yes" if s["cross_zone"] else "no"}</td></tr>'
    return f"<table><tr><th>Code</th><th>Scenario</th><th>Store / lift height</th><th>Max pallet</th><th>Min temp</th><th>Cross-zone</th></tr>{rows}</table>"


def summary_table():
    rows = ""
    for r in R:
        g = "".join(f"<td>{badge(r['gates'][k])}</td>" for k in C["scenarios"])
        rows += (f'<tr><td><b>{e(r["short"])}</b></td>{g}<td class="num"><b>{r["adjusted"]}</b></td>'
                 f'<td class="num">{r["raw"]}</td><td class="num">{r["evidence_coverage"]}%</td><td>{e(ROLE[r["short"]])}</td></tr>')
    return ("<table><tr><th>Supplier</th><th>Plants</th><th>DCs</th><th>New plant</th><th>Risk-adj. score /100</th>"
            f"<th>Evidence-only score</th><th>Evidence coverage</th><th>Role</th></tr>{rows}</table>")


def gate_matrix():
    head = "".join(f"<th>{e(r['short'])}<br>P / DC / New</th>" for r in R)
    rows = ""
    for g in C["gates"]:
        cells = ""
        for r in R:
            d = r["gate_detail"].get(g["id"], {})
            cells += '<td style="white-space:nowrap">' + " ".join(badge(d.get(s, "unverified"), True) for s in C["scenarios"]) + "</td>"
        rows += f'<tr><td><b>{g["id"]}</b> {e(g["name"])}</td>{cells}</tr>'
    return f"<table><tr><th>Gate</th>{head}</tr>{rows}</table>"


def supplier_section(r):
    s = SUPS[r["short"]]
    gates = "".join(
        f'<tr><td><b>{gid}</b></td><td style="white-space:nowrap">{" ".join(badge(gd.get(k, "unverified"), True) for k in C["scenarios"])}</td><td>{e(gd.get("note", ""))}</td></tr>'
        for gid, gd in s["gates"].items())
    rows = "".join(
        f'<tr><td>{x["id"]}</td><td>{e(x["name"])}</td><td class="num">{x["w"]}</td><td class="num">{x["score"]}</td>'
        f'<td>{badge(x["evidence"])}</td><td class="num">{x["adj"]}</td><td>{e(x.get("note", ""))}</td></tr>' for x in r["rows"])
    gaps = "".join(f'<li><b>{x["id"]} {e(x["name"])}</b>: {e(x.get("note", ""))}</li>' for x in r["gaps"])
    src = "".join(f"<li>{e(u)}</li>" for u in s["sources"])
    return f"""
<h2 class="pb">{e(s["name"])}</h2>
<p>{e(s["profile"])}</p>
<div class="kpis"><div class="kpi"><div class="v">{r["adjusted"]}</div><div class="l">Risk-adjusted score /100</div></div>
<div class="kpi"><div class="v">{r["evidence_coverage"]}%</div><div class="l">Weight backed by any evidence</div></div>
<div class="kpi"><div class="v">{" ".join(badge(r["gates"][k]) for k in C["scenarios"])}</div><div class="l">Gates: Plants / DCs / New plant</div></div></div>
<p><b>Role in recommendation:</b> {e(ROLE[r["short"]])}</p>
<h3>Knock-out gates (Plants · DCs · New plant)</h3>
<table><tr><th>Gate</th><th>Status</th><th>Evidence / gap</th></tr>{gates}</table>
<h3>Weighted scorecard</h3>
<table><tr><th>ID</th><th>Criterion</th><th>W</th><th>Score</th><th>Evidence</th><th>Pts</th><th>Basis</th></tr>{rows}</table>
<h3>Gaps to close before award (score ≤2 or unverified)</h3><ul>{gaps}</ul>
<h3>Sources</h3><ul class="src">{src}</ul>"""


html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Supplier Evaluation Criteria</title>
<link rel="stylesheet" href="style.css"></head><body>
<h1>Supplier Evaluation Criteria &amp; Scorecards</h1>
<div class="sub">Material-handling automation for Smithfield Foods North America — 36 plants, 4 DCs, new flagship plant (Sioux Falls, SD)</div>
<div class="meta">Global Solution Manager, China sourcing · 2026-10-11 · Companion: <code>supplier_scorecard.xlsx</code> (live formulas) and <code>tool/criteria.yaml</code> + <code>tool/score.py</code> (re-score any supplier)</div>

<div class="box"><b>Result.</b> Supplier A fails four of six knock-out gates in every scenario (4 m lift, no 1 t at height, no -18 °C, no cross-zone) and cannot serve the network.
No Chinese supplier publicly proves all DC gates; <b>VisionNav</b> is the only mobile candidate that is not excluded anywhere (CONDITIONAL on load-at-height, freezer and UL proof),
<b>Multiway</b> fails the DC gate on load at height (published 700–750 kg at 9.5–11 m), and <b>Inform</b> is the strongest storage-system candidate for the greenfield plant.
Scores are deliberately conservative: unverified evidence scores zero, so each supplier's gap to 100 is its RFQ work list.</div>

<h2>1. How to use this tool (reusable for any supplier)</h2>
<ol>
<li><b>Fix the scenario envelope.</b> Each site type is a scenario with binding height, load, temperature and cross-zone requirements (table 2). New sites add a row.</li>
<li><b>Apply knock-out gates per scenario.</b> A single FAIL excludes the supplier for that scenario regardless of score. UNVERIFIED or CLAIMED results make the supplier CONDITIONAL: it may proceed to RFQ but cannot be awarded until the gate is proven by datasheet and a witnessed test.</li>
<li><b>Score 15 weighted criteria 0–5</b> using the scoring guides (table 4). Each score carries an evidence level; the evidence multiplier (verified ×1.0, claimed ×0.7, unverified ×0) converts it into a risk-adjusted score. Information not provided is scored 0 and listed as a gap: never assumed.</li>
<li><b>Rank within role</b> (mobile vehicles vs fixed storage), then check the single-supplier question: does one supplier PASS or CONDITIONAL in every scenario? See logistics_solution.pdf.</li>
<li><b>Convert gaps into RFQ questions and witnessed tests</b> (Appendix). Re-score as evidence arrives; the XLSX recalculates automatically.</li>
</ol>

<h2>2. Scenarios and binding constraints</h2>
{scen_table()}
<p class="small">Sources: Smithfield brief; DC1 data (rack 12.3 m, top beam 10.46 m, 544–907 kg typical, 1,134 kg max, 40×48 in GMA grid-base pallets, chilled -2 °C / frozen -18 °C, 20 h/day). New-plant parameters are design variables; -25 °C is the recommended freezer set-point (see solution).</p>

<h2>3. Knock-out gates (technical and legal)</h2>
{gates_table()}

<h2>4. Weighted criteria: technical, commercial, risk &amp; governance (100 points)</h2>
{criteria_table()}
<p class="small">Weight rationale: technical fit 46 (the pilot failed on capability), commercial 35 (payback &lt;3 yrs is the group roll-out standard; North American service decides uptime across 41 sites), risk &amp; governance 19 (US tariffs on China-made industrial trucks, cybersecurity of connected fleet software, enforceable guarantees). Hikrobot was screened out before scoring: it is a Hikvision subsidiary, and Hikvision is on the US Entity List / FCC Covered List.</p>

<h2 class="pb">5. Results: Supplier A + three independently traceable candidates</h2>
{summary_table()}
<h3>Gate matrix (each cell: Plants · DCs · New plant)</h3>
<p class="small">Legend: PASS = verified on official source · FAIL = evidence shows non-compliance · CLM = claimed (vendor/trade press, not yet proven) · UNV = unverified / not provided.</p>
{gate_matrix()}
<div class="box warn"><b>Reading the scores.</b> Totals are low because the public record is thin, not because the suppliers are weak: risk-adjusted points are only earned with evidence.
"Evidence-only score" ignores the multiplier for claimed data (but still zeroes unverified items) to show upside if claims hold. Supplier A is scored only on what Smithfield's project document states;
everything else (certification, service, financials, cybersecurity, contract terms, hygiene) is <b>UNVERIFIED</b>.</div>

{"".join(supplier_section(r) for r in R)}

<h2 class="pb">Appendix: RFQ verification checklist (turns CONDITIONAL into PASS/FAIL)</h2>
<table><tr><th>Gate / criterion</th><th>Required evidence</th><th>Witnessed test</th></tr>
<tr><td>G1 + G2 height × load</td><td>Stamped load chart: residual capacity at 8.5 m and 10.46 m beam for a 1,134 kg 40×48 in load, load centre 24 in</td><td>Factory test: 20 put/pick cycles at 10.46 m with 1,134 kg; deflection and mast sway logged</td></tr>
<tr><td>G3 freezer</td><td>Rated operating range; battery heating; sensor/LiDAR/camera heater spec</td><td>72 h continuous duty in -18 °C chamber (-25 °C for new plant) incl. charging</td></tr>
<tr><td>G4 cross-zone</td><td>Condensation/frost mitigation design, dwell limits</td><td>50 transitions -18 °C ↔ +2 °C ↔ ambient with no navigation fault (only if vehicles are expected to cross zones)</td></tr>
<tr><td>G5 load carrier</td><td>Pallet detection spec for GMA grid-base, damaged-pallet handling</td><td>Run with 100 pallets drawn from DC1 inbound, incl. damaged ones</td></tr>
<tr><td>G6 safety</td><td>UL 3100 / UL 583 listing no. or NRTL report; B56.5 conformity; risk assessment</td><td>NRTL field evaluation at first US site</td></tr>
<tr><td>T2 throughput</td><td>Vendor simulation of DC1 flows (61 pal/h in + out, 59/41 chilled/frozen)</td><td>4-week pilot: ≥ simulated pal/h at ≥98 % availability</td></tr>
<tr><td>T5 integration</td><td>API docs, VDA 5050 conformity, Accellos/WMS adapter, read-only fallback via middleware</td><td>End-to-end task dispatch + status feedback in pilot</td></tr>
<tr><td>C2 service</td><td>US entity, technician count/locations, parts depot, SLA</td><td>Reference call with 2 US customers</td></tr>
<tr><td>R1 tariffs</td><td>Country of origin per HTS line; DDP tariff-inclusive price with change clause</td><td>Customs-broker ruling</td></tr>
<tr><td>R2 cyber</td><td>On-prem deployment option, SBOM, remote-access model, data-flow diagram, IEC 62443 mapping</td><td>Smithfield IT security review / pen-test</td></tr>
</table>
</body></html>"""

(ROOT.parent / "build/supplier_evaluation_criteria.html").write_text(html)
print("wrote build/supplier_evaluation_criteria.html")
