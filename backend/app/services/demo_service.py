"""
Demo Scenario Service — four deterministic scenarios for hackathon demo.
"""
from typing import Dict, Any, List
from datetime import datetime


SCENARIOS = {
    "agreement": {
        "scenario_id": "agreement",
        "name": "Multi-source Agreement",
        "description": "Citizen reports cloudy water. Sensor confirms high turbidity. Satellite shows moderate anomaly.",
        "expected_status": "SUPPORTED",
        "observation": {
            "latitude": 52.123,
            "longitude": 5.123,
            "timestamp": "2026-09-28T10:30:00",
            "water_clarity": "cloudy",
            "visible_waste": False,
            "algae": False,
            "odor": "none",
        },
        "evidence": [
            {
                "source_type": "sensor",
                "timestamp": "2026-09-28T10:20:00",
                "location": {"lat": 52.123, "lon": 5.123},
                "payload": {"turbidity": 35.0, "ph": 7.4, "conductivity": 820},
                "quality_score": 0.9,
            },
            {
                "source_type": "satellite",
                "timestamp": "2026-09-28T10:00:00",
                "location": {"lat": 52.123, "lon": 5.123},
                "payload": {"anomaly_score": 0.7, "ndvi": 0.3},
                "quality_score": 0.7,
            },
            {
                "source_type": "historical",
                "timestamp": "2026-09-27T10:00:00",
                "location": {"lat": 52.123, "lon": 5.123},
                "payload": {"baseline_normal": False, "turbidity": 30.0},
                "quality_score": 0.8,
            },
        ],
    },
    "citizen_conflict": {
        "scenario_id": "citizen_conflict",
        "name": "Citizen Conflict",
        "description": "Citizen reports highly polluted water. Sensor shows normal turbidity. Satellite shows no anomaly.",
        "expected_status": "CONTRADICTED",
        "observation": {
            "latitude": 52.123,
            "longitude": 5.123,
            "timestamp": "2026-09-28T10:30:00",
            "water_clarity": "opaque",
            "visible_waste": True,
            "algae": False,
            "odor": "chemical",
        },
        "evidence": [
            {
                "source_type": "sensor",
                "timestamp": "2026-09-28T10:20:00",
                "location": {"lat": 52.123, "lon": 5.123},
                "payload": {"turbidity": 3.0, "ph": 7.1, "conductivity": 400},
                "quality_score": 0.9,
            },
            {
                "source_type": "satellite",
                "timestamp": "2026-09-28T10:00:00",
                "location": {"lat": 52.123, "lon": 5.123},
                "payload": {"anomaly_score": 0.1, "ndvi": 0.2},
                "quality_score": 0.7,
            },
            {
                "source_type": "historical",
                "timestamp": "2026-09-27T10:00:00",
                "location": {"lat": 52.123, "lon": 5.123},
                "payload": {"baseline_normal": True, "turbidity": 4.0},
                "quality_score": 0.8,
            },
        ],
    },
    "sensor_conflict": {
        "scenario_id": "sensor_conflict",
        "name": "Sensor Conflict",
        "description": "Citizen reports cloudy water. Sensor shows normal. Satellite shows moderate anomaly.",
        "expected_status": "PARTIALLY_SUPPORTED",
        "observation": {
            "latitude": 52.123,
            "longitude": 5.123,
            "timestamp": "2026-09-28T10:30:00",
            "water_clarity": "cloudy",
            "visible_waste": False,
            "algae": False,
            "odor": "none",
        },
        "evidence": [
            {
                "source_type": "sensor",
                "timestamp": "2026-09-28T10:20:00",
                "location": {"lat": 52.123, "lon": 5.123},
                "payload": {"turbidity": 5.0, "ph": 7.2, "conductivity": 500},
                "quality_score": 0.9,
            },
            {
                "source_type": "satellite",
                "timestamp": "2026-09-28T10:00:00",
                "location": {"lat": 52.123, "lon": 5.123},
                "payload": {"anomaly_score": 0.7, "ndvi": 0.35},
                "quality_score": 0.7,
            },
        ],
    },
    "missing_evidence": {
        "scenario_id": "missing_evidence",
        "name": "Missing Evidence",
        "description": "Citizen reports cloudy water. No sensor data. Satellite unclear.",
        "expected_status": "INSUFFICIENT_EVIDENCE",
        "observation": {
            "latitude": 52.123,
            "longitude": 5.123,
            "timestamp": "2026-09-28T10:30:00",
            "water_clarity": "cloudy",
            "visible_waste": False,
            "algae": False,
            "odor": "none",
        },
        "evidence": [
            {
                "source_type": "satellite",
                "timestamp": "2026-09-28T10:00:00",
                "location": {"lat": 52.123, "lon": 5.123},
                "payload": {"anomaly_score": 0.4, "ndvi": 0.25},
                "quality_score": 0.3,
            },
        ],
    },
}


def get_all_scenarios() -> List[Dict[str, Any]]:
    """Return all scenario metadata (without full data)."""
    return [
        {
            "scenario_id": s["scenario_id"],
            "name": s["name"],
            "description": s["description"],
            "expected_status": s["expected_status"],
        }
        for s in SCENARIOS.values()
    ]


def get_scenario(scenario_id: str) -> Dict[str, Any]:
    """Get a specific scenario by ID."""
    return SCENARIOS.get(scenario_id)
