"""
Next Best Evidence Service — deterministic rule-based recommendations.

No ML. Just clear, explainable rules.
"""
from typing import Dict, Any, List, Optional


def recommend_next_evidence(
    citizen: Dict[str, Any],
    all_evidence: Dict[str, Dict[str, Any]],
    comparisons: List[Dict[str, Any]],
    evidence_status: str,
) -> Dict[str, Any]:
    """
    Recommend the most useful next evidence action.

    Returns:
        {
            "recommended_action": str,
            "reason": str,
            "priority": "HIGH" | "MEDIUM" | "LOW"
        }
    """
    has_sensor = "sensor" in all_evidence
    has_satellite = "satellite" in all_evidence
    has_historical = "historical" in all_evidence
    has_weather = "weather" in all_evidence

    # Rule 1: Citizen vs sensor conflict → repeat sensor measurement
    for c in comparisons:
        if c.get("source_b") == "sensor" and c.get("relationship") == "CONFLICT":
            return {
                "recommended_action": "Repeat turbidity measurement",
                "reason": "Citizen observation and sensor evidence disagree.",
                "priority": "HIGH",
            }

    # Rule 2: Multiple sources conflict → human review
    conflict_count = sum(1 for c in comparisons if c.get("relationship") == "CONFLICT")
    if conflict_count >= 2:
        return {
            "recommended_action": "Request human review",
            "reason": f"Multiple evidence sources ({conflict_count}) conflict with each other.",
            "priority": "HIGH",
        }

    # Rule 3: Sensor missing → collect sensor data
    if not has_sensor:
        return {
            "recommended_action": "Collect sensor/turbidity measurement",
            "reason": "No sensor evidence available for cross-validation.",
            "priority": "HIGH",
        }

    # Rule 4: Satellite missing → collect satellite data
    if not has_satellite:
        return {
            "recommended_action": "Collect satellite imagery",
            "reason": "No satellite evidence available for cross-validation.",
            "priority": "MEDIUM",
        }

    # Rule 5: Historical missing → collect historical context
    if not has_historical:
        return {
            "recommended_action": "Collect historical baseline data",
            "reason": "No historical context available for comparison.",
            "priority": "MEDIUM",
        }

    # Rule 6: Weather missing → collect weather context
    if not has_weather:
        return {
            "recommended_action": "Collect weather/rainfall data",
            "reason": "No weather context available to explain observations.",
            "priority": "LOW",
        }

    # Rule 7: Insufficient evidence overall
    if evidence_status == "INSUFFICIENT_EVIDENCE":
        return {
            "recommended_action": "Collect additional independent evidence",
            "reason": "Current evidence is insufficient for reliable assessment.",
            "priority": "HIGH",
        }

    # Rule 8: Low quality citizen evidence
    citizen_quality = all_evidence.get("citizen", {}).get("quality", 0.7)
    if citizen_quality < 0.5:
        return {
            "recommended_action": "Request clearer photo or description",
            "reason": "Citizen evidence quality is low.",
            "priority": "MEDIUM",
        }

    # Rule 9: Satellite anomaly without ground truth
    if has_satellite and has_sensor:
        sat_data = all_evidence.get("satellite", {})
        anomaly = sat_data.get("anomaly_score", 0)
        if anomaly > 0.5:
            return {
                "recommended_action": "Verify satellite anomaly with field measurement",
                "reason": "Satellite anomaly detected but needs ground-truth confirmation.",
                "priority": "MEDIUM",
            }

    # Default: no specific next evidence needed
    return {
        "recommended_action": "Continue routine monitoring",
        "reason": "Evidence is sufficient for current assessment.",
        "priority": "LOW",
    }
