import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

SURVEY_STATUS_CHOICES = ("planned", "active", "completed", "cancelled")


class SurveyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    objective: str | None = None
    start_date: date
    end_date: date | None = None
    site_ids: list[uuid.UUID] = Field(default_factory=list)


class SurveyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    objective: str | None
    owner_id: uuid.UUID
    status: str
    start_date: date
    end_date: date | None
    created_at: datetime
    site_count: int = 0


class MediaAssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    survey_id: uuid.UUID
    monitoring_site_id: uuid.UUID
    device_id: uuid.UUID | None
    media_type: str
    storage_path: str
    uploaded_at: datetime
    processing_status: str


class ObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    media_asset_id: uuid.UUID
    species_name: str | None
    confidence: float | None
    is_endangered: bool
    notes: str | None
    created_at: datetime
