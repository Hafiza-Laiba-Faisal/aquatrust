"""Demo scenario API — expose the four deterministic scenarios."""
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.database import get_db
from app.models.observation import Observation
from app.models.evidence import Evidence
from app.models.assessment import Assessment
from app.models.comparison import EvidenceComparison
from app.services.demo_service import get_all_scenarios, get_scenario
from app.services.evidence_service import get_evidence_for_observation, normalize_evidence, get_citizen_evidence
from app.services.conflict_engine import run_conflict_engine
from app.services.reliability_engine import run_reliability_engine
from app.services.assessment_engine import run_assessment_engine
from app.services.explanation_service import run_explanation_service
from app.services.next_evidence_service import recommend_next_evidence

router = APIRouter()


@router.get("/demo/scenarios")
def list_scenarios():
    """List all available demo scenarios."""
    return {"scenarios": get_all_scenarios()}


@router.get("/demo/scenarios/{scenario_id}")
def get_scenario_by_id(scenario_id: str):
    """Get a specific scenario definition."""
    scenario = get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


class ScenarioRunResponse(BaseModel):
    scenario_id: str
    observation_id: UUID
    assessment_id: UUID
    assessment: str
    evidence_status: str
    evidence_reliability: float
    assessment_confidence: float
    uncertainty: float
    requires_human_review: bool
    supporting_evidence: List[str]
    conflicting_evidence: List[str]
    explanation: str
    recommended_action: str
    next_evidence: Optional[str] = None


@router.post("/demo/scenarios/{scenario_id}/run", response_model=ScenarioRunResponse)
def run_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Run a demo scenario end-to-end and return the full assessment."""
    scenario = get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Create observation
    obs_data = scenario["observation"]
    db_obs = Observation(
        latitude=obs_data["latitude"],
        longitude=obs_data["longitude"],
        timestamp=datetime.fromisoformat(obs_data["timestamp"]),
        water_clarity=obs_data.get("water_clarity"),
        visible_waste=obs_data.get("visible_waste"),
        algae=obs_data.get("algae"),
        odor=obs_data.get("odor"),
    )
    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)

    # Create evidence
    for ev_data in scenario["evidence"]:
        db_ev = Evidence(
            observation_id=db_obs.id,
            source_type=ev_data["source_type"],
            timestamp=datetime.fromisoformat(ev_data["timestamp"]),
            location=ev_data.get("location"),
            payload=ev_data["payload"],
            quality_score=ev_data.get("quality_score", 0.5),
        )
        db.add(db_ev)
    db.commit()

    # Run assessment pipeline
    evidence_list = get_evidence_for_observation(db, db_obs.id)
    all_evidence = normalize_evidence(evidence_list)
    citizen = get_citizen_evidence(db, db_obs)
    all_evidence["citizen"] = citizen

    conflict_result = run_conflict_engine(citizen, all_evidence)
    reliability_result = run_reliability_engine(
        all_evidence,
        conflict_result["comparisons"],
        conflict_result["agreement_score"],
        conflict_result["evidence_status"],
    )
    assessment_label = run_assessment_engine(
        citizen,
        all_evidence,
        conflict_result["evidence_status"],
        reliability_result["confidence"],
    )
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
    next_evidence_result = recommend_next_evidence(
        citizen, all_evidence, conflict_result["comparisons"], conflict_result["evidence_status"]
    )

    # Store assessment
    db_assessment = Assessment(
        observation_id=db_obs.id,
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
            observation_id=db_obs.id,
            source_a=comp["source_a"],
            source_b=comp["source_b"],
            relationship=comp["relationship"],
            agreement_score=comp["agreement_score"],
            explanation=comp["explanation"],
        )
        db.add(db_comp)

    db.commit()
    db.refresh(db_assessment)

    return ScenarioRunResponse(
        scenario_id=scenario_id,
        observation_id=db_obs.id,
        assessment_id=db_assessment.id,
        assessment=assessment_label,
        evidence_status=conflict_result["evidence_status"],
        evidence_reliability=reliability_result["reliability"],
        assessment_confidence=reliability_result["confidence"],
        uncertainty=reliability_result["uncertainty"],
        requires_human_review=reliability_result["requires_review"],
        supporting_evidence=conflict_result["supporting_evidence"],
        conflicting_evidence=conflict_result["conflicts"],
        explanation=explanation_result["explanation"],
        recommended_action=explanation_result["recommendation"],
        next_evidence=next_evidence_result["recommended_action"],
    )
