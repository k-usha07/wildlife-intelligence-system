from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────
    app_name: str = "Wildlife Population Intelligence System"
    version: str = "1.0.0"
    env: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # ── Security / JWT ──────────────────────────────────────────────────
    secret_key: str = "change-this-to-a-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # ── Database ────────────────────────────────────────────────────────
    database_url: str = "postgresql+psycopg2://wildlife:wildlife@db:5432/wildlife_db"

    # ── CORS  ← THIS IS THE FIX: must be a List[str], not a str ──────
    frontend_origin: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── Media / Dataset Storage ────────────────────────────────────────
    media_storage_path: str = "./storage/media"
    datasets_dir: str = "./storage/datasets"

    # ── Redis ──────────────────────────────────────────────────────────
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = ""

    # ── ML Model Paths ────────────────────────────────────────────────
    yolo_model_path: str = "./models/yolov8_wildlife.pt"
    species_classifier_path: str = "./models/species_classifier.h5"
    audio_model_path: str = "./models/birdnet_model.tflite"
    population_model_path: str = "./models/population_estimator.pkl"

    # ── ML Feature Flags ──────────────────────────────────────────────
    enable_image_analysis: bool = True
    enable_audio_analysis: bool = True
    enable_ml_models: bool = False

    # ── External APIs ─────────────────────────!─────────────────────────
    kaggle_username: str = ""
    kaggle_key: str = ""
    gbif_api_base: str = "https://api.gbif.org/v1"

    class Config:
        env_file = ".env"


settings = Settings()