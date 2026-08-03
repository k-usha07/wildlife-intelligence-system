"""iNaturalist dataset integration.

Purpose: species classification / biodiversity recognition training data.

Milestone 1 scope: pull a labeled sample of research-grade observations
(with photos + species names) via the public iNaturalist API, to validate
the species-classification schema end to end. The full iNat competition
training sets (iNat2021 etc.) are distributed as large tarballs — see
https://github.com/visipedia/inat_comp for bulk download links to wire into
a Milestone 2 training job.

Usage:
    python -m app.datasets.inaturalist_integration --taxon "Aves" --place_id 6883 --limit 200
"""
import argparse
import csv

import requests

from app.datasets.base import dataset_dir, log

INAT_API = "https://api.inaturalist.org/v1/observations"


def fetch_observations(taxon_name: str, place_id: int | None, limit: int) -> list[dict]:
    params = {
        "taxon_name": taxon_name,
        "quality_grade": "research",
        "photos": "true",
        "per_page": min(limit, 200),
    }
    if place_id:
        params["place_id"] = place_id

    resp = requests.get(INAT_API, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("results", [])[:limit]


def save_csv(records: list[dict], out_path) -> None:
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "species_guess", "scientific_name", "observed_on", "photo_url", "latitude", "longitude"])
        for r in records:
            taxon = r.get("taxon") or {}
            photos = r.get("photos") or []
            photo_url = photos[0]["url"] if photos else ""
            geojson = r.get("geojson") or {}
            coords = geojson.get("coordinates", [None, None])
            writer.writerow([
                r.get("id"),
                r.get("species_guess"),
                taxon.get("name"),
                r.get("observed_on"),
                photo_url,
                coords[1] if len(coords) > 1 else None,
                coords[0] if len(coords) > 0 else None,
            ])


def main():
    parser = argparse.ArgumentParser(description="Pull iNaturalist research-grade observations")
    parser.add_argument("--taxon", default="Aves", help="taxon name, e.g. Aves, Mammalia")
    parser.add_argument("--place_id", type=int, default=None, help="iNaturalist place id to filter by")
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    log(f"Fetching up to {args.limit} iNaturalist observations for taxon={args.taxon}")
    records = fetch_observations(args.taxon, args.place_id, args.limit)

    out_dir = dataset_dir("inaturalist")
    out_path = out_dir / f"observations_{args.taxon.lower()}.csv"
    save_csv(records, out_path)
    log(f"Saved {len(records)} observations to {out_path}")
    log("For bulk pretraining data (iNat2021 etc.), see https://github.com/visipedia/inat_comp")


if __name__ == "__main__":
    main()
