"""
Alignment service — spatial, temporal, and quality alignment of evidence.

All scores are prototype alignment metrics (0.0–1.0), NOT scientifically validated.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2


# ---------------------------------------------------------------------------
# Continuous scoring functions (new)
# ---------------------------------------------------------------------------

def spatial_score(loc_a: Dict[str, float], loc_b: Dict[str, float], threshold_km: float = 5.0) -> float:
    """
    Continuous spatial alignment score (0.0–1.0).
    1.0 = same location, 0.0 = at or beyond threshold distance.
    """
    if not loc_a or not loc_b:
        return 0.5  # neutral when location missing

    lat1, lon1 = loc_a.get("lat", 0), loc_a.get("lon", 0)
    lat2, lon2 = loc_b.get("lat", 0), loc_b.get("lon", 0)

    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    if distance >= threshold_km:
        return 0.0
    return round(1.0 - (distance / threshold_km), 2)


def temporal_score(ts_a: Optional[datetime], ts_b: Optional[datetime], threshold_hours: float = 24.0) -> float:
    """
    Continuous temporal alignment score (0.0–1.0).
    1.0 = same timestamp, 0.0 = at or beyond threshold.
    """
    if ts_a is None or ts_b is None:
        return 0.5  # neutral when timestamp missing

    diff_hours = abs((ts_a - ts_b).total_seconds()) / 3600.0
    if diff_hours >= threshold_hours:
        return 0.0
    return round(1.0 - (diff_hours / threshold_hours), 2)


def compute_alignment_score(spatial: float, temporal: float, quality: float) -> float:
    """
    Overall alignment score — weighted combination of spatial, temporal, and quality.
    Weights: spatial 0.35, temporal 0.25, quality 0.40
    """
    score = 0.35 * spatial + 0.25 * temporal + 0.40 * quality
    return round(min(max(score, 0.0), 1.0), 2)


# ---------------------------------------------------------------------------
# Legacy boolean functions (kept for backward compatibility)
# ---------------------------------------------------------------------------

def spatial_match(loc_a: Dict[str, float], loc_b: Dict[str, float], threshold_km: float = 5.0) -> bool:
    """Simple haversine-based spatial match (boolean)."""
    if not loc_a or not loc_b:
        return True
    return spatial_score(loc_a, loc_b, threshold_km) > 0.0


def temporal_match(ts_a: Optional[datetime], ts_b: Optional[datetime], threshold_hours: float = 24.0) -> bool:
    """Check if two timestamps are within threshold (boolean)."""
    if ts_a is None or ts_b is None:
        return True
    return temporal_score(ts_a, ts_b, threshold_hours) > 0.0


def compute_source_quality(evidence: Dict[str, Any]) -> float:
    """Extract quality score from evidence entry."""
    return evidence.get("quality", 0.5)


# ---------------------------------------------------------------------------
# Main alignment entry point
# ---------------------------------------------------------------------------

def align_evidence(
    citizen_evidence: Dict[str, Any],
    all_evidence: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Align citizen evidence against all other sources.
    Returns list of alignment results with continuous scores.
    """
    alignments = []
    citizen_loc = citizen_evidence.get("location", {})
    citizen_ts = citizen_evidence.get("timestamp")

    for source, data in all_evidence.items():
        if source == "citizen":
            continue

        loc = data.get("location", {})
        ts = data.get("timestamp")

        spatial = spatial_score(citizen_loc, loc)
        temporal = temporal_score(citizen_ts, ts)
        quality = compute_source_quality(data)
        alignment_score = compute_alignment_score(spatial, temporal, quality)

        alignments.append({
            "source": source,
            "spatial_match": spatial,
            "temporal_match": temporal,
            "source_quality": quality,
            "alignment_score": alignment_score,
            "aligned": spatial > 0.0 and temporal > 0.0,
        })

    return alignments
