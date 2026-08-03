"""BirdCLEF and Animal Kingdom dataset integration.

Both datasets are distributed via Kaggle:
  - BirdCLEF (bird sound recognition / bioacoustic classification):
      https://www.kaggle.com/competitions/birdclef-2024 (and prior years)
  - Animal Kingdom (animal image/video recognition, species identification):
      https://www.kaggle.com/datasets/kaustubhb999/animal-kingdom-dataset
      (a subset mirror; the full academic release is at
      https://sutdcv.github.io/Animal-Kingdom/)

This script wraps the official `kaggle` CLI so credentials and licensing
terms stay in the user's control (Kaggle requires accepting each dataset's
terms in-browser once, before the API is allowed to download it).

Setup:
    pip install kaggle
    export KAGGLE_USERNAME=...   # or set in backend/.env
    export KAGGLE_KEY=...

Usage:
    python -m app.datasets.kaggle_datasets_integration --dataset birdclef
    python -m app.datasets.kaggle_datasets_integration --dataset animal_kingdom
"""
import argparse
import os
import subprocess

from app.core.config import settings
from app.datasets.base import dataset_dir, log

DATASET_SLUGS = {
    "birdclef": "competitions/birdclef-2024",          # kaggle competitions download -c birdclef-2024
    "animal_kingdom": "kaustubhb999/animal-kingdom-dataset",  # kaggle datasets download -d ...
}


def ensure_kaggle_credentials() -> None:
    if settings.kaggle_username and settings.kaggle_key:
        os.environ.setdefault("KAGGLE_USERNAME", settings.kaggle_username)
        os.environ.setdefault("KAGGLE_KEY", settings.kaggle_key)

    if not (os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY")):
        raise SystemExit(
            "Kaggle credentials not found. Set KAGGLE_USERNAME and KAGGLE_KEY "
            "(in backend/.env or as env vars) — get them from "
            "https://www.kaggle.com/settings > API > Create New Token."
        )


def download(dataset_key: str) -> None:
    ensure_kaggle_credentials()
    out_dir = dataset_dir(dataset_key)
    slug = DATASET_SLUGS[dataset_key]

    if slug.startswith("competitions/"):
        competition = slug.split("/", 1)[1]
        cmd = ["kaggle", "competitions", "download", "-c", competition, "-p", str(out_dir)]
    else:
        cmd = ["kaggle", "datasets", "download", "-d", slug, "-p", str(out_dir), "--unzip"]

    log(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    log(f"Dataset '{dataset_key}' downloaded to {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Download Kaggle-hosted wildlife datasets")
    parser.add_argument("--dataset", choices=DATASET_SLUGS.keys(), required=True)
    args = parser.parse_args()
    download(args.dataset)


if __name__ == "__main__":
    main()
