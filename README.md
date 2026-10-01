# QUB GIFT City Datathon 2026 — Tourism for Inclusive Growth in Gujarat

> **The challenge:** Where should Gujarat invest its **₹6,500 crore** tourism budget to
> maximise economic development, employment creation, regional inclusion and
> environmental sustainability?

Gujarat is India's **3rd-highest** receiver of foreign tourists and has declared
2026/2027 the *"Year of Tourism"* — but on-the-ground experiences at sites are uneven.
The task: turn the three datasets below into a defensible investment recommendation.

---

## 📁 Folder structure

```
QUB_Datathon/
├── data/
│   ├── hotels.csv                  # 2,365 hotels — accommodation SUPPLY
│   ├── tourism_statistics.csv      # 20 rows — tourist footfall DEMAND
│   ├── socio_economic.csv          # 32 districts — inclusion / CONTEXT
│   ├── data_dictionary.xlsx        # column defs, metadata, cleaning log
│   └── source_hotels_gujarat.xlsx  # original raw workbook (untouched)
├── challenge_brief.pdf             # the official brief
├── prepare_data.py                 # reproducible cleaning script
└── README.md
```

All three CSVs were derived from the single source workbook by `prepare_data.py`.
Re-create them anytime with: `python3 prepare_data.py`

---

## 🔑 The one thing that makes this dataset work: `district`

The three files were originally **not joinable** — hotels list tourist *sites*
("Somnath", "Bhuj", "Ambaji"), tourism uses ALL-CAPS district names ("MAHESANA"),
and the census uses yet another spelling ("Mehsana"). Every file now carries a
harmonised **`district`** key so they join cleanly:

```python
import pandas as pd
hotels  = pd.read_csv("data/hotels.csv")
tourism = pd.read_csv("data/tourism_statistics.csv")
socio   = pd.read_csv("data/socio_economic.csv")

districts = tourism[tourism.category == "district"]
joined = (districts.rename(columns={"join_district": "district"})
          .merge(hotels.groupby("district").size().rename("n_hotels"), on="district", how="left")
          .merge(socio, on="district", how="left"))
```

✅ Verified: **100% of hotel and tourism districts map to a census district.**

---

## 📊 The datasets

| File | Grain | What it tells you | Key columns |
|---|---|---|---|
| `hotels.csv` | 1 row / hotel | Accommodation **supply**, price, quality | `rating`, `actual_price`, `discount_pct`, `facilities`, `district` |
| `tourism_statistics.csv` | 1 row / ranked place | Visitor **demand** (footfall) | `category` (destination/district), `rank`, `footfall_annual_lacs`, `join_district` |
| `socio_economic.csv` | 1 row / district | **Inclusion** context (2011 Census) | `population_2011`, `density_per_km2`, `sex_ratio_f_per_1000m`, `literacy_rate_pct` |

**State context (metadata):** total footfall Apr 2025–Feb 2026 = **2,090.42 Lacs**
(~209M visits); March 2026 = 180.87 Lacs. *Unit: 1 Lac = 100,000 visits.*

---

## 🧹 Data cleaning applied (see `data_dictionary.xlsx → Cleaning_log`)

- **hotels:** repaired 1 column-shifted row (*The Fern Residency*); coerced price/rating
  to numeric; 751 `"Not Available"` → blank; normalised facility casing; added
  `discount_pct` and the `district` join key.
- **tourism:** un-stacked 4 tables crammed in one sheet into a tidy long format;
  mapped district names to census spelling.
- **socio:** fixed **Surat density 1.337 → 1337** (thousands-separator parse error);
  `"85.31%"` → numeric `85.31`; stripped footnote markers from the district column.

---

## 💡 Starter insight — demand vs. supply gap (already computed)

Joining footfall (demand) against hotel count (supply) surfaces the investment story:

| District | Annual footfall (Lacs) | Hotels | Visits/hotel | Literacy % | Read |
|---|--:|--:|--:|--:|---|
| **Banaskantha** (Ambaji) | 189.6 | 61 | 310,770 | **65.3** | Huge demand, thin supply, **poorest district** → inclusive-growth flagship |
| **Devbhoomi Dwarka** | 259.2 | 92 | 281,739 | 74.3 | Pilgrimage hub, undersupplied |
| **Kheda / Panchmahal / Mehsana** | 79–173 | **0** | — | 71–83 | Top-10 footfall, **no hotels in data** → greenfield supply gap |
| Surat / Kachchh / Ahmedabad | 72–410 | 282–481 | 25k–85k | 71–86 | Already well-supplied (lower priority) |

> The budget question isn't "where do tourists go?" — it's **"where does demand
> outstrip supply *in districts that also need the development?*"** That's the
> intersection of all three datasets.

---

## 🎯 Suggested directions (mapped to the evaluation criteria)

| Approach | Idea | Hits criteria |
|---|---|---|
| **Geographic** | Map footfall vs hotel density to rank under-served districts | Insight, Evidence |
| **Financial** | Allocate ₹6,500 cr by a demand/supply/inclusion score; estimate jobs created | Feasibility, Social impact |
| **Predictive** | Model footfall from socio-economic + supply features; find growth headroom | Analysis quality, Innovation |
| **Statistical** | Test whether literacy / sex-ratio correlate with tourism intensity | Analysis quality |
| **Inclusion lens** | Weight investment toward low-literacy / low-density districts with demand | Social impact, Regional inclusion |

**Deliverable:** a 5-minute presentation — problem, methodology, insights,
implications, recommendations.

---
*Folder prepared from `hotels_gujarat.xlsx`. Sources: commissionertourism.gujarat.gov.in
(footfall) and the 2011 Census of India.*
