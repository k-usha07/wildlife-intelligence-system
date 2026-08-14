from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    app_name: str = "Wildlife Population Intelligence System"
    version: str = "1.0.0"
    env: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"
    secret_key: str = "change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    database_url: str = "postgresql+psycopg2://wildlife:wildlife@localhost:5432/wildlife_db"
    frontend_origin: List[str] = ["http://localhost:5173"]
    media_storage_path: str = "./storage/media"
    datasets_dir: str = "./storage/datasets"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    enable_ml_models: bool = False
    yolo_model_path: str = "./models/yolov8_wildlife.pt"
    species_classifier_path: str = "./models/species_classifier.h5"
    audio_model_path: str = "./models/birdnet_model.tflite"
    population_model_path: str = "./models/population_estimator.pkl"

    class Config:
        env_file = ".env"
        extra = "ignore"   # Ignore extra env vars from Render


settings = Settings()