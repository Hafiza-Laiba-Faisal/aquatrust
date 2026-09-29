from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ReviewCreate(BaseModel):
    assessment_id: UUID
    reviewer_decision: str  # confirmed, rejected, needs_more_evidence
    reviewer_comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: UUID
    assessment_id: UUID
    reviewer_decision: str
    reviewer_comment: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True
