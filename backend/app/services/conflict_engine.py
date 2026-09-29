"""
Conflict Engine — the core of AquaTrust.
Compares citizen observation against all evidence sources and determines
agreement, partial agreement, conflict, or missing evidence.
"""
from typing import Dict, Any, List, Tuple
from enum import Enum


class Relationship(str, Enum):
    AGREEMENT = "AGREEMENT"
    PARTIAL = "PARTIAL"
    CONFLICT = "CONFLICT"
    MISSING = "MISSING"


# Mapping of citizen observations to expected sensor/satellite signals
# This is the knowledge base for conflict detection
SIGNAL_MAP = {
    "water_clarity": {
        "clear": {"turbidity": "low", "turbidity_max": 5},
        "slightly_cloudy": {"turbidity": "moderate", "turbidity_max": 25},
        "cloudy": {"turbidity": "high", "turbidity_max": 50},
        "opaque": {"turbidity": "very_high", "turbidity_max": 100},
    },
    "visible_waste": {
        True: {"waste_detected": True},
        False: {"waste_detected": False},
    },
    "algae": {
        True: {"vegetation_index": "high", "ndvi_min": 0.4},
        False: {"vegetation_index": "low", "ndvi_max": 0.3},
    },
    "odor": {
        "none": {"contamination": "none"},
        "earthy": {"contamination": "organic"},
        "chemical": {"contamination": "chemical"},
        "sewage": {"contamination": "sewage"},
    },
}


def _classify_turbidity(value: float) -> str:
    if value <= 5:
        return "low"
    elif value <= 25:
        return "moderate"
    elif value <= 50:
        return "high"
    else:
        return "very_high"


def _classify_ndvi(value: float) -> str:
    if value < 0.2:
        return "low"
    elif value < 0.4:
        return "moderate"
    else:
        return "high"


def compare_citizen_sensor(citizen: Dict[str, Any], sensor: Dict[str, Any]) -> Tuple[Relationship, float, str]:
    """Compare citizen observation against sensor data."""
    citizen_clarity = citizen.get("water_clarity")
    sensor_turbidity = sensor.get("turbidity")

    if sensor_turbidity is None:
        return Relationship.MISSING, 0.0, "No sensor turbidity data available"

    sensor_class = _classify_turbidity(sensor_turbidity)
    expected = SIGNAL_MAP["water_clarity"].get(citizen_clarity, {})
    expected_class = expected.get("turbidity", "unknown")

    if sensor_class == expected_class:
        return Relationship.AGREEMENT, 0.9, f"Citizen reports {citizen_clarity}, sensor confirms {sensor_class} turbidity"
    elif (sensor_class == "low" and expected_class in ("high", "very_high")) or \
         (sensor_class in ("high", "very_high") and expected_class == "low"):
        return Relationship.CONFLICT, 0.1, f"Citizen reports {citizen_clarity} but sensor shows {sensor_class} turbidity"
    else:
        return Relationship.PARTIAL, 0.5, f"Citizen reports {citizen_clarity}, sensor shows {sensor_class} turbidity — partial match"


def compare_citizen_satellite(citizen: Dict[str, Any], satellite: Dict[str, Any]) -> Tuple[Relationship, float, str]:
    """Compare citizen observation against satellite data."""
    citizen_algae = citizen.get("algae")
    satellite_ndvi = satellite.get("ndvi")
    satellite_anomaly = satellite.get("anomaly_score")

    if satellite_ndvi is None and satellite_anomaly is None:
        return Relationship.MISSING, 0.0, "No satellite data available"

    # High anomaly score is strong evidence — check first
    if satellite_anomaly is not None and satellite_anomaly > 0.6:
        return Relationship.AGREEMENT, 0.7, "Satellite anomaly supports citizen observation of abnormal conditions"

    if citizen_algae is not None and satellite_ndvi is not None:
        ndvi_class = _classify_ndvi(satellite_ndvi)
        if citizen_algae and ndvi_class == "high":
            return Relationship.AGREEMENT, 0.85, "Citizen reports algae, satellite confirms high vegetation index"
        elif not citizen_algae and ndvi_class == "low":
            return Relationship.AGREEMENT, 0.85, "Citizen reports no algae, satellite confirms low vegetation index"
        elif citizen_algae and ndvi_class == "low":
            return Relationship.CONFLICT, 0.15, "Citizen reports algae but satellite shows low vegetation index"
        else:
            return Relationship.PARTIAL, 0.5, "Partial match between citizen and satellite data"

    if satellite_anomaly is not None:
        if satellite_anomaly < 0.3:
            return Relationship.CONFLICT, 0.2, "Satellite shows no significant anomaly, contradicting citizen observation"
        else:
            return Relationship.PARTIAL, 0.5, "Satellite shows moderate anomaly — partial support"

    return Relationship.PARTIAL, 0.5, "Insufficient satellite data for strong comparison"


