"""Tests for the conflict engine."""
from app.services.conflict_engine import (
    run_conflict_engine,
    Relationship,
    compare_citizen_sensor,
    compare_citizen_satellite,
    compare_citizen_historical,
    _classify_turbidity,
)


class TestClassifyTurbidity:
    def test_low(self):
        assert _classify_turbidity(3.0) == "low"

    def test_moderate(self):
        assert _classify_turbidity(15.0) == "moderate"

    def test_high(self):
        assert _classify_turbidity(35.0) == "high"

    def test_very_high(self):
        assert _classify_turbidity(75.0) == "very_high"


class TestCompareCitizenSensor:
    def test_agreement(self):
        citizen = {"water_clarity": "cloudy"}
        sensor = {"turbidity": 35.0}
        rel, score, _ = compare_citizen_sensor(citizen, sensor)
        assert rel == Relationship.AGREEMENT
        assert score > 0.8

    def test_conflict(self):
        citizen = {"water_clarity": "opaque"}
        sensor = {"turbidity": 3.0}
        rel, score, _ = compare_citizen_sensor(citizen, sensor)
        assert rel == Relationship.CONFLICT
        assert score < 0.3

    def test_missing(self):
        citizen = {"water_clarity": "cloudy"}
        sensor = {}
        rel, score, _ = compare_citizen_sensor(citizen, sensor)
        assert rel == Relationship.MISSING


class TestCompareCitizenSatellite:
    def test_agreement_algae(self):
        citizen = {"algae": True}
        satellite = {"ndvi": 0.5}
        rel, score, _ = compare_citizen_satellite(citizen, satellite)
        assert rel == Relationship.AGREEMENT

    def test_conflict_algae(self):
        citizen = {"algae": True}
        satellite = {"ndvi": 0.1}
        rel, score, _ = compare_citizen_satellite(citizen, satellite)
        assert rel == Relationship.CONFLICT

    def test_missing(self):
        citizen = {"algae": True}
        satellite = {}
        rel, score, _ = compare_citizen_satellite(citizen, satellite)
        assert rel == Relationship.MISSING


class TestCompareCitizenHistorical:
    def test_agreement_abnormal(self):
        citizen = {"water_clarity": "cloudy", "visible_waste": False, "algae": False}
        historical = {"baseline_normal": False}
        rel, score, _ = compare_citizen_historical(citizen, historical)
        assert rel == Relationship.AGREEMENT

    def test_conflict_normal_baseline(self):
        citizen = {"water_clarity": "cloudy", "visible_waste": True, "algae": False}
        historical = {"baseline_normal": True}
        rel, score, _ = compare_citizen_historical(citizen, historical)
        assert rel == Relationship.CONFLICT


class TestRunConflictEngine:
    def test_scenario_1_agreement(self):
        """Citizen cloudy + sensor high turbidity + satellite anomaly = SUPPORTED."""
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
        result = run_conflict_engine(citizen, all_evidence)
        assert result["evidence_status"] == "SUPPORTED"
        assert result["agreement_score"] > 0.6

    def test_scenario_2_citizen_conflict(self):
        """Citizen opaque + sensor normal + satellite no anomaly = CONTRADICTED."""
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
        result = run_conflict_engine(citizen, all_evidence)
        assert result["evidence_status"] == "CONTRADICTED"
        assert len(result["conflicts"]) > 0

    def test_scenario_3_partial(self):
        """Citizen cloudy + sensor normal + satellite anomaly = PARTIALLY_SUPPORTED."""
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
        result = run_conflict_engine(citizen, all_evidence)
        assert result["evidence_status"] == "PARTIALLY_SUPPORTED"

    def test_scenario_4_insufficient(self):
        """Citizen cloudy + no sensor + satellite unclear = INSUFFICIENT_EVIDENCE."""
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
        result = run_conflict_engine(citizen, all_evidence)
        assert result["evidence_status"] == "INSUFFICIENT_EVIDENCE"

    def test_full_agreement_all_sources(self):
        """All sources agree with citizen observation."""
        citizen = {
            "water_clarity": "cloudy",
            "visible_waste": False,
            "algae": True,
            "odor": "none",
        }
        all_evidence = {
            "citizen": citizen,
            "sensor": {"turbidity": 35.0, "quality": 0.9},
            "satellite": {"ndvi": 0.5, "quality": 0.8},
            "historical": {"baseline_normal": False, "quality": 0.7},
            "weather": {"rainfall_mm": 25.0, "quality": 0.6},
        }
        result = run_conflict_engine(citizen, all_evidence)
        assert result["evidence_status"] == "SUPPORTED"
        assert len(result["conflicts"]) == 0
        assert len(result["supporting_evidence"]) >= 3

    def test_multiple_conflicting_sources(self):
        """Multiple sources conflict with citizen."""
        citizen = {
            "water_clarity": "opaque",
            "visible_waste": True,
            "algae": False,
            "odor": "sewage",
        }
        all_evidence = {
            "citizen": citizen,
            "sensor": {"turbidity": 2.0, "quality": 0.9},
            "satellite": {"anomaly_score": 0.05, "quality": 0.8},
            "historical": {"baseline_normal": True, "quality": 0.7},
        }
        result = run_conflict_engine(citizen, all_evidence)
        assert result["evidence_status"] == "CONTRADICTED"
        assert len(result["conflicts"]) >= 2

    def test_single_weak_source(self):
        """Only one source with low quality."""
        citizen = {
            "water_clarity": "cloudy",
            "visible_waste": False,
            "algae": False,
            "odor": "none",
        }
        all_evidence = {
            "citizen": citizen,
            "sensor": {"turbidity": 20.0, "quality": 0.3},
        }
        result = run_conflict_engine(citizen, all_evidence)
        # Single source with partial agreement -> INSUFFICIENT or PARTIAL
        assert result["evidence_status"] in ("INSUFFICIENT_EVIDENCE", "PARTIALLY_SUPPORTED")

    def test_no_evidence_at_all(self):
        """No evidence sources besides citizen."""
        citizen = {
            "water_clarity": "cloudy",
            "visible_waste": False,
            "algae": False,
            "odor": "none",
        }
        all_evidence = {"citizen": citizen}
        result = run_conflict_engine(citizen, all_evidence)
        assert result["evidence_status"] == "INSUFFICIENT_EVIDENCE"
        assert result["agreement_score"] == 0.0

    def test_conflict_identifies_source_pair(self):
        """Each conflict should identify the source pair."""
        citizen = {
            "water_clarity": "opaque",
            "visible_waste": False,
            "algae": False,
            "odor": "none",
        }
        all_evidence = {
            "citizen": citizen,
            "sensor": {"turbidity": 2.0, "quality": 0.9},
        }
        result = run_conflict_engine(citizen, all_evidence)
        assert len(result["comparisons"]) == 1
        comp = result["comparisons"][0]
        assert comp["source_a"] == "citizen"
        assert comp["source_b"] == "sensor"
        assert comp["relationship"] == Relationship.CONFLICT
