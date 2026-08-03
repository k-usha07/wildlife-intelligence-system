"""Snapshot Serengeti dataset integration.

Purpose: wildlife species detection / camera trap image classification.

The full image set is tens of TB, hosted by LILA BC (Labeled Information
Library of Alexandria: Biology and Conservation) on public cloud storage.
Milestone 1 scope: download the season metadata (species labels + bounding
boxes) so the schema/pipeline can be built and tested against real labels,
then stream a small sample of images for local development. Full-resolution
bulk image sync is a Milestone-2 infrastructure task (done via `azcopy` /
`aws s3 sync` against the LILA-hosted buckets referenced below).

Usage:
    python -m app.datasets.snapshot_serengeti_integration --season S1 --sample 20
"""
import argparse
import json

import requests

from app.datasets.base import dataset_dir, log

# Public, versioned metadata index maintained by LILA BC for Snapshot Serengeti.
LILA_METADATA_INDEX = "https://lila.science/datasets/snapshot-serengeti"
# Season-level COCO-camera-traps style annotation files (hosted by LILA BC).
SEASON_ANNOTATIONS_URL = {
    "S1": "https://lilablobssc.blob.core.windows.net/snapshotserengeti-v-2-0/SnapshotSerengeti_S1_v2_1.json",
}


def download_annotations(season: str, out_dir) -> str | None:
    url = SEASON_ANNOTATIONS_URL.get(season)
    if not url:
        log(f"No known annotation URL configured for season '{season}'. "
            f"See {LILA_METADATA_INDEX} for the full season list and add it here.")
        return None

    log(f"Downloading annotations for season {season} ...")
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    out_path = out_dir / f"{season}_annotations.json"
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1 << 20):
            f.write(chunk)
    log(f"Saved annotations to {out_path}")
    return str(out_path)


def summarize(annotations_path: str, sample: int) -> None:
    with open(annotations_path) as f:
        data = json.load(f)
    categories = {c["id"]: c["name"] for c in data.get("categories", [])}
    log(f"Categories in this season: {len(categories)} species labels")
    for image in data.get("images", [])[:sample]:
        log(f"  sample image: {image.get('file_name')}")


def main():
    parser = argparse.ArgumentParser(description="Integrate Snapshot Serengeti metadata")
    parser.add_argument("--season", default="S1")
    parser.add_argument("--sample", type=int, default=10, help="number of sample image refs to print")
    args = parser.parse_args()

    out_dir = dataset_dir("snapshot_serengeti")
    ann_path = download_annotations(args.season, out_dir)
    if ann_path:
        summarize(ann_path, args.sample)

    log("NOTE: Full image bulk sync (multi-TB) should be run separately with "
        "azcopy/aws s3 sync against the LILA BC bucket for this dataset — "
        "not part of Milestone 1 automated integration.")


if __name__ == "__main__":
    main()