def compare_citizen_historical(citizen: Dict[str, Any], historical: Dict[str, Any]) -> Tuple[Relationship, float, str]:
    """Compare citizen observation against historical baseline."""
    historical_normal = historical.get("baseline_normal", True)
    historical_turbidity = historical.get("turbidity")

    citizen_clarity = citizen.get("water_clarity")
    citizen_abnormal = citizen_clarity in ("cloudy", "opaque") or citizen.get("visible_waste") or citizen.get("algae")

    if historical_normal and citizen_abnormal:
        return Relationship.CONFLICT, 0.2, "Citizen reports abnormal conditions but historical baseline is normal"
    elif not historical_normal and citizen_abnormal:
        return Relationship.AGREEMENT, 0.8, "Citizen reports abnormal conditions, historical baseline also shows anomalies"
    elif historical_normal and not citizen_abnormal:
        return Relationship.AGREEMENT, 0.85, "Citizen reports normal conditions, consistent with historical baseline"
    else:
        return Relationship.PARTIAL, 0.5, "Historical data partially consistent with citizen observation"


def compare_citizen_weather(citizen: Dict[str, Any], weather: Dict[str, Any]) -> Tuple[Relationship, float, str]:
    """Compare citizen observation against weather context."""
    rainfall = weather.get("rainfall_mm", 0)
    heavy_rain = rainfall > 20

    citizen_clarity = citizen.get("water_clarity")
    citizen_abnormal = citizen_clarity in ("cloudy", "opaque")

    if heavy_rain and citizen_abnormal:
        return Relationship.AGREEMENT, 0.75, "Heavy rainfall supports citizen observation of cloudy/abnormal water"
    elif not heavy_rain and citizen_abnormal:
        return Relationship.PARTIAL, 0.4, "No heavy rainfall to explain abnormal observation — partial support"
    else:
        return Relationship.AGREEMENT, 0.6, "Weather conditions consistent with citizen observation"


def run_conflict_engine(
    citizen: Dict[str, Any],
    all_evidence: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Main conflict engine entry point.
    Compares citizen evidence against all available sources.
    """
    comparisons = []
    agreement_scores = []
    conflicts = []
    supporting = []

    comparators = {
        "sensor": compare_citizen_sensor,
        "satellite": compare_citizen_satellite,
        "historical": compare_citizen_historical,
        "weather": compare_citizen_weather,
    }

    for source, comparator in comparators.items():
        if source not in all_evidence:
            continue

        relationship, score, explanation = comparator(citizen, all_evidence[source])
        comparisons.append({
            "source_a": "citizen",
            "source_b": source,
            "relationship": relationship,
            "agreement_score": score,
            "explanation": explanation,
        })
        agreement_scores.append(score)

        if relationship == Relationship.AGREEMENT:
            supporting.append(explanation)
        elif relationship == Relationship.CONFLICT:
            conflicts.append(explanation)

    # Compute overall agreement score
    if agreement_scores:
        overall_agreement = sum(agreement_scores) / len(agreement_scores)
    else:
        overall_agreement = 0.0

    # Determine evidence status
    has_conflict = any(c["relationship"] == Relationship.CONFLICT for c in comparisons)
    has_agreement = any(c["relationship"] == Relationship.AGREEMENT for c in comparisons)
    all_missing = all(c["relationship"] == Relationship.MISSING for c in comparisons) if comparisons else True
    # Count non-missing comparisons
    non_missing = [c for c in comparisons if c["relationship"] != Relationship.MISSING]

    if all_missing or len(non_missing) == 0:
        evidence_status = "INSUFFICIENT_EVIDENCE"
    elif has_conflict and has_agreement:
        evidence_status = "PARTIALLY_SUPPORTED"
    elif has_conflict:
        evidence_status = "CONTRADICTED"
    elif has_agreement and len(non_missing) >= 2:
        evidence_status = "SUPPORTED"
    elif has_agreement and len(non_missing) == 1:
        # Only one supporting source — not enough for full support
        evidence_status = "PARTIALLY_SUPPORTED"
    elif len(non_missing) == 1:
        # Only one source with partial/uncertain agreement
        evidence_status = "INSUFFICIENT_EVIDENCE"
    else:
        evidence_status = "UNCERTAIN"

    return {
        "agreement_score": round(overall_agreement, 2),
        "conflicts": conflicts,
        "supporting_evidence": supporting,
        "comparisons": comparisons,
        "evidence_status": evidence_status,
    }
