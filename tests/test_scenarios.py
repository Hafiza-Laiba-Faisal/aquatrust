"""Integration tests for the four deterministic demo scenarios."""
from app.services.conflict_engine import run_conflict_engine
from app.services.reliability_engine import run_reliability_engine
from app.services.assessment_engine import run_assessment_engine


def run_full_pipeline(citizen, all_evidence):
    """Run the complete assessment pipeline."""
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
    return {
        "conflict": conflict_result,
        "reliability": reliability_result,
        "assessment": assessment_label,
    }


class TestScenario1Agreement:
    """Citizen cloudy + sensor high turbidity + satellite anomaly."""

    def test_scenario_1(self):
        citizen = {
            "water_clarity": "cloudy",
            "visible_waste": False,
            "algae": False,
            "odor": "none",
        }
        all_evidence = {
            "citizen": citizen,
            "sensor": {"turbidity": 35.0, "quality": 0.9},
            "satellite": {"anomaly_score": 0.7, "quality": 0.7},
        }
        result = run_full_pipeline(citizen, all_evidence)

        assert result["conflict"]["evidence_status"] == "SUPPORTED"
        assert result["reliability"]["confidence"] > 0.5
        assert result["reliability"]["requires_review"] is False
        assert "turbidity" in result["assessment"].lower() or "stress" in result["assessment"].lower()


class TestScenario2CitizenConflict:
    """Citizen opaque + sensor normal + satellite no anomaly."""

    def test_scenario_2(self):
        citizen = {
            "water_clarity": "opaque",
            "visible_waste": True,
            "algae": False,
            "odor": "chemical",
        }
        all_evidence = {
            "citizen": citizen,
            "sensor": {"turbidity": 3.0, "quality": 0.9},
            "satellite": {"anomaly_score": 0.1, "quality": 0.7},
        }
        result = run_full_pipeline(citizen, all_evidence)

        assert result["conflict"]["evidence_status"] == "CONTRADICTED"
        assert result["reliability"]["confidence"] < 0.5
        assert result["reliability"]["requires_review"] is True
        assert len(result["conflict"]["conflicts"]) > 0


class TestScenario3PartialSupport:
    """Citizen cloudy + sensor normal + satellite anomaly."""

    def test_scenario_3(self):
        citizen = {
            "water_clarity": "cloudy",
            "visible_waste": False,
            "algae": False,
            "odor": "none",
        }
        all_evidence = {
            "citizen": citizen,
            "sensor": {"turbidity": 5.0, "quality": 0.9},
            "satellite": {"anomaly_score": 0.7, "quality": 0.7},
        }
        result = run_full_pipeline(citizen, all_evidence)

        assert result["conflict"]["evidence_status"] == "PARTIALLY_SUPPORTED"
        assert result["reliability"]["requires_review"] is True


class TestScenario4InsufficientEvidence:
    """Citizen cloudy + no sensor + satellite unclear."""

    def test_scenario_4(self):
        citizen = {
            "water_clarity": "cloudy",
            "visible_waste": False,
            "algae": False,
            "odor": "none",
        }
        all_evidence = {
            "citizen": citizen,
            "satellite": {"anomaly_score": 0.4, "quality": 0.3},
        }
        result = run_full_pipeline(citizen, all_evidence)

        assert result["conflict"]["evidence_status"] == "INSUFFICIENT_EVIDENCE"
        assert result["reliability"]["confidence"] < 0.4
        assert result["reliability"]["requires_review"] is True
