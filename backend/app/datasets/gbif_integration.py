"""GBIF (Global Biodiversity Information Facility) integration.

Purpose: species occurrence records + biodiversity analysis reference data.
GBIF exposes a free REST API, so Milestone 1 integration pulls occurrence
records for a bounding box / country / species list directly (no manual
download step needed) and stores them as CSV for downstream biodiversity
analytics (Milestone 3).

Usage:
    python -m app.datasets.gbif_integration --country IN --limit 500
"""
import argparse
import csv

import requests

from app.core.config import settings
from app.datasets.base import dataset_dir, log


def fetch_occurrences(country: str, limit: int) -> list[dict]:
    url = f"{settings.gbif_api_base}/occurrence/search"
    params = {
        "country": country,
        "hasCoordinate": "true",
        "limit": min(limit, 300),  # GBIF caps page size at 300
    }
    records: list[dict] = []
    offset = 0
    while len(records) < limit:
        params["offset"] = offset
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        batch = payload.get("results", [])
        if not batch:
            break
        records.extend(batch)
        offset += len(batch)
        if payload.get("endOfRecords"):
            break
    return records[:limit]


def save_csv(records: list[dict], out_path) -> None:
    fields = [
        "key", "scientificName", "species", "kingdom", "country",
        "decimalLatitude", "decimalLongitude", "eventDate", "basisOfRecord",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(r)


def main():
    parser = argparse.ArgumentParser(description="Pull GBIF occurrence records")
    parser.add_argument("--country", default="IN", help="ISO-2 country code")
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()

    log(f"Fetching up to {args.limit} GBIF occurrence records for country={args.country}")
    records = fetch_occurrences(args.country, args.limit)

    out_dir = dataset_dir("gbif")
    out_path = out_dir / f"occurrences_{args.country}.csv"
    save_csv(records, out_path)
    log(f"Saved {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
