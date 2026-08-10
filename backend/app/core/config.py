from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Wildlife Population Intelligence System"
    env: str = "development"

    secret_key: str = "change-this-to-a-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    database_url: str = "postgresql+psycopg2://wildlife:wildlife@localhost:5432/wildlife_db"

    frontend_origin: str = "http://localhost:5173"

@property
def frontend_origins(self) -> list[str]:
    """Supports a single origin or a comma-separated list, e.g.
    FRONTEND_ORIGIN=http://localhost:5173,https://your-frontend.example
    Trims whitespace and drops empty entries."""
    return [o.strip() for o in self.frontend_origin.split(",") if o.strip()]
    media_storage_path: str = "./storage/media"
    datasets_dir: str = "./storage/datasets"

    kaggle_username: str = ""
    kaggle_key: str = ""
    gbif_api_base: str = "https://api.gbif.org/v1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
