import uuid

from sqlalchemy import Column, String, Float, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
import enum


class Relationship(str, enum.Enum):
    AGREEMENT = "AGREEMENT"
    PARTIAL = "PARTIAL"
    CONFLICT = "CONFLICT"
    MISSING = "MISSING"


class EvidenceComparison(Base):
    __tablename__ = "evidence_comparisons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    observation_id = Column(UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False)
    source_a = Column(String, nullable=False)
    source_b = Column(String, nullable=False)
    relationship = Column(SQLEnum(Relationship), nullable=False)
    agreement_score = Column(Float, nullable=False)
    explanation = Column(Text, nullable=True)
