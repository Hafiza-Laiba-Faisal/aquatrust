import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base
import enum


class SourceType(str, enum.Enum):
    citizen = "citizen"
    sensor = "sensor"
    satellite = "satellite"
    weather = "weather"
    historical = "historical"


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    observation_id = Column(UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False)
    source_type = Column(SQLEnum(SourceType), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    location = Column(JSONB, nullable=True)  # {lat, lon}
    payload = Column(JSONB, nullable=False)
    quality_score = Column(Float, default=0.5)
