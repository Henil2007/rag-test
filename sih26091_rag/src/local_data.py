"""
Hyper-local structured data lookup.
This is deliberately kept SEPARATE from the RAG text retriever: structured
tabular stats (population, existing unit counts) should be queried directly,
not embedded as prose and semantically searched.

Swap load_local_stats() to pull from a real Census/MSME/Agri-census source
later without touching the rest of the pipeline.
"""

import csv
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dummy_local_stats.csv")


def load_local_stats():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_village(village_name: str):
    rows = load_local_stats()
    village_name_lower = village_name.strip().lower()
    for row in rows:
        if row["village"].strip().lower() == village_name_lower:
            return row
    # fallback: fuzzy-ish partial match
    for row in rows:
        if village_name_lower in row["village"].strip().lower():
            return row
    return None


SECTOR_TO_COLUMN = {
    "dairy": "existing_dairy_units",
    "retail": "existing_retail_units",
    "textile": "existing_textile_units",
    "textiles": "existing_textile_units",
}


def get_competitor_density(village_row: dict, sector: str):
    col = SECTOR_TO_COLUMN.get(sector.strip().lower())
    if col is None or village_row is None:
        return None
    households = int(village_row["households"])
    existing_units = int(village_row[col])
    per_1000_households = round((existing_units / households) * 1000, 2)
    return {
        "existing_units": existing_units,
        "households": households,
        "units_per_1000_households": per_1000_households,
    }


if __name__ == "__main__":
    row = find_village("Rampura")
    print(row)
    print(get_competitor_density(row, "dairy"))
