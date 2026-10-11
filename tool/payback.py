"""DC payback model for end-to-end (dock -> rack -> dock) mobile automation, plus sanity checks.

All inputs are explicit assumptions (A) or site data from the brief (S). Re-run with a site's own
numbers to rank retrofit waves. Usage: uv run python tool/payback.py
"""
import json
import math
from pathlib import Path

BASE = {
    # --- site data (S): DC1 from the Smithfield site document
    "inbound_pal_h": 61.0,            # S: 1,220 pal/day over 20 h
    "chilled_share": 0.59,            # S
    "outbound_ratio": 1.0,            # A: steady-state DC, outbound ≈ inbound
    # --- automation (A, to be replaced by vendor simulation)
    "agv_pal_h": 9.0,                 # dock-to-rack cycles/h at up to 10.5 m
    "availability_buffer": 1.15,      # charging + maintenance + peaks
    "agv_landed_usd": 185_000,        # per freezer-capable high-reach AGV, DDP incl. tariffs
    "integration_usd": 1_100_000,     # WES/middleware, WMS interface, network, safety, airlock P&D conveyors
    "project_pct": 0.10,              # PM, commissioning, training
    "service_pct": 0.06,              # annual service contract as % of vehicle capex
    "software_usd_per_agv": 3_000,    # annual fleet-software support
    # --- manual baseline (A)
    "manual_pal_h": 12.0,             # reach-truck driver, dock-to-rack incl. travel
    "freezer_productivity": 0.80,     # cold-stress warm-up breaks at -18 °C
    "fte_per_position": 2.4,          # 2 shifts x 1.2 coverage (6-day ops, relief, absence)
    "loaded_cost_usd": 68_000,        # per FTE/yr, wage + burden
    "retained_fte": 2.4,              # one AGV supervisor / exception handler per shift
    "truck_cost_usd": 18_000,         # per avoided reach truck/yr (lease, maintenance, battery)
    "damage_savings_usd": 50_000,     # rack/product damage avoided per year
}

SENSITIVITY = {
    "agv_landed_usd": (150_000, 240_000),
    "agv_pal_h": (11.0, 7.0),
    "loaded_cost_usd": (78_000, 58_000),
    "manual_pal_h": (10.0, 14.0),
    "integration_usd": (800_000, 1_600_000),
}


def model(p):
    moves = p["inbound_pal_h"] * (1 + p["outbound_ratio"])
    chilled, frozen = moves * p["chilled_share"], moves * (1 - p["chilled_share"])
    # zone-dedicated fleets: vehicles never cross zones (airlock conveyor hand-off)
    fleet = sum(math.ceil(m / p["agv_pal_h"] * p["availability_buffer"]) for m in (chilled, frozen))
    positions = chilled / p["manual_pal_h"] + frozen / (p["manual_pal_h"] * p["freezer_productivity"])
    fte_saved = positions * p["fte_per_position"] - p["retained_fte"]
    trucks = math.ceil(positions * 1.1)
    veh_capex = fleet * p["agv_landed_usd"]
    capex = (veh_capex + p["integration_usd"]) * (1 + p["project_pct"])
    savings = fte_saved * p["loaded_cost_usd"] + trucks * p["truck_cost_usd"] + p["damage_savings_usd"]
    opex = veh_capex * p["service_pct"] + fleet * p["software_usd_per_agv"]
    net = savings - opex
    # break-even landed price per AGV for a 3.0-year payback
    max_price = (3.0 * net / (1 + p["project_pct"]) - p["integration_usd"]) / fleet
    # (approximation: ignores service cost scaling with price; conservative within ±3 %)
    return {
        "moves_h": round(moves, 1), "fleet": fleet, "manual_positions": round(positions, 1),
        "fte_saved": round(fte_saved, 1), "capex": round(capex), "annual_savings": round(savings),
        "annual_opex": round(opex), "net_annual": round(net), "payback_yrs": round(capex / net, 2),
        "max_landed_price_for_3yr": round(max_price, -3),
    }


def supplier_a_check():
    """Back-solve what Supplier A's 3.9-yr payback implies — shows the horizontal-only savings ceiling."""
    chilled_moves = 36.0                      # S: AGVs serve chilled inbound only
    tug_pal_h = 20.0                          # A: manual horizontal move with pallet jack/forklift
    positions = chilled_moves / tug_pal_h
    savings = positions * BASE["fte_per_position"] * BASE["loaded_cost_usd"]
    implied_capex = savings * 3.9
    return {
        "chilled_moves_h": chilled_moves, "positions_replaced": round(positions, 1),
        "annual_savings": round(savings), "implied_all_in_capex": round(implied_capex, -3),
        "implied_per_agv": round(implied_capex / 10, -3),
        "fleet_capacity_now_pal_h": 10 * 4.5, "fleet_capacity_clear_routes_pal_h": 10 * 6.2,
        "units_needed_at_6_2": math.ceil(chilled_moves / 6.2 * BASE["availability_buffer"]),
    }


def plant1_check():
    demand_h = 400 / 16.5
    return {
        "demand_pal_h": round(demand_h, 1),
        "stated_capacity_pal_h": 7 * 21,
        "stated_utilisation_pct": round(demand_h / (7 * 21) * 100),
        "implied_speed_m_s": round(2 * 288.6 / (3600 / 21 - 60), 1),  # 60 s pick/drop handling
        "if_21_is_fleet_rate_pal_day": round(21 * 16.5),
        "units_needed_at_8_pal_h": math.ceil(demand_h / 8 * BASE["availability_buffer"]),
    }


if __name__ == "__main__":
    base = model(BASE)
    sens = []
    for k, (good, bad) in SENSITIVITY.items():
        lo, hi = model(BASE | {k: good})["payback_yrs"], model(BASE | {k: bad})["payback_yrs"]
        sens.append({"param": k, "good": good, "bad": bad, "payback_good": lo, "payback_bad": hi})
    out = {"inputs": BASE, "base": base, "sensitivity": sens,
           "supplier_a": supplier_a_check(), "plant1": plant1_check()}
    Path("build").mkdir(exist_ok=True)
    Path("build/payback.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
