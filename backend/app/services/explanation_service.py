"""
Explanation Service — generates human-readable explanations
and next-evidence recommendations.
"""
from typing import Dict, Any, List, Optional


def generate_explanation(
    assessment: str,
    confidence: float,
    reliability: float,
    uncertainty: float,
    evidence_status: str,
    supporting_evidence: List[str],
    conflicting_evidence: List[str],
    comparisons: List[Dict[str, Any]],
) -> str:
    """Generate a human-readable explanation paragraph."""
    parts = []

    # Main assessment statement
    parts.append(f"Assessment: {assessment}")
    parts.append(f"Confidence: {confidence:.0%}")
    parts.append(f"Evidence reliability: {reliability:.0%}")

    # Evidence status explanation
    status_explanations = {
        "SUPPORTED": "Multiple independent sources support the citizen observation.",
        "PARTIALLY_SUPPORTED": "Some sources support the observation, but conflicts exist.",
        "CONTRADICTED": "Independent sources contradict the citizen observation.",
        "INSUFFICIENT_EVIDENCE": "Not enough evidence available to make a reliable assessment.",
        "UNCERTAIN": "Evidence is mixed and no clear conclusion can be drawn.",
    }
    parts.append(status_explanations.get(evidence_status, "Evidence status unclear."))

    # Supporting evidence
    if supporting_evidence:
        parts.append(f"Supporting evidence: {'; '.join(supporting_evidence[:3])}")

    # Conflicting evidence
    if conflicting_evidence:
        parts.append(f"Conflicting evidence: {'; '.join(conflicting_evidence[:3])}")

    # Uncertainty explanation
    if uncertainty > 0.5:
        parts.append("High uncertainty — additional evidence strongly recommended.")

    return " ".join(parts)


def generate_recommendation(evidence_status: str, requires_review: bool, confidence: float) -> str:
    """Generate a recommendation based on the assessment."""
    if requires_review:
        if evidence_status == "CONTRADICTED":
            return "Additional verification recommended — evidence conflicts detected."
        elif evidence_status == "INSUFFICIENT_EVIDENCE":
            return "Additional evidence collection recommended — current data insufficient."
        else:
            return "Human verification recommended due to low confidence."

    if confidence > 0.8:
        return "Evidence convergence — observation likely accurate."
    elif confidence > 0.6:
        return "Observation likely accurate — routine monitoring continues."
    else:
        return "Continue monitoring — evidence still accumulating."


def run_explanation_service(
    assessment: str,
    confidence: float,
    reliability: float,
    uncertainty: float,
    evidence_status: str,
    supporting_evidence: List[str],
    conflicting_evidence: List[str],
    comparisons: List[Dict[str, Any]],
    requires_review: bool,
    citizen: Dict[str, Any],
    all_evidence: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Main explanation service entry point."""
    explanation = generate_explanation(
        assessment, confidence, reliability, uncertainty,
        evidence_status, supporting_evidence, conflicting_evidence, comparisons,
    )
    recommendation = generate_recommendation(evidence_status, requires_review, confidence)

    return {
        "explanation": explanation,
        "recommendation": recommendation,
        "next_evidence": None,  # populated by next_evidence_service
    }
