from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceCreate, EvidenceResponse

router = APIRouter()


@router.post("/evidence", response_model=EvidenceResponse, status_code=201)
def create_evidence(ev: EvidenceCreate, db: Session = Depends(get_db)):
    """Submit evidence for an observation."""
    db_ev = Evidence(
        observation_id=ev.observation_id,
        source_type=ev.source_type,
        timestamp=ev.timestamp or datetime.utcnow(),
        location=ev.location,
        payload=ev.payload,
        quality_score=ev.quality_score,
    )
    db.add(db_ev)
    db.commit()
    db.refresh(db_ev)
    return db_ev


@router.get("/evidence/{observation_id}", response_model=List[EvidenceResponse])
def get_evidence(observation_id: UUID, db: Session = Depends(get_db)):
    """Get all evidence for a specific observation."""
    evidence = db.query(Evidence).filter(Evidence.observation_id == observation_id).all()
    return evidence
