"""Tests for the assessment engine."""
from app.services.assessment_engine import determine_assessment


class TestDetermineAssessment:
    def test_visible_waste(self):
        citizen = {"visible_waste": True, "water_clarity": "clear"}
        result = determine_assessment(citizen, {}, "SUPPORTED", 0.8)
        assert "waste" in result.lower() or "contamination" in result.lower()

    def test_algae_bloom(self):
        citizen = {"algae": True, "water_clarity": "clear"}
        result = determine_assessment(citizen, {}, "SUPPORTED", 0.8)
        assert "algae" in result.lower()

    def test_chemical_odor(self):
        citizen = {"odor": "chemical", "water_clarity": "clear"}
        result = determine_assessment(citizen, {}, "SUPPORTED", 0.8)
        assert "chemical" in result.lower()

    def test_sewage_odor(self):
        citizen = {"odor": "sewage", "water_clarity": "clear"}
        result = determine_assessment(citizen, {}, "SUPPORTED", 0.8)
        assert "sewage" in result.lower()

    def test_opaque_high_confidence(self):
        citizen = {"water_clarity": "opaque"}
        result = determine_assessment(citizen, {}, "SUPPORTED", 0.8)
        assert "severe" in result.lower() or "pollution" in result.lower()

    def test_opaque_low_confidence(self):
        citizen = {"water_clarity": "opaque"}
        result = determine_assessment(citizen, {}, "INSUFFICIENT_EVIDENCE", 0.3)
        assert "verification" in result.lower() or "insufficient" in result.lower()

    def test_cloudy_supported(self):
        citizen = {"water_clarity": "cloudy"}
        result = determine_assessment(citizen, {}, "SUPPORTED", 0.8)
        assert "turbidity" in result.lower() or "stress" in result.lower()

    def test_cloudy_partial(self):
        citizen = {"water_clarity": "cloudy"}
        result = determine_assessment(citizen, {}, "PARTIALLY_SUPPORTED", 0.5)
        assert "partial" in result.lower() or "stress" in result.lower()

    def test_clear_water(self):
        citizen = {"water_clarity": "clear"}
        result = determine_assessment(citizen, {}, "SUPPORTED", 0.8)
        assert "normal" in result.lower()

    def test_slightly_cloudy(self):
        citizen = {"water_clarity": "slightly_cloudy"}
        result = determine_assessment(citizen, {}, "SUPPORTED", 0.8)
        assert "mild" in result.lower() or "acceptable" in result.lower()
