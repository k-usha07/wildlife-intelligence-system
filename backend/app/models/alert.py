import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

alert_severity_enum = ENUM(
    "info", "warning", "critical", name="alert_severity", create_type=False
)
alert_type_enum = ENUM(
    "endangered_species", "population_decline", "habitat_degradation", "device_issue",
    name="alert_type",
    create_type=False,
)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    monitoring_site_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sites.id"))
    observation_id = Column(UUID(as_uuid=True), ForeignKey("observations.id", ondelete="SET NULL"))
    alert_type = Column(alert_type_enum, nullable=False)
    severity = Column(alert_severity_enum, nullable=False, default="info")
    message = Column(Text, nullable=False)
    is_acknowledged = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    survey = relationship("Survey")
