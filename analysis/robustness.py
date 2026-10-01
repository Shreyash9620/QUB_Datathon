"""
Monte-Carlo robustness for the PRAVAAH allocation — pre-empts the "arbitrary weights" critique.
Re-runs the allocator under 500 random objective-weight vectors and measures how stable each
district's budget and rank are. Two regimes:
  - full policy space : weights ~ Dirichlet(1,1,1,1)  (uniform over the whole simplex, stringent)
  - plausible band    : weights ~ Dirichlet(5,5,5,5)  (clustered near balanced, realistic)
Run:  python3 analysis/robustness.py
"""
import os
import numpy as np
import pandas as pd
from pravaah_model import build_master, score_evidenced, allocate, BUDGET_CR

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
N = 500
SEED = 42


def prep():
    m = build_master()
    ev = score_evidenced(m[m.tier == "evidenced"])
    return m.merge(ev[["district", "E", "J", "I", "S", "archetype"]], on="district", how="left")


def simulate(m, alpha, n=N, seed=SEED):
    rng = np.random.default_rng(seed)
    allocs = {d: [] for d in m.district}
    ranks = {d: [] for d in m.district}
    for _ in range(n):
        w = rng.dirichlet(alpha)
        a = allocate(m, tuple(w)).sort_values("alloc_cr", ascending=False).reset_index(drop=True)
        a["rank"] = a.index + 1
        for _, r in a.iterrows():
            allocs[r.district].append(r.alloc_cr)
            ranks[r.district].append(r["rank"])
    rows = []
    for d in allocs:
        arr, rk = np.array(allocs[d]), np.array(ranks[d])
        rows.append(dict(district=d, mean_cr=round(arr.mean(), 1), std_cr=round(arr.std(), 1),
                         min_cr=round(arr.min(), 1), max_cr=round(arr.max(), 1),
                         cv_pct=round(100 * arr.std() / arr.mean(), 1) if arr.mean() else np.nan,
                         p_top5_pct=round(100 * (rk <= 5).mean(), 1),
                         best_rank=int(rk.min()), worst_rank=int(rk.max())))
    return pd.DataFrame(rows).sort_values("mean_cr", ascending=False).reset_index(drop=True)


def main():
    m = prep()
    full = simulate(m, [1, 1, 1, 1])
    band = simulate(m, [5, 5, 5, 5])
    base = allocate(m, "balanced").set_index("district")["alloc_cr"]

    out = full.copy()
    out["balanced_cr"] = out["district"].map(base).round(0)
    out["p_top5_band_pct"] = out["district"].map(dict(zip(band.district, band.p_top5_pct)))
    out["cv_band_pct"] = out["district"].map(dict(zip(band.district, band.cv_pct)))
    out.to_csv(os.path.join(OUT, "robustness_summary.csv"), index=False)

    pd.set_option("display.width", 200)
    print("=" * 88)
    print(f"PRAVAAH ROBUSTNESS  —  {N} Monte-Carlo weightings  (full policy space, Dirichlet[1,1,1,1])")
    print("=" * 88)
    cols = ["district", "balanced_cr", "mean_cr", "std_cr", "min_cr", "max_cr", "cv_pct", "p_top5_pct", "best_rank", "worst_rank"]
    print(out[out.balanced_cr > 0][cols].head(12).to_string(index=False))
    print("-" * 88)
    ev = out[out.district.isin(m[m.tier == "evidenced"].district)]
    stable = ev[ev.p_top5_pct >= 80]
    print(f"Districts top-5 in >=80% of random weightings : {list(stable.district)}")
    print(f"Mean coeff. of variation (evidenced ₹)        : {ev.cv_pct.mean():.1f}%  (full space)  |  {out['cv_band_pct'].dropna().mean():.1f}%  (plausible band)")
    print(f"\nInterpretation: low CV + high P(top-5) => the recommendation is weight-invariant, not cherry-picked.")
    print("Written: analysis/outputs/robustness_summary.csv")


if __name__ == "__main__":
    main()
