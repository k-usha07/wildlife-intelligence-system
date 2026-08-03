"""Shared helpers for the Milestone-1 dataset integration scripts.

These scripts download or register metadata for the datasets referenced in the
project brief:
  - Snapshot Serengeti (camera trap species detection)
  - iNaturalist (species classification / biodiversity recognition)
  - BirdCLEF (bird sound recognition / bioacoustic classification)
  - Animal Kingdom (animal image recognition / species identification)
  - GBIF (species occurrence records / biodiversity analysis)

Milestone 1 scope: get the datasets (or a representative sample / metadata
index) onto disk under DATASETS_DIR with a consistent folder layout, so the
Milestone 2 AI/ML training pipelines can consume them directly. Full dataset
downloads (esp. Snapshot Serengeti, tens of TB) are represented here via
their official, resumable access points rather than bundled.
"""
import os
from pathlib import Path

from app.core.config import settings


def dataset_dir(name: str) -> Path:
    path = Path(settings.datasets_dir) / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def log(msg: str) -> None:
    print(f"[datasets] {msg}")
