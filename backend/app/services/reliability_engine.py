"""
Reliability Engine — computes evidence reliability, confidence, and uncertainty.

Key distinction:
- Reliability: how trustworthy is the evidence? (source quality, coverage)
- Confidence: how confident is the system in the final assessment?
- Uncertainty: how much doubt remains?
"""
from typing import Dict, Any, List


def compute_reliability(all_evidence: Dict[str, Dict[str, Any]], comparisons: List[Dict[str, Any]]) -> float:
    """
    Compute evidence reliability based on:
    - Source quality scores
    - Number of independent sources
    - Source diversity
    """
    if not all_evidence:
        return 0.0

    # Average quality across sources
    qualities = [data.get("quality", 0.5) for data in all_evidence.values()]
    avg_quality = sum(qualities) / len(qualities)

    # Source count bonus (more sources = more reliable, up to a point)
    source_count = len(all_evidence)
    count_factor = min(source_count / 4.0, 1.0)  # normalize to 4 sources

    # Source diversity bonus
    source_types = set(all_evidence.keys())
    diversity_factor = min(len(source_types) / 4.0, 1.0)

    # Agreement factor from comparisons
    if comparisons:
        agreement_scores = [c.get("agreement_score", 0.5) for c in comparisons]
        avg_agreement = sum(agreement_scores) / len(agreement_scores)
    else:
        avg_agreement = 0.5

    # Weighted combination
    reliability = (
        0.30 * avg_quality
        + 0.20 * count_factor
        + 0.15 * diversity_factor
        + 0.35 * avg_agreement
    )

    return round(min(max(reliability, 0.0), 1.0), 2)


def compute_confidence(agreement_score: float, reliability: float, evidence_status: str) -> float:
    """
    Compute final assessment confidence.
    Combines agreement, reliability, and evidence status.
    """
    # Base confidence from agreement and reliability
    base = 0.5 * agreement_score + 0.5 * reliability

    # Adjust based on evidence status
    status_multiplier = {
        "SUPPORTED": 1.0,
        "PARTIALLY_SUPPORTED": 0.75,
        "UNCERTAIN": 0.5,
        "CONTRADICTED": 0.3,
        "INSUFFICIENT_EVIDENCE": 0.2,
    }

    multiplier = status_multiplier.get(evidence_status, 0.5)
    confidence = base * multiplier

    return round(min(max(confidence, 0.0), 1.0), 2)


def compute_uncertainty(confidence: float, conflict_count: int, missing_count: int) -> float:
    """
    Compute uncertainty — increases with conflicts and missing evidence.
    """
    base_uncertainty = 1.0 - confidence
    conflict_penalty = min(conflict_count * 0.1, 0.3)
    missing_penalty = min(missing_count * 0.15, 0.3)

    uncertainty = base_uncertainty + conflict_penalty + missing_penalty
    return round(min(uncertainty, 1.0), 2)


def determine_requires_review(confidence: float, uncertainty: float, evidence_status: str) -> bool:
    """Determine if human review is required."""
    if evidence_status in ("CONTRADICTED", "INSUFFICIENT_EVIDENCE"):
        return True
    if confidence < 0.5:
        return True
    if uncertainty > 0.6:
        return True
    return False


def run_reliability_engine(
    all_evidence: Dict[str, Dict[str, Any]],
    comparisons: List[Dict[str, Any]],
    agreement_score: float,
    evidence_status: str,
) -> Dict[str, Any]:
    """Main reliability engine entry point."""
    reliability = compute_reliability(all_evidence, comparisons)
    confidence = compute_confidence(agreement_score, reliability, evidence_status)

    conflict_count = sum(1 for c in comparisons if c.get("relationship") == "CONFLICT")
    missing_count = sum(1 for c in comparisons if c.get("relationship") == "MISSING")

    uncertainty = compute_uncertainty(confidence, conflict_count, missing_count)
    requires_review = determine_requires_review(confidence, uncertainty, evidence_status)

    return {
        "reliability": reliability,
        "confidence": confidence,
        "uncertainty": uncertainty,
        "requires_review": requires_review,
    }
