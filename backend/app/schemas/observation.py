from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ObservationCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timestamp: Optional[datetime] = None
    photo_url: Optional[str] = None
    water_clarity: Optional[str] = None
    visible_waste: Optional[bool] = None
    algae: Optional[bool] = None
    odor: Optional[str] = None


class ObservationResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    latitude: float
    longitude: float
    timestamp: datetime
    photo_url: Optional[str] = None
    water_clarity: Optional[str] = None
    visible_waste: Optional[bool] = None
    algae: Optional[bool] = None
    odor: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
