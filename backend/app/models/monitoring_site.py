import uuid

from geoalchemy2 import Geography
from sqlalchemy import Column, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

habitat_type_enum = ENUM(
    "forest", "grassland", "wetland", "desert", "coastal", "marine", "mountain", "other",
    name="habitat_type",
    create_type=False,
)

device_type_enum = ENUM(
    "camera_trap", "audio_sensor", "drone", "environmental_sensor",
    name="device_type",
    create_type=False,
)

device_status_enum = ENUM(
    "active", "inactive", "maintenance", "lost",
    name="device_status",
    create_type=False,
)


class MonitoringSite(Base):
    __tablename__ = "monitoring_sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    habitat_type = Column(habitat_type_enum, nullable=False, default="other")
    protected_area = Column(String(150))
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    elevation_m = Column(Numeric(8, 2))
    description = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    devices = relationship("Device", back_populates="site", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_code = Column(String(50), unique=True, nullable=False)
    device_type = Column(device_type_enum, nullable=False)
    monitoring_site_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sites.id", ondelete="CASCADE"), nullable=False)
    status = Column(device_status_enum, nullable=False, default="active")
    installed_at = Column(Date)
    last_maintained_at = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    site = relationship("MonitoringSite", back_populates="devices")
