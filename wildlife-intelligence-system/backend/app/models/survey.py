import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

survey_status_enum = ENUM(
    "planned", "active", "completed", "cancelled", name="survey_status", create_type=False
)
media_type_enum = ENUM("image", "audio", "video", name="media_type", create_type=False)

survey_sites = Table(
    "survey_sites",
    Base.metadata,
    Column("survey_id", UUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"), primary_key=True),
    Column("monitoring_site_id", UUID(as_uuid=True), ForeignKey("monitoring_sites.id", ondelete="CASCADE"), primary_key=True),
)


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    objective = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(survey_status_enum, nullable=False, default="planned")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    sites = relationship("MonitoringSite", secondary=survey_sites, backref="surveys")
    media_assets = relationship("MediaAsset", back_populates="survey", cascade="all, delete-orphan")


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    monitoring_site_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sites.id"), nullable=False)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"))
    media_type = Column(media_type_enum, nullable=False)
    storage_path = Column(String(500), nullable=False)
    captured_at = Column(DateTime(timezone=True))
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    file_size_bytes = Column(BigInteger)
    processing_status = Column(String(30), nullable=False, default="pending")

    survey = relationship("Survey", back_populates="media_assets")
    observations = relationship("Observation", back_populates="media_asset", cascade="all, delete-orphan")


class Observation(Base):
    __tablename__ = "observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    media_asset_id = Column(UUID(as_uuid=True), ForeignKey("media_assets.id", ondelete="CASCADE"), nullable=False)
    species_name = Column(String(150))
    confidence = Column(Numeric(5, 4))
    is_endangered = Column(Boolean, default=False)
    count_estimate = Column(Numeric)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    media_asset = relationship("MediaAsset", back_populates="observations")
