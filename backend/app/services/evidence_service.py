"""Evidence service — retrieves and normalizes evidence from all sources."""
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.models.evidence import Evidence, SourceType


def get_evidence_for_observation(db, observation_id: UUID) -> List[Evidence]:
    """Retrieve all evidence records for a given observation."""
    return db.query(Evidence).filter(Evidence.observation_id == observation_id).all()


def normalize_evidence(evidence_list: List[Evidence]) -> Dict[str, Dict[str, Any]]:
    """
    Convert evidence list into a normalized dict keyed by source_type.
    Each entry contains measurements and quality.
    """
    normalized = {}
    for ev in evidence_list:
        normalized[ev.source_type] = {
            "measurements": ev.payload,
            "quality": ev.quality_score,
            "timestamp": ev.timestamp,
            "location": ev.location,
        }
    return normalized


def get_citizen_evidence(db, observation) -> Dict[str, Any]:
    """Convert citizen observation into evidence-format dict."""
    return {
        "measurements": {
            "water_clarity": observation.water_clarity,
            "visible_waste": observation.visible_waste,
            "algae": observation.algae,
            "odor": observation.odor,
        },
        "quality": 0.7,  # citizen observations have moderate baseline quality
        "timestamp": observation.timestamp,
        "location": {"lat": observation.latitude, "lon": observation.longitude},
    }
