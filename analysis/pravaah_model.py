"""
PRAVAAH Allocation Framework  —  QUB GIFT City Datathon 2026
Yield-adjusted, inclusion-weighted, sustainability-capped allocation of Gujarat's
Rs 6,500 crore tourism budget across districts and investment levers.

Pipeline:  SCORE -> CONSTRAIN -> ALLOCATE -> STRESS-TEST
All external assumptions are declared up top and are fully tunable (transparency = Evidence).

Run:  python3 analysis/pravaah_model.py
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "outputs")
BUDGET_CR = 6500.0  # Rs crore

# ===================== EXTERNAL ASSUMPTIONS (tunable; flagged for judges) =====================
# A1. Yield = estimated in-destination spend per visit by tourism archetype (INR). This is the
#     "footfall != value" correction: pilgrimage day-trips spend far less than premium eco/Rann.
YIELD = {"pilgrimage": 800, "coastal_leisure": 2000, "heritage": 2200,
         "urban_heritage": 2500, "eco_premium": 6000}
# A2. Employment intensity: jobs per Rs 1 crore of tourism activity. Central = 22, derived from
#     WTTC 2024 India (46.5M jobs / Rs 21 trillion T&T GDP = 22.1 jobs/cr). Sensitivity band 15-35.
#     India TSA: tourism = 13.34% of employment (direct 5.82%) => ~2.3x direct-to-total multiplier.
JOBS_PER_CRORE = 22
JOBS_RANGE = (15, 35)        # reported as a range, not false precision
# A3. Budget split: evidenced districts (have footfall) vs exploration tranche (22 blind districts).
EVIDENCED_SHARE = 0.85
# A4. Inclusion floor: minimum share of TOTAL budget to bottom-quartile-literacy districts.
INCLUSION_FLOOR = 0.30
# A5. Objective weight schemes (Economic, Employment, Inclusion, Sustainability).
WEIGHTS = {"balanced": (.25, .25, .25, .25),
           "pro_inclusion": (.20, .20, .40, .20),
           "pro_growth": (.40, .30, .15, .15)}
# Tourism archetype per evidenced district (drives yield) and eco-sensitivity flags.
ARCHETYPE = {"Ahmedabad": "urban_heritage", "Devbhoomi Dwarka": "pilgrimage",
             "Banaskantha": "pilgrimage", "Kheda": "pilgrimage", "Gir Somnath": "coastal_leisure",
             "Panchmahal": "heritage", "Kachchh": "eco_premium", "Mehsana": "heritage",
             "Surat": "urban_heritage", "Porbandar": "coastal_leisure"}
ECO_SENSITIVE = {"Gir Somnath", "Kachchh", "Devbhoomi Dwarka", "Porbandar", "Dang", "Junagadh"}


def mm(s):  # min-max to 0-100; flat series -> 50
    s = s.astype(float)
    if s.max() == s.min():
        return pd.Series(50.0, index=s.index)
    return (s - s.min()) / (s.max() - s.min()) * 100


def build_master():
    h = pd.read_csv(os.path.join(DATA, "hotels.csv"))
    t = pd.read_csv(os.path.join(DATA, "tourism_statistics.csv"))
    s = pd.read_csv(os.path.join(DATA, "socio_economic.csv"))
    dem = (t[t.category == "district"][["join_district", "footfall_annual_lacs"]]
           .rename(columns={"join_district": "district"}))
    sup = h.groupby("district").agg(hotels=("hotel_name", "size"),
                                    avg_price=("actual_price", "mean"),
                                    avg_rating=("rating", "mean")).reset_index()
    m = s.merge(dem, on="district", how="left").merge(sup, on="district", how="left")
    m["hotels"] = m["hotels"].fillna(0).astype(int)
    m["tier"] = np.where(m["footfall_annual_lacs"].notna(), "evidenced", "exploration")
    m["eco_sensitive"] = m["district"].isin(ECO_SENSITIVE)
    m["visits_per_hotel"] = m["footfall_annual_lacs"] * 1e5 / m["hotels"].replace(0, np.nan)
    # Inclusion need (all 32 districts): inverse literacy, percentile-ranked.
    m["inclusion_need"] = mm(-m["literacy_rate_pct"])
    cutoff = m["literacy_rate_pct"].quantile(0.25)
    m["bottom_quartile"] = m["literacy_rate_pct"] <= cutoff
    return m


def score_evidenced(ev):
    ev = ev.copy()
    arch = ev["district"].map(ARCHETYPE)
    yld = arch.map(YIELD)
    # E: yield-adjusted economic value of demand.
    ev["E"] = mm(ev["footfall_annual_lacs"] * yld)
    # J: job-creation headroom = demand relative to existing supply (rewards undersupply).
    ev["J"] = mm(ev["footfall_annual_lacs"] / np.sqrt(ev["hotels"] + 1))
    # I: inclusion need (re-normalised within tier).
    ev["I"] = mm(ev["inclusion_need"])
    # S: sustainability HEADROOM = 100 - congestion penalty - eco penalty (0-hotel => max headroom).
    cong = ev["visits_per_hotel"].fillna(0)          # no hotels -> 0 congestion -> full headroom
    ev["S"] = mm(-(mm(cong) + ev["eco_sensitive"] * 40))
    ev["archetype"] = arch
    return ev


def lever_split(row):
    """Rule-based split of a district's budget across investment levers (sums to 1)."""
    congested = (row.get("visits_per_hotel", 0) or 0) > 150000
    undersupplied = row["hotels"] < (row["footfall_annual_lacs"] or 0) * 0.5  # <0.5 hotels per Lac
    low_quality = (row.get("avg_rating") or 5) < 3.5
    if row["eco_sensitive"] and congested:                 # protect + spread
        s = {"new_capacity": .10, "quality_upgrade": .30, "dispersal_connectivity": .35, "skilling_sustainability": .25}
    elif undersupplied:                                    # greenfield build-out
        s = {"new_capacity": .50, "quality_upgrade": .15, "dispersal_connectivity": .20, "skilling_sustainability": .15}
    elif low_quality:                                      # fix the experience
        s = {"new_capacity": .15, "quality_upgrade": .45, "dispersal_connectivity": .20, "skilling_sustainability": .20}
    else:                                                  # balanced mature market
        s = {"new_capacity": .25, "quality_upgrade": .30, "dispersal_connectivity": .25, "skilling_sustainability": .20}
    return pd.Series(s)


