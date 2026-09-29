from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.observation import Observation
from app.models.evidence import Evidence
from app.models.assessment import Assessment
from app.models.comparison import EvidenceComparison
from app.schemas.assessment import AssessmentResponse, ExplanationResponse
from app.services.evidence_service import get_evidence_for_observation, normalize_evidence, get_citizen_evidence
from app.services.alignment_service import align_evidence
from app.services.conflict_engine import run_conflict_engine
from app.services.reliability_engine import run_reliability_engine
from app.services.assessment_engine import run_assessment_engine
from app.services.explanation_service import run_explanation_service

router = APIRouter()


@router.post("/assessments/{observation_id}", response_model=AssessmentResponse, status_code=201)
def create_assessment(observation_id: UUID, db: Session = Depends(get_db)):
    """Run full assessment pipeline for an observation."""
    # Fetch observation
    observation = db.query(Observation).filter(Observation.id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")

    # Fetch all evidence
    evidence_list = get_evidence_for_observation(db, observation_id)
    all_evidence = normalize_evidence(evidence_list)

    # Get citizen evidence from observation
    citizen = get_citizen_evidence(db, observation)
    all_evidence["citizen"] = citizen

    # Run alignment
    alignments = align_evidence(citizen, all_evidence)

    # Run conflict engine
    conflict_result = run_conflict_engine(citizen, all_evidence)

    # Run reliability engine
    reliability_result = run_reliability_engine(
        all_evidence,
        conflict_result["comparisons"],
        conflict_result["agreement_score"],
        conflict_result["evidence_status"],
    )

    # Run assessment engine
    assessment_label = run_assessment_engine(
        citizen,
        all_evidence,
        conflict_result["evidence_status"],
        reliability_result["confidence"],
    )

    # Run explanation service
    explanation_result = run_explanation_service(
        assessment_label,
        reliability_result["confidence"],
        reliability_result["reliability"],
        reliability_result["uncertainty"],
        conflict_result["evidence_status"],
        conflict_result["supporting_evidence"],
        conflict_result["conflicts"],
        conflict_result["comparisons"],
        reliability_result["requires_review"],
        citizen,
        all_evidence,
    )

    # Store assessment
    db_assessment = Assessment(
        observation_id=observation_id,
        assessment=assessment_label,
        reliability=reliability_result["reliability"],
        confidence=reliability_result["confidence"],
        uncertainty=reliability_result["uncertainty"],
        requires_review=reliability_result["requires_review"],
        explanation=explanation_result["explanation"],
    )
    db.add(db_assessment)

    # Store comparisons
    for comp in conflict_result["comparisons"]:
        db_comp = EvidenceComparison(
            observation_id=observation_id,
            source_a=comp["source_a"],
            source_b=comp["source_b"],
            relationship=comp["relationship"],
            agreement_score=comp["agreement_score"],
            explanation=comp["explanation"],
        )
        db.add(db_comp)

    db.commit()
    db.refresh(db_assessment)
    return db_assessment


@router.get("/assessments/{observation_id}", response_model=AssessmentResponse)
def get_assessment(observation_id: UUID, db: Session = Depends(get_db)):
    """Get the latest assessment for an observation."""
    assessment = (
        db.query(Assessment)
        .filter(Assessment.observation_id == observation_id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@router.get("/assessments/{observation_id}/explanation", response_model=ExplanationResponse)
def get_explanation(observation_id: UUID, db: Session = Depends(get_db)):
    """Get detailed explanation for an assessment."""
    assessment = (
        db.query(Assessment)
        .filter(Assessment.observation_id == observation_id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Re-run explanation components
    observation = db.query(Observation).filter(Observation.id == observation_id).first()
    evidence_list = get_evidence_for_observation(db, observation_id)
    all_evidence = normalize_evidence(evidence_list)
    citizen = get_citizen_evidence(db, observation)
    all_evidence["citizen"] = citizen

    conflict_result = run_conflict_engine(citizen, all_evidence)
    reliability_result = run_reliability_engine(
        all_evidence,
        conflict_result["comparisons"],
        conflict_result["agreement_score"],
        conflict_result["evidence_status"],
    )
    explanation_result = run_explanation_service(
        assessment.assessment,
        reliability_result["confidence"],
        reliability_result["reliability"],
        reliability_result["uncertainty"],
        conflict_result["evidence_status"],
        conflict_result["supporting_evidence"],
        conflict_result["conflicts"],
        conflict_result["comparisons"],
        reliability_result["requires_review"],
        citizen,
        all_evidence,
    )

    return ExplanationResponse(
        assessment=assessment.assessment,
        confidence=assessment.confidence,
        reliability=assessment.reliability,
        uncertainty=assessment.uncertainty,
        evidence_status=conflict_result["evidence_status"],
        supporting_evidence=conflict_result["supporting_evidence"],
        conflicting_evidence=conflict_result["conflicts"],
        recommendation=explanation_result["recommendation"],
        next_evidence=explanation_result["next_evidence"],
    )


@router.get("/observations/{observation_id}/next-evidence")
def get_next_evidence(observation_id: UUID, db: Session = Depends(get_db)):
    """Get next best evidence recommendation."""
    observation = db.query(Observation).filter(Observation.id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")

    evidence_list = get_evidence_for_observation(db, observation_id)
    all_evidence = normalize_evidence(evidence_list)
    citizen = get_citizen_evidence(db, observation)
    all_evidence["citizen"] = citizen

    conflict_result = run_conflict_engine(citizen, all_evidence)

    from app.services.explanation_service import recommend_next_evidence
    next_ev = recommend_next_evidence(citizen, all_evidence, conflict_result["comparisons"], conflict_result["evidence_status"])

    return {"next_evidence": next_ev}
