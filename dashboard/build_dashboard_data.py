"""
Build the dashboard data layer from the FROZEN PRAVAAH outputs.
- Exports the two referenced-but-missing CSVs (frontier_points, quadrant_data).
- Emits dashboard/data.js (window.PRAVAAH = {...}) so the dashboard runs from file:// with no server.
No re-modelling: every number is read/derived from the frozen engine outputs.
Run:  python3 dashboard/build_dashboard_data.py
"""
import os, sys, json
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "analysis", "outputs")
DASH = os.path.join(ROOT, "dashboard")
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from pravaah_model import build_master, score_evidenced, allocate, WEIGHTS, BUDGET_CR, JOBS_PER_CRORE  # noqa

ECO = {"Gir Somnath", "Kachchh", "Devbhoomi Dwarka", "Porbandar", "Dang", "Junagadh"}
HIGHLIGHT = {"Panchmahal", "Kheda", "Mehsana"}
LEVCOLS = ["new_capacity_cr", "quality_upgrade_cr", "dispersal_connectivity_cr", "skilling_sustainability_cr"]
LEVLABELS = ["Build", "Upgrade", "Protect & disperse", "Skilling & sustainability"]
DOM = dict(zip(LEVCOLS, ["Build", "Upgrade", "Protect & disperse", "Skilling"]))

m = build_master()
ev = score_evidenced(m[m.tier == "evidenced"])
m = m.merge(ev[["district", "E", "J", "I", "S", "archetype"]], on="district", how="left")
m["lowlit"] = m["literacy_rate_pct"] <= m["literacy_rate_pct"].quantile(0.25)
m["eco"] = m["district"].isin(ECO)
meta = m.set_index("district")

# ---------- export quadrant_data.csv ----------
lev = pd.read_csv(os.path.join(OUT, "lever_allocation.csv")).set_index("district")
fracs = lev[LEVCOLS].div(lev[LEVCOLS].sum(axis=1), axis=0).fillna(0)
bal = allocate(m, "balanced").set_index("district")
qd = m[m.tier == "evidenced"][["district", "footfall_annual_lacs", "hotels"]].copy()
qd["alloc_cr"] = qd["district"].map(bal["alloc_cr"]).round().astype(int)
qd["strategy"] = qd["district"].apply(lambda d: DOM[lev.loc[d, LEVCOLS].idxmax()] if d in lev.index else "Explore")
qd["highlight"] = qd["district"].isin(HIGHLIGHT)
qd.to_csv(os.path.join(OUT, "quadrant_data.csv"), index=False)

# ---------- export frontier_points.csv ----------
pg, pi = np.array(WEIGHTS["pro_growth"]), np.array(WEIGHTS["pro_inclusion"])
fr = []
for t in np.linspace(0, 1, 21):
    a = allocate(m, tuple(pg * (1 - t) + pi * t))
    fr.append({"t": round(float(t), 3),
               "econ": round(float((a["alloc_cr"] * a["E"].fillna(0) / 100).sum()), 1),
               "incl": round(float((a["alloc_cr"] * a["I"].fillna(0) / 100).sum()), 1)})
pd.DataFrame(fr).to_csv(os.path.join(OUT, "frontier_points.csv"), index=False)

# ---------- per-scenario blocks ----------
sc = pd.read_csv(os.path.join(OUT, "scenario_comparison.csv"))
SCEN = {"Balanced": "balanced_cr", "Pro-Growth": "pro_growth_cr", "Pro-Inclusion": "pro_inclusion_cr"}


def scen_block(name):
    s = sc[["district", SCEN[name]]].rename(columns={SCEN[name]: "cr"}).copy()
    s["cr"] = s["cr"].round()
    s["E"] = s["district"].map(meta["E"]).fillna(0)
    s["lowlit"] = s["district"].map(meta["lowlit"])
    s["eco"] = s["district"].map(meta["eco"])
    s = s.sort_values("cr", ascending=False).reset_index(drop=True)
    total = s["cr"].sum()
    levtot = {lab: 0.0 for lab in LEVLABELS}
    for _, r in s.iterrows():
        d = r["district"]
        f = fracs.loc[d] if d in fracs.index else None
        for c, lab in zip(LEVCOLS, LEVLABELS):
            levtot[lab] += r["cr"] * (f[c] if f is not None else {"new_capacity_cr": .30, "quality_upgrade_cr": .20,
                                                                   "dispersal_connectivity_cr": .20, "skilling_sustainability_cr": .30}[c])
    districts = [{"d": r["district"], "cr": int(r["cr"]), "jobs": int(round(r["cr"] * JOBS_PER_CRORE)),
                  "lowlit": bool(r["lowlit"]), "eco": bool(r["eco"])} for _, r in s.iterrows()]
    return {
        "jobs": int(round(total * JOBS_PER_CRORE)),
        "inclusionPct": round(100 * s.loc[s["lowlit"], "cr"].sum() / total, 1),
        "econIndex": round((s["cr"] * s["E"]).sum() / total, 1),
        "ecoProtectedCr": int(round(s.loc[s["eco"], "cr"].sum())),
        "levers": {k: int(round(v)) for k, v in levtot.items()},
        "districts": districts,
    }


# ---------- quadrant + robustness for JS ----------
quadrant = [{"d": r.district, "footfall": round(float(r.footfall_annual_lacs), 1), "hotels": int(r.hotels),
             "alloc": int(r.alloc_cr), "strategy": r.strategy, "highlight": bool(r.highlight)}
            for r in qd.itertuples()]
rob = pd.read_csv(os.path.join(OUT, "robustness_summary.csv"))
rob = rob[rob["std_cr"] > 0].sort_values("balanced_cr", ascending=False)
robustness = [{"d": r.district, "pTop5": round(float(r.p_top5_pct), 0), "balanced": int(round(r.balanced_cr)),
               "min": int(round(r.min_cr)), "max": int(round(r.max_cr)), "stable": bool(r.p_top5_pct >= 80)}
              for r in rob.itertuples()]

DATA = {
    "updated": "2026-06-12",
    "budget": int(BUDGET_CR),
    "jobsPerCr": int(JOBS_PER_CRORE),
    "ecoDistricts": len(ECO),
    "scenarioMeta": {
        "Balanced": {"tag": "Recommended", "blurb": "Equal weight on all four objectives.", "accent": "teal"},
        "Pro-Growth": {"tag": "Higher economic returns", "blurb": "Tilts to yield & high-demand corridors.", "accent": "amber"},
        "Pro-Inclusion": {"tag": "Greater regional equity", "blurb": "Tilts to low-literacy, under-served districts.", "accent": "teal"},
    },
    "scenarios": {n: scen_block(n) for n in SCEN},
    "quadrant": quadrant,
    "robustness": robustness,
    "frontier": fr,
}

with open(os.path.join(DASH, "data.js"), "w") as f:
    f.write("// Auto-generated from frozen PRAVAAH outputs by build_dashboard_data.py — do not edit by hand.\n")
    f.write("window.PRAVAAH = " + json.dumps(DATA, indent=2) + ";\n")

print("Wrote dashboard/data.js")
for n, b in DATA["scenarios"].items():
    print(f"  {n:14s} jobs={b['jobs']:,} inclusion={b['inclusionPct']}% econIdx={b['econIndex']} eco₹={b['ecoProtectedCr']} top={b['districts'][0]['d']} {b['districts'][0]['cr']}")
print("Exported quadrant_data.csv + frontier_points.csv")
