import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

HABITAT_CHOICES = ("forest", "grassland", "wetland", "desert", "coastal", "marine", "mountain", "other")
DEVICE_TYPE_CHOICES = ("camera_trap", "audio_sensor", "drone", "environmental_sensor")
DEVICE_STATUS_CHOICES = ("active", "inactive", "maintenance", "lost")


class MonitoringSiteCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    habitat_type: str = Field(default="other", description=f"One of: {', '.join(HABITAT_CHOICES)}")
    protected_area: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    elevation_m: float | None = None
    description: str | None = None


class MonitoringSiteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    habitat_type: str
    protected_area: str | None
    latitude: float
    longitude: float
    elevation_m: float | None
    description: str | None
    created_at: datetime
    device_count: int = 0


class DeviceCreate(BaseModel):
    device_code: str = Field(min_length=2, max_length=50)
    device_type: str = Field(description=f"One of: {', '.join(DEVICE_TYPE_CHOICES)}")
    monitoring_site_id: uuid.UUID
    status: str = Field(default="active", description=f"One of: {', '.join(DEVICE_STATUS_CHOICES)}")
    installed_at: date | None = None
    notes: str | None = None


class DeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    device_code: str
    device_type: str
    monitoring_site_id: uuid.UUID
    status: str
    installed_at: date | None
    notes: str | None
    created_at: datetime