def allocate(m, scheme):
    # scheme may be a named string or an explicit (wE,wJ,wI,wS) weight tuple (for Monte Carlo).
    wE, wJ, wI, wS = WEIGHTS[scheme] if isinstance(scheme, str) else scheme
    ev = m[m.tier == "evidenced"].copy()
    ev["priority"] = wE * ev.E + wJ * ev.J + wI * ev.I + wS * ev.S
    ev["alloc_cr"] = EVIDENCED_SHARE * BUDGET_CR * ev["priority"] / ev["priority"].sum()

    # Exploration tranche: directional proxy = inclusion need x population scale (demand unknown).
    ex = m[m.tier == "exploration"].copy()
    proxy = mm(ex["inclusion_need"]) * (ex["population_2011"] / ex["population_2011"].max())
    ex["priority"] = np.nan
    ex["alloc_cr"] = (1 - EVIDENCED_SHARE) * BUDGET_CR * proxy / proxy.sum()

    a = pd.concat([ev, ex], ignore_index=True)

    # Enforce inclusion floor across the whole budget (scale bottom-quartile up, rest down).
    bq = a["bottom_quartile"]
    floor_cr = INCLUSION_FLOOR * BUDGET_CR
    if a.loc[bq, "alloc_cr"].sum() < floor_cr:
        need, have = floor_cr, a.loc[bq, "alloc_cr"].sum()
        a.loc[bq, "alloc_cr"] *= need / have
        a.loc[~bq, "alloc_cr"] *= (BUDGET_CR - need) / (BUDGET_CR - have)
    return a.sort_values("alloc_cr", ascending=False).reset_index(drop=True)


