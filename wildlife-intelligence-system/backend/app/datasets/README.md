# Dataset integration (Milestone 1)

Scripts to pull the datasets referenced in the project brief into
`storage/datasets/<name>/`, ready for the Milestone 2 AI/ML training
pipelines.

| Dataset             | Purpose                                            | Script                                 | Access method            |
|----------------------|-----------------------------------------------------|------------------------------------------|-----------------------------|
| Snapshot Serengeti    | Wildlife species detection, camera trap classification | `snapshot_serengeti_integration.py`      | LILA BC direct download (metadata now, bulk images via azcopy/aws s3 later) |
| iNaturalist           | Species classification, biodiversity recognition    | `inaturalist_integration.py`             | Public iNaturalist REST API |
| BirdCLEF              | Bird sound recognition, bioacoustic classification   | `kaggle_datasets_integration.py`         | Kaggle API (competition)   |
| Animal Kingdom        | Animal image recognition, species identification     | `kaggle_datasets_integration.py`         | Kaggle API (dataset)        |
| GBIF                  | Species occurrence records, biodiversity analysis     | `gbif_integration.py`                    | Public GBIF REST API        |

## Run them all

```bash
cd backend
source venv/bin/activate   # or run inside the backend Docker container

python -m app.datasets.gbif_integration --country IN --limit 500
python -m app.datasets.inaturalist_integration --taxon Aves --limit 200
python -m app.datasets.snapshot_serengeti_integration --season S1 --sample 10

# Requires Kaggle API credentials in backend/.env (KAGGLE_USERNAME / KAGGLE_KEY)
python -m app.datasets.kaggle_datasets_integration --dataset birdclef
python -m app.datasets.kaggle_datasets_integration --dataset animal_kingdom
```

Downloaded/streamed data lands under `DATASETS_DIR` (default
`backend/storage/datasets/`), one subfolder per dataset. Large bulk
downloads (Snapshot Serengeti full imagery, full Kaggle competition sets)
are intentionally left as an explicit, separate step from Milestone 1 —
this milestone wires up the integration path and validates it against real
metadata/labels so Milestone 2's training code has a known folder layout
to target.
