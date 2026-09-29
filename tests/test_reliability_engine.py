"""Tests for the reliability engine."""
from app.services.reliability_engine import (
    compute_reliability,
    compute_confidence,
    compute_uncertainty,
    determine_requires_review,
    run_reliability_engine,
)


class TestComputeReliability:
    def test_empty_evidence(self):
        assert compute_reliability({}, []) == 0.0

    def test_single_source(self):
        evidence = {"sensor": {"quality": 0.9}}
        result = compute_reliability(evidence, [])
        assert 0.0 < result < 1.0

    def test_multiple_sources_higher_reliability(self):
        evidence = {
            "sensor": {"quality": 0.9},
            "satellite": {"quality": 0.8},
            "historical": {"quality": 0.7},
        }
        result = compute_reliability(evidence, [])
        assert result > 0.3

    def test_high_quality_sources(self):
        evidence = {
            "sensor": {"quality": 0.95},
            "satellite": {"quality": 0.9},
        }
        result = compute_reliability(evidence, [])
        assert result > 0.4

    def test_low_quality_sources(self):
        evidence = {
            "sensor": {"quality": 0.2},
            "satellite": {"quality": 0.1},
        }
        result = compute_reliability(evidence, [])
        assert result < 0.5


class TestComputeConfidence:
    def test_supported_high_confidence(self):
        conf = compute_confidence(0.9, 0.8, "SUPPORTED")
        assert conf > 0.7

    def test_insufficient_low_confidence(self):
        conf = compute_confidence(0.2, 0.3, "INSUFFICIENT_EVIDENCE")
        assert conf < 0.3

    def test_contradicted_low_confidence(self):
        conf = compute_confidence(0.2, 0.5, "CONTRADICTED")
        assert conf < 0.4

    def test_reliability_and_confidence_differ(self):
        """Reliability and confidence should NOT be the same value."""
        conf = compute_confidence(0.5, 0.8, "PARTIALLY_SUPPORTED")
        rel = 0.8
        assert conf != rel


class TestComputeUncertainty:
    def test_high_confidence_low_uncertainty(self):
        unc = compute_uncertainty(0.9, 0, 0)
        assert unc < 0.2

    def test_low_confidence_high_uncertainty(self):
        unc = compute_uncertainty(0.2, 2, 1)
        assert unc > 0.5

    def test_conflicts_increase_uncertainty(self):
        unc_no_conflict = compute_uncertainty(0.7, 0, 0)
        unc_with_conflict = compute_uncertainty(0.7, 2, 0)
        assert unc_with_conflict > unc_no_conflict

    def test_missing_evidence_increases_uncertainty(self):
        unc_no_missing = compute_uncertainty(0.7, 0, 0)
        unc_with_missing = compute_uncertainty(0.7, 0, 2)
        assert unc_with_missing > unc_no_missing


class TestDetermineRequiresReview:
    def test_contradicted_requires_review(self):
        assert determine_requires_review(0.3, 0.5, "CONTRADICTED") is True

    def test_insufficient_requires_review(self):
        assert determine_requires_review(0.2, 0.8, "INSUFFICIENT_EVIDENCE") is True

    def test_low_confidence_requires_review(self):
        assert determine_requires_review(0.3, 0.4, "PARTIALLY_SUPPORTED") is True

    def test_high_confidence_no_review(self):
        assert determine_requires_review(0.85, 0.15, "SUPPORTED") is False

    def test_high_uncertainty_requires_review(self):
        assert determine_requires_review(0.6, 0.7, "PARTIALLY_SUPPORTED") is True


class TestRunReliabilityEngine:
    def test_full_pipeline(self):
        evidence = {
            "citizen": {"quality": 0.7},
            "sensor": {"quality": 0.9},
            "satellite": {"quality": 0.7},
        }
        comparisons = [
            {"relationship": "AGREEMENT", "agreement_score": 0.9},
            {"relationship": "AGREEMENT", "agreement_score": 0.7},
        ]
        result = run_reliability_engine(evidence, comparisons, 0.8, "SUPPORTED")
        assert result["reliability"] > 0.4
        assert result["confidence"] > 0.5
        assert result["uncertainty"] < 0.5
        assert result["requires_review"] is False

    def test_high_agreement_high_reliability(self):
        evidence = {
            "citizen": {"quality": 0.8},
            "sensor": {"quality": 0.9},
            "satellite": {"quality": 0.85},
            "historical": {"quality": 0.75},
        }
        comparisons = [
            {"relationship": "AGREEMENT", "agreement_score": 0.9},
            {"relationship": "AGREEMENT", "agreement_score": 0.85},
            {"relationship": "AGREEMENT", "agreement_score": 0.8},
        ]
        result = run_reliability_engine(evidence, comparisons, 0.85, "SUPPORTED")
        assert result["reliability"] > 0.5
        assert result["confidence"] > 0.6
        assert result["requires_review"] is False

    def test_high_conflict_low_confidence(self):
        evidence = {
            "citizen": {"quality": 0.7},
            "sensor": {"quality": 0.9},
        }
        comparisons = [
            {"relationship": "CONFLICT", "agreement_score": 0.1},
        ]
        result = run_reliability_engine(evidence, comparisons, 0.1, "CONTRADICTED")
        assert result["confidence"] < 0.4
        assert result["requires_review"] is True

    def test_missing_evidence_low_confidence(self):
        evidence = {"citizen": {"quality": 0.7}}
        comparisons = []
        result = run_reliability_engine(evidence, comparisons, 0.0, "INSUFFICIENT_EVIDENCE")
        assert result["confidence"] < 0.3
        assert result["requires_review"] is True

    def test_low_quality_source_reduces_reliability(self):
        evidence = {
            "citizen": {"quality": 0.3},
            "sensor": {"quality": 0.2},
        }
        comparisons = [
            {"relationship": "AGREEMENT", "agreement_score": 0.5},
        ]
        result = run_reliability_engine(evidence, comparisons, 0.5, "PARTIALLY_SUPPORTED")
        assert result["reliability"] < 0.5
