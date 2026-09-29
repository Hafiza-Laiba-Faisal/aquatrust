from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class AssessmentResponse(BaseModel):
    id: UUID
    observation_id: UUID
    assessment: str
    reliability: float
    confidence: float
    uncertainty: float
    requires_review: bool
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class ExplanationResponse(BaseModel):
    assessment: str
    confidence: float
    reliability: float
    uncertainty: float
    evidence_status: str
    supporting_evidence: List[str]
    conflicting_evidence: List[str]
    recommendation: str
    next_evidence: Optional[str] = None