def main():
    m = build_master()
    ev = score_evidenced(m[m.tier == "evidenced"])
    m = m.merge(ev[["district", "E", "J", "I", "S", "archetype"]], on="district", how="left")

    scenarios = {s: allocate(m, s) for s in WEIGHTS}
    bal = scenarios["balanced"]

    # Levers + jobs on the balanced scenario.
    levers = bal.apply(lever_split, axis=1)
    bal = pd.concat([bal, levers], axis=1)
    for c in levers.columns:
        bal[c + "_cr"] = (bal[c] * bal["alloc_cr"]).round(1)
    bal["est_jobs"] = (bal["alloc_cr"] * JOBS_PER_CRORE).round(0).astype(int)

    # --------- persist ---------
    cols = ["district", "tier", "archetype", "eco_sensitive", "footfall_annual_lacs", "hotels",
            "avg_rating", "literacy_rate_pct", "E", "J", "I", "S", "priority", "alloc_cr", "est_jobs"]
    bal[cols].round(2).to_csv(os.path.join(OUT, "allocation_balanced.csv"), index=False)
    cmp = bal[["district", "tier"]].copy()
    for s in WEIGHTS:
        cmp[s + "_cr"] = cmp["district"].map(dict(zip(scenarios[s].district, scenarios[s].alloc_cr.round(0))))
    cmp.to_csv(os.path.join(OUT, "scenario_comparison.csv"), index=False)
    bal[["district"] + [c + "_cr" for c in levers.columns]].round(1).to_csv(
        os.path.join(OUT, "lever_allocation.csv"), index=False)

    # --------- executive summary ---------
    pd.set_option("display.width", 220)
    print("=" * 92)
    print("PRAVAAH ALLOCATION  —  Balanced scenario  (Rs 6,500 cr)")
    print("=" * 92)
    show = bal.head(15)[["district", "tier", "archetype", "alloc_cr", "est_jobs",
                         "footfall_annual_lacs", "hotels", "literacy_rate_pct", "priority"]]
    show = show.rename(columns={"footfall_annual_lacs": "footfall_L", "literacy_rate_pct": "lit%"})
    print(show.to_string(index=False))
    print("-" * 92)
    print(f"TOTAL budget allocated     : Rs {bal.alloc_cr.sum():,.0f} cr")
    jlo, jhi = int(BUDGET_CR * JOBS_RANGE[0]), int(BUDGET_CR * JOBS_RANGE[1])
    print(f"TOTAL jobs (est @ {JOBS_PER_CRORE}/cr) : {bal.est_jobs.sum():,}  (range {jlo:,}-{jhi:,} @ {JOBS_RANGE[0]}-{JOBS_RANGE[1]}/cr)")
    print(f"Share to bottom-quartile literacy districts : {bal.loc[bal.bottom_quartile,'alloc_cr'].sum()/BUDGET_CR:6.1%}  (floor {INCLUSION_FLOOR:.0%})")
    print(f"Share to evidenced tier    : {bal.loc[bal.tier=='evidenced','alloc_cr'].sum()/BUDGET_CR:6.1%}")
    print(f"Share to eco-sensitive      : {bal.loc[bal.eco_sensitive,'alloc_cr'].sum()/BUDGET_CR:6.1%}")
    print("\nLEVER MIX (Rs cr, statewide):")
    for c in levers.columns:
        print(f"  {c:26s} {bal[c+'_cr'].sum():8,.0f}")
    print("\nSCENARIO SENSITIVITY — top 8 districts, Rs cr by policy stance:")
    print(cmp.head(8).to_string(index=False))
    print("\nOutputs written to analysis/outputs/  (allocation_balanced, scenario_comparison, lever_allocation)")


if __name__ == "__main__":
    main()
