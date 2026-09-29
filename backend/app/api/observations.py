from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.observation import Observation
from app.schemas.observation import ObservationCreate, ObservationResponse

router = APIRouter()


@router.post("/observations", response_model=ObservationResponse, status_code=201)
def create_observation(obs: ObservationCreate, db: Session = Depends(get_db)):
    """Create a new citizen observation."""
    db_obs = Observation(
        latitude=obs.latitude,
        longitude=obs.longitude,
        timestamp=obs.timestamp or datetime.utcnow(),
        photo_url=obs.photo_url,
        water_clarity=obs.water_clarity,
        visible_waste=obs.visible_waste,
        algae=obs.algae,
        odor=obs.odor,
    )
    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)
    return db_obs


@router.get("/observations/{observation_id}", response_model=ObservationResponse)
def get_observation(observation_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a specific observation by ID."""
    obs = db.query(Observation).filter(Observation.id == observation_id).first()
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return obs


@router.get("/observations", response_model=List[ObservationResponse])
def list_observations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all observations."""
    return db.query(Observation).offset(skip).limit(limit).all()
