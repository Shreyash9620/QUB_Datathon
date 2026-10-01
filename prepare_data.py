"""
prepare_data.py  —  QUB GIFT City Datathon 2026: "Tourism for Inclusive Growth in Gujarat"

Splits the source workbook (hotels_gujarat.xlsx) into three clean, analysis-ready,
*joinable* CSVs plus a data dictionary. Every cleaning step is logged so the
transformation is fully reproducible and auditable (evidence/feasibility criteria).

Source workbook sheets:
    final_hotel_dataset      -> data/hotels.csv
    Gujarat Tourism Data     -> data/tourism_statistics.csv   (tidied from 4 stacked tables)
    Gujarat 2011 Census Data -> data/socio_economic.csv

Run:  python3 prepare_data.py
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "data", "source_hotels_gujarat.xlsx")
DATA = os.path.join(HERE, "data")
CLEAN_LOG = []  # (dataset, action) tuples for the data dictionary


def log(dataset, action):
    CLEAN_LOG.append((dataset, action))
    print(f"  [{dataset}] {action}")


# --------------------------------------------------------------------------------------
# District harmonisation — the analytical bridge across all three datasets.
# Hotel "destination name" values are tourist SITES/cities; map them to census districts
# so hotels, tourism footfall and socio-economic indicators can be joined on `district`.
# --------------------------------------------------------------------------------------
DEST_TO_DISTRICT = {
    "Ahmedabad": "Ahmedabad", "Surat": "Surat", "Gandhinagar": "Gandhinagar",
    "Kutch": "Kachchh", "Bhuj": "Kachchh", "Anjar": "Kachchh",
    "Rajkot": "Rajkot", "Vadodara": "Vadodara", "Somnath": "Gir Somnath",
    "Dwarka": "Devbhoomi Dwarka", "Valsad": "Valsad", "Anand": "Anand",
    "Ambaji": "Banaskantha", "Bharuch": "Bharuch", "Botad": "Botad",
    "Jamnagar": "Jamnagar", "Bhavnagar": "Bhavnagar", "Navsari": "Navsari",
    "Girnar": "Junagadh", "Junagadh": "Junagadh", "Saputara": "Dang",
    "Porbandar": "Porbandar", "Patan": "Patan", "Surendranagar": "Surendranagar",
}
# Tourism sheet uses ALL-CAPS spelling variants; map to census canonical spelling.
TOURISM_DISTRICT_CANON = {
    "AHMEDABAD": "Ahmedabad", "DEVBHUMI DWARKA": "Devbhoomi Dwarka",
    "GIR SOMNATH": "Gir Somnath", "BANASKANTHA": "Banaskantha",
    "PANCHMAHAL": "Panchmahal", "KHEDA": "Kheda", "MAHESANA": "Mehsana",
    "PORBANDAR": "Porbandar", "KACHCHH": "Kachchh", "SURAT": "Surat",
}


def clean_hotels():
    print("\n[1/3] hotels.csv")
    h = pd.read_excel(SRC, "final_hotel_dataset")
    h.columns = [c.strip() for c in h.columns]

    # Fix the single column-shifted row (The Fern Residency): every field is shifted
    # one column left, with the true destination ("Ahmedabad") having fallen off the end.
    mask = h["destination name"].astype(str).str.strip() == "Gym"
    if mask.any():
        i = h[mask].index[0]
        h.loc[i] = ["The Fern Residency", 3.9, "Very Good", "Keshav Nagar, Ahmedabad",
                    "24.7 km from Gandhinagar District", 9036, 11812, "Gym", "Ahmedabad"]
        log("hotels", f"Repaired column-shifted row {i} (The Fern Residency, Ahmedabad)")

    # Coerce numeric types now that the bad row is fixed.
    for col in ["rating", "discount price", "actual price"]:
        h[col] = pd.to_numeric(h[col], errors="coerce")
    log("hotels", "Coerced rating / discount price / actual price to numeric")

    # "Not Available" placeholders -> missing.
    na_count = (h["near by place"].astype(str).str.strip() == "Not Available").sum()
    h["near by place"] = h["near by place"].replace(r"^\s*Not Available\s*$", pd.NA, regex=True)
    log("hotels", f"Converted {na_count} 'Not Available' nearby-place placeholders to NaN")

    # Normalise facility casing duplicate (Room service / Room Service).
    h["facilities"] = (h["facilities"].astype(str).str.strip()
                       .str.replace("Room service", "Room Service", regex=False))
    log("hotels", "Normalised 'Room service' -> 'Room Service' casing")

    # Tidy column names.
    h = h.rename(columns={
        "hotel name": "hotel_name", "rating text": "rating_text",
        "near by place": "nearby_place", "discount price": "discount_price",
        "actual price": "actual_price", "destination name": "destination",
    })

    # Derived feature + the join key to districts.
    h["discount_pct"] = ((h["actual_price"] - h["discount_price"]) / h["actual_price"] * 100).round(1)
    h["district"] = h["destination"].map(DEST_TO_DISTRICT)
    unmapped = sorted(h.loc[h["district"].isna(), "destination"].unique())
    log("hotels", f"Added discount_pct; mapped destination->district (unmapped: {unmapped or 'none'})")

    h = h[["hotel_name", "rating", "rating_text", "place", "nearby_place",
           "discount_price", "actual_price", "discount_pct", "facilities",
           "destination", "district"]]
    h.to_csv(os.path.join(DATA, "hotels.csv"), index=False)
    print(f"  -> {len(h)} rows written")
    return h


def clean_tourism():
    print("\n[2/3] tourism_statistics.csv")
    raw = pd.read_excel(SRC, "Gujarat Tourism Data", header=None)

    def grab(start, end, category):
        block = raw.iloc[start:end, [0, 1, 2, 3]].copy()
        block.columns = ["rank", "name", "footfall_mar2026_lacs", "footfall_annual_lacs"]
        block["category"] = category
        block["name"] = block["name"].astype(str).str.title().str.strip()
        for c in ["rank", "footfall_mar2026_lacs", "footfall_annual_lacs"]:
            block[c] = pd.to_numeric(block[c], errors="coerce")
        return block.dropna(subset=["rank"])

    dest = grab(13, 23, "destination")     # Top 10 destinations
    dist = grab(28, 38, "district")        # Top 10 districts
    log("tourism", f"Extracted Top-{len(dest)} destinations and Top-{len(dist)} districts from stacked tables")

    # Canonical district names so the district rows join to socio_economic.csv.
    dist["join_district"] = dist["name"].str.upper().map(TOURISM_DISTRICT_CANON).fillna(dist["name"])
    dest["join_district"] = pd.NA
    log("tourism", "Mapped district rows to canonical census spelling (MAHESANA->Mehsana, etc.)")

    out = pd.concat([dest, dist], ignore_index=True)[
        ["category", "rank", "name", "join_district", "footfall_mar2026_lacs", "footfall_annual_lacs"]
    ]
    out["rank"] = out["rank"].astype(int)
    out.to_csv(os.path.join(DATA, "tourism_statistics.csv"), index=False)
    print(f"  -> {len(out)} rows written")

    # State-level totals are captured as metadata (returned for the README/dictionary).
    totals = {"footfall_annual_apr2025_feb2026_lacs": 2090.42, "footfall_mar2026_lacs": 180.87}
    log("tourism", f"State totals recorded as metadata: {totals} (1 Lac = 100,000 visits)")
    return out, totals


def clean_socio():
    print("\n[3/3] socio_economic.csv")
    s = pd.read_excel(SRC, "Gujarat 2011 Census Data")
    s.columns = ["district", "population_2011", "density_per_km2",
                 "sex_ratio_f_per_1000m", "literacy_rate_pct"]
    log("socio", "Renamed columns (stripped footnote markers from 'District [1,2,...]')")

    # Surat density was parsed as 1.337 (thousands separator read as a decimal point).
    bad = s.loc[s["district"] == "Surat", "density_per_km2"].iloc[0]
    if bad < 10:
        s.loc[s["district"] == "Surat", "density_per_km2"] = round(bad * 1000)
        log("socio", f"Fixed Surat density {bad} -> 1337 (thousands-separator parse error)")

    s["density_per_km2"] = s["density_per_km2"].round().astype(int)
    s["literacy_rate_pct"] = (s["literacy_rate_pct"].astype(str)
                              .str.rstrip("%").astype(float))
    log("socio", "Converted literacy '85.31%' -> numeric 85.31")

    s.to_csv(os.path.join(DATA, "socio_economic.csv"), index=False)
    print(f"  -> {len(s)} rows written")
    return s


def write_dictionary(hotels, tourism, socio, totals):
    print("\n[+] data_dictionary.xlsx")
    defs = {
        "hotels.csv": [
            ("hotel_name", "text", "Hotel/property name", ""),
            ("rating", "float", "Guest rating", "0-5"),
            ("rating_text", "text", "Rating band (Excellent/Very Good/Good/Average/Poor)", ""),
            ("place", "text", "Locality/area of the hotel", ""),
            ("nearby_place", "text", "Distance/description to a nearby landmark", "blank = not available"),
            ("discount_price", "int", "Discounted nightly price", "INR"),
            ("actual_price", "int", "Original nightly price", "INR"),
            ("discount_pct", "float", "Derived: (actual-discount)/actual*100", "%"),
            ("facilities", "text", "Headline facility listed", ""),
            ("destination", "text", "Tourist destination/city as published", ""),
            ("district", "text", "JOIN KEY: destination mapped to census district", ""),
        ],
        "tourism_statistics.csv": [
            ("category", "text", "'destination' or 'district' ranking table", ""),
            ("rank", "int", "Rank within its category (1=highest footfall)", "1-10"),
            ("name", "text", "Destination or district name as published", ""),
            ("join_district", "text", "JOIN KEY: canonical district (district rows only)", ""),
            ("footfall_mar2026_lacs", "float", "Tourist footfall, March 2026", "Lacs (1=100,000)"),
            ("footfall_annual_lacs", "float", "Footfall, Apr 2025 - Feb 2026", "Lacs (1=100,000)"),
        ],
        "socio_economic.csv": [
            ("district", "text", "JOIN KEY: district name (2011 Census)", ""),
            ("population_2011", "int", "Total population, 2011 Census", "persons"),
            ("density_per_km2", "int", "Population density", "persons/km^2"),
            ("sex_ratio_f_per_1000m", "int", "Females per 1000 males", ""),
            ("literacy_rate_pct", "float", "Literacy rate", "%"),
        ],
    }
    with pd.ExcelWriter(os.path.join(DATA, "data_dictionary.xlsx"), engine="openpyxl") as xw:
        overview = pd.DataFrame([
            ["hotels.csv", len(hotels), "Accommodation supply: price, rating, facilities by destination/district"],
            ["tourism_statistics.csv", len(tourism), "Tourism demand: Top-10 destinations & districts by footfall"],
            ["socio_economic.csv", len(socio), "District socio-economic indicators (2011 Census)"],
        ], columns=["file", "rows", "description"])
        meta = pd.DataFrame([
            ["State footfall Apr 2025 - Feb 2026", f"{totals['footfall_annual_apr2025_feb2026_lacs']} Lacs"],
            ["State footfall Mar 2026", f"{totals['footfall_mar2026_lacs']} Lacs"],
            ["Unit", "1 Lac = 100,000 visits"],
            ["Tourism budget", "Rs 6,500 crore"],
            ["Join key across datasets", "district"],
            ["Source", "commissionertourism.gujarat.gov.in/tourist-footfall/table; 2011 Census of India"],
        ], columns=["metadata", "value"])
        overview.to_excel(xw, sheet_name="Overview", index=False)
        meta.to_excel(xw, sheet_name="Metadata", index=False)
        for fname, rows in defs.items():
            pd.DataFrame(rows, columns=["column", "type", "description", "units/notes"]).to_excel(
                xw, sheet_name=fname[:31], index=False)
        pd.DataFrame(CLEAN_LOG, columns=["dataset", "cleaning_action"]).to_excel(
            xw, sheet_name="Cleaning_log", index=False)
    print(f"  -> dictionary written ({len(CLEAN_LOG)} cleaning actions logged)")


if __name__ == "__main__":
    print("Preparing QUB Datathon data folder...")
    hotels = clean_hotels()
    tourism, totals = clean_tourism()
    socio = clean_socio()
    write_dictionary(hotels, tourism, socio, totals)
    print("\nDone. Clean, joinable CSVs + data dictionary written to data/.")
