"""
Assessment Engine — determines the final water condition assessment
based on all evidence and conflict analysis.
"""
from typing import Dict, Any, List


def determine_assessment(
    citizen: Dict[str, Any],
    all_evidence: Dict[str, Dict[str, Any]],
    evidence_status: str,
    confidence: float,
) -> str:
    """
    Determine the final assessment label.
    """
    # Check for specific conditions
    citizen_clarity = citizen.get("water_clarity")
    visible_waste = citizen.get("visible_waste")
    algae = citizen.get("algae")
    odor = citizen.get("odor")

    # Waste detection
    if visible_waste:
        return "Visible contamination — waste detected"

    # Algae bloom
    if algae:
        return "Possible algae bloom"

    # Odor-based
    if odor == "chemical":
        return "Possible chemical contamination"
    if odor == "sewage":
        return "Possible sewage contamination"

    # Clarity-based with confidence
    if citizen_clarity == "opaque":
        if confidence > 0.6:
            return "Severe turbidity — likely pollution event"
        else:
            return "Possible severe turbidity — verification needed"

    if citizen_clarity == "cloudy":
        if evidence_status == "SUPPORTED":
            return "Elevated turbidity — likely ecological stress"
        elif evidence_status == "PARTIALLY_SUPPORTED":
            return "Possible ecological stress — partial evidence"
        else:
            return "Unclear water condition — insufficient evidence"

    if citizen_clarity == "slightly_cloudy":
        return "Mild turbidity — within acceptable range"

    if citizen_clarity == "clear":
        return "Normal water condition"

    # Fallback
    if confidence > 0.7:
        return "Normal water condition"
    else:
        return "Indeterminate — more evidence needed"


def run_assessment_engine(
    citizen: Dict[str, Any],
    all_evidence: Dict[str, Dict[str, Any]],
    evidence_status: str,
    confidence: float,
) -> str:
    """Main assessment engine entry point."""
    return determine_assessment(citizen, all_evidence, evidence_status, confidence)
