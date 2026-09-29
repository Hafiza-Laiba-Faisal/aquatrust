import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    observation_id = Column(UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False)
    assessment = Column(String, nullable=False)
    reliability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    requires_review = Column(Boolean, default=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
