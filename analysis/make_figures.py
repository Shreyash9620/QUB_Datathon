"""
Generate all presentation figures (static PNGs) for the PRAVAAH deck.
Outputs -> analysis/outputs/figures/
Run:  python3 analysis/make_figures.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import geopandas as gpd
from pravaah_model import build_master, score_evidenced, allocate, WEIGHTS, BUDGET_CR

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "outputs")
FIG = os.path.join(OUT, "figures")
os.makedirs(FIG, exist_ok=True)

# Strategy palette (matches the hero visual)
C = {"BUILD": "#1D9E75", "UPGRADE": "#378ADD", "DISPERSE": "#BA7517", "EXPLORE": "#888780"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": "#888",
                     "axes.linewidth": 0.8, "figure.dpi": 150, "savefig.bbox": "tight"})


def scored_master():
    m = build_master()
    ev = score_evidenced(m[m.tier == "evidenced"])
    return m.merge(ev[["district", "E", "J", "I", "S", "archetype"]], on="district", how="left")


def strat_of(row, lev):
    if row["tier"] == "exploration":
        return "EXPLORE"
    d = lev.loc[row["district"]]
    key = d.idxmax()
    return {"new_capacity_cr": "BUILD", "quality_upgrade_cr": "UPGRADE",
            "dispersal_connectivity_cr": "DISPERSE", "skilling_sustainability_cr": "SKILL"}[key].replace("SKILL", "DISPERSE")


def fig_allocation(bal, lev):
    ev = bal[bal.tier == "evidenced"].sort_values("alloc_cr")
    strat = [strat_of(r, lev) for _, r in ev.iterrows()]
    colors = [C[s] for s in strat]
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.barh(ev["district"], ev["alloc_cr"], color=colors, height=0.7)
    for y, (_, r) in enumerate(ev.iterrows()):
        ax.text(r["alloc_cr"] + 8, y, f"₹{r['alloc_cr']:.0f} cr", va="center", fontsize=10, color="#222")
    ax.set_xlabel("Allocation (₹ crore)")
    ax.set_title("PRAVAAH allocation — evidenced districts (₹5,525 cr) + ₹975 cr exploration tranche",
                 fontsize=12, loc="left", pad=10)
    ax.set_xlim(0, 1050)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    legend = [Line2D([0], [0], color=C[k], lw=8, label=v) for k, v in
              [("BUILD", "Build new capacity"), ("UPGRADE", "Upgrade quality"), ("DISPERSE", "Protect & disperse")]]
    ax.legend(handles=legend, loc="lower right", frameon=False, fontsize=9)
    fig.savefig(os.path.join(FIG, "fig_allocation.png")); plt.close(fig)


def fig_quadrant(bal, lev):
    d = bal[bal.tier == "evidenced"].copy()
    d["hotels_plot"] = d["hotels"].replace(0, 0.6)  # so zero-hotel sits on the floor of a log axis
    strat = [strat_of(r, lev) for _, r in d.iterrows()]
    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.scatter(d["footfall_annual_lacs"], d["hotels_plot"],
               s=d["alloc_cr"] * 1.6, c=[C[s] for s in strat], alpha=0.8, edgecolor="white", linewidth=1.2, zorder=3)
    mx, my = d["footfall_annual_lacs"].median(), d["hotels"].median()
    ax.axvline(mx, color="#bbb", ls="--", lw=1); ax.axhline(my, color="#bbb", ls="--", lw=1)
    ax.set_yscale("log")
    off = {  # per-district label offset (dx, dy in points, ha) to avoid collisions
        "Ahmedabad": (8, 2, "left"), "Kachchh": (7, 9, "left"), "Surat": (-8, -15, "right"),
        "Gir Somnath": (8, 5, "left"), "Devbhoomi Dwarka": (8, 5, "left"),
        "Banaskantha": (9, -13, "left"), "Porbandar": (8, 3, "left"),
        "Mehsana": (-7, 13, "right"), "Panchmahal": (3, -19, "left"), "Kheda": (10, 13, "left"),
    }
    for _, r in d.iterrows():
        dx, dy, ha = off.get(r["district"], (6, 6, "left"))
        ax.annotate(r["district"], (r["footfall_annual_lacs"], r["hotels_plot"]),
                    xytext=(dx, dy), textcoords="offset points", fontsize=9, color="#333", ha=ha)
    ax.text(232, 0.83, "← white space\nhigh demand · no supply",
            fontsize=10.5, color=C["BUILD"], weight="bold", ha="left", va="center")
    ax.set_xlabel("Demand → annual footfall (Lacs)"); ax.set_ylabel("Supply → hotels (log scale)")
    ax.set_title("Demand vs supply — bubble size = ₹ allocation", fontsize=12, loc="left", pad=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(FIG, "fig_quadrant.png")); plt.close(fig)


def fig_robustness():
    r = pd.read_csv(os.path.join(OUT, "robustness_summary.csv"))
    r = r[r["std_cr"] > 0].sort_values("balanced_cr")  # evidenced tier only (exploration is weight-fixed)
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for y, (_, row) in enumerate(r.iterrows()):
        stable = row["p_top5_pct"] >= 80
        col = C["BUILD"] if stable else "#bbb"
        ax.plot([row["min_cr"], row["max_cr"]], [y, y], color=col, lw=3, solid_capstyle="round", zorder=2)
        ax.scatter(row["balanced_cr"], y, color="#222", s=28, zorder=3)
        ax.text(row["max_cr"] + 20, y, f"{row['p_top5_pct']:.0f}% top-5", va="center", fontsize=9,
                color=(C["BUILD"] if stable else "#999"))
    ax.set_yticks(range(len(r))); ax.set_yticklabels(r["district"])
    ax.set_xlabel("₹ allocation across 500 random weightings  (min–max range; dot = balanced)")
    ax.set_title("Robustness — the core stays put under any weighting", fontsize=12, loc="left", pad=10)
    ax.set_xlim(0, 2200)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(FIG, "fig_robustness.png")); plt.close(fig)


def fig_lever():
    lv = pd.read_csv(os.path.join(OUT, "lever_allocation.csv"))
    tot = lv[["new_capacity_cr", "quality_upgrade_cr", "dispersal_connectivity_cr", "skilling_sustainability_cr"]].sum()
    labels = ["Build new capacity", "Upgrade quality", "Protect & disperse", "Skilling & sustainability"]
    cols = [C["BUILD"], C["UPGRADE"], C["DISPERSE"], "#5DCAA5"]
    fig, ax = plt.subplots(figsize=(8.5, 2.4))
    left = 0
    for v, l, c in zip(tot, labels, cols):
        ax.barh(0, v, left=left, color=c, height=0.5)
        ax.text(left + v / 2, 0, f"{l}\n₹{v:,.0f} cr", ha="center", va="center", fontsize=9.5,
                color="white", weight="bold")
        left += v
    ax.set_xlim(0, left); ax.set_ylim(-0.5, 0.5); ax.axis("off")
    ax.set_title("How the ₹6,500 cr is spent — by investment lever", fontsize=12, loc="left", pad=8)
    fig.savefig(os.path.join(FIG, "fig_lever.png")); plt.close(fig)


def fig_frontier(m):
    pg, pi = np.array(WEIGHTS["pro_growth"]), np.array(WEIGHTS["pro_inclusion"])
    bal = np.array(WEIGHTS["balanced"])
    xs, ys = [], []
    for t in np.linspace(0, 1, 21):
        w = pg * (1 - t) + pi * t
        a = allocate(m, tuple(w))
        econ = (a["alloc_cr"] * a["E"].fillna(0) / 100).sum()
        incl = (a["alloc_cr"] * a["I"].fillna(0) / 100).sum()
        xs.append(incl); ys.append(econ)
    ab = allocate(m, "balanced")
    bx = (ab["alloc_cr"] * ab["I"].fillna(0) / 100).sum()
    by = (ab["alloc_cr"] * ab["E"].fillna(0) / 100).sum()
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.plot(xs, ys, "-o", color="#888", ms=4, lw=1.5, zorder=2)
    ax.scatter([xs[0]], [ys[0]], color=C["UPGRADE"], s=80, zorder=3, label="Pro-growth")
    ax.scatter([xs[-1]], [ys[-1]], color=C["BUILD"], s=80, zorder=3, label="Pro-inclusion")
    ax.scatter([bx], [by], color="#C0392B", s=120, marker="*", zorder=4, label="Balanced (chosen)")
    ax.set_xlabel("Inclusion captured (₹ × inclusion score)")
    ax.set_ylabel("Economic value captured (₹ × econ score)")
    ax.set_title("Efficient frontier — balanced is a deliberate trade-off", fontsize=12, loc="left", pad=10)
    ax.legend(frameon=False, fontsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(FIG, "fig_frontier.png")); plt.close(fig)


def fig_choropleth(bal):
    gdf = gpd.read_file(os.path.join(DATA, "gujarat_districts.geojson"))
    gdf["djoin"] = gdf["district"].replace({"Devbhumi Dwarka": "Devbhoomi Dwarka", "Kutch": "Kachchh"})
    gdf = gdf.merge(bal[["district", "alloc_cr", "tier"]], left_on="djoin", right_on="district", how="left")
    fig, ax = plt.subplots(figsize=(8, 8.4))
    gdf.plot(column="alloc_cr", cmap="YlGnBu", ax=ax, edgecolor="white", linewidth=0.6,
             legend=True, legend_kwds={"label": "₹ allocation (crore)", "shrink": 0.5},
             missing_kwds={"color": "#ececec", "edgecolor": "white", "label": "No data"})
    halo = [pe.withStroke(linewidth=2.6, foreground="white")]
    leader = {"Ahmedabad": (70.9, 21.7), "Kheda": (73.05, 24.0), "Panchmahal": (74.2, 23.6)}
    for _, r in gdf.iterrows():
        if pd.isna(r["alloc_cr"]) or r["alloc_cr"] < 300:
            continue
        c = r.geometry.representative_point()
        lbl = f"{r['djoin']}\n₹{r['alloc_cr']:.0f}"
        if r["djoin"] in leader:
            lx, ly = leader[r["djoin"]]
            ax.annotate(lbl, (c.x, c.y), xytext=(lx, ly), textcoords="data", ha="center",
                        fontsize=8.5, color="#11324a", weight="bold", path_effects=halo,
                        arrowprops=dict(arrowstyle="-", color="#555", lw=0.8))
        else:
            ax.annotate(lbl, (c.x, c.y), ha="center", fontsize=8.5, color="#11324a",
                        weight="bold", path_effects=halo)
    ax.set_title("Where the ₹6,500 cr lands — district allocation", fontsize=13, loc="left", pad=10)
    ax.axis("off")
    fig.savefig(os.path.join(FIG, "fig_choropleth.png")); plt.close(fig)


def main():
    m = scored_master()
    bal = allocate(m, "balanced")
    lev = pd.read_csv(os.path.join(OUT, "lever_allocation.csv")).set_index("district")
    fig_allocation(bal, lev)
    fig_quadrant(bal, lev)
    fig_robustness()
    fig_lever()
    fig_frontier(m)
    fig_choropleth(bal)
    print("Figures written to analysis/outputs/figures/:")
    for f in sorted(os.listdir(FIG)):
        print("  ", f)


if __name__ == "__main__":
    main()
