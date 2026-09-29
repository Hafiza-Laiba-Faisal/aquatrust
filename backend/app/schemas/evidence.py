from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class EvidenceCreate(BaseModel):
    observation_id: UUID
    source_type: str  # citizen, sensor, satellite, weather, historical
    timestamp: Optional[datetime] = None
    location: Optional[Dict[str, float]] = None
    payload: Dict[str, Any]
    quality_score: float = Field(default=0.5, ge=0.0, le=1.0)


class EvidenceResponse(BaseModel):
    id: UUID
    observation_id: UUID
    source_type: str
    timestamp: datetime
    location: Optional[Dict[str, float]] = None
    payload: Dict[str, Any]
    quality_score: float

    class Config:
        from_attributes = True
