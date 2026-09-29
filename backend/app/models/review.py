import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
import enum


class ReviewerDecision(str, enum.Enum):
    confirmed = "confirmed"
    rejected = "rejected"
    needs_more_evidence = "needs_more_evidence"


class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    reviewer_decision = Column(SQLEnum(ReviewerDecision), nullable=False)
    reviewer_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
