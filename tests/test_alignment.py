"""Tests for spatial and temporal alignment."""
from datetime import datetime, timedelta

from app.services.alignment_service import (
    spatial_match,
    temporal_match,
    compute_source_quality,
    align_evidence,
    spatial_score,
    temporal_score,
    compute_alignment_score,
)


class TestSpatialScore:
    def test_same_location(self):
        loc = {"lat": 52.123, "lon": 5.123}
        assert spatial_score(loc, loc) == 1.0

    def test_very_close(self):
        loc_a = {"lat": 52.123, "lon": 5.123}
        loc_b = {"lat": 52.1231, "lon": 5.1231}
        score = spatial_score(loc_a, loc_b)
        assert score > 0.9

    def test_distant(self):
        loc_a = {"lat": 52.123, "lon": 5.123}
        loc_b = {"lat": 48.856, "lon": 2.352}
        assert spatial_score(loc_a, loc_b) == 0.0

    def test_missing_location(self):
        assert spatial_score({}, {"lat": 52.0, "lon": 5.0}) == 0.5
        assert spatial_score({"lat": 52.0, "lon": 5.0}, {}) == 0.5

    def test_custom_threshold(self):
        loc_a = {"lat": 52.123, "lon": 5.123}
        loc_b = {"lat": 52.133, "lon": 5.133}
        assert spatial_score(loc_a, loc_b, threshold_km=1.0) == 0.0
        assert spatial_score(loc_a, loc_b, threshold_km=2.0) > 0.0


class TestTemporalScore:
    def test_same_timestamp(self):
        ts = datetime(2026, 9, 28, 10, 0, 0)
        assert temporal_score(ts, ts) == 1.0

    def test_one_hour_apart(self):
        ts_a = datetime(2026, 9, 28, 10, 0, 0)
        ts_b = datetime(2026, 9, 28, 11, 0, 0)
        score = temporal_score(ts_a, ts_b)
        assert 0.9 < score <= 1.0

    def test_old_evidence(self):
        ts_a = datetime(2026, 9, 28, 10, 0, 0)
        ts_b = datetime(2026, 9, 29, 10, 0, 0)  # 24h later
        assert temporal_score(ts_a, ts_b) == 0.0

    def test_missing_timestamp(self):
        ts = datetime(2026, 9, 28, 10, 0, 0)
        assert temporal_score(None, ts) == 0.5
        assert temporal_score(ts, None) == 0.5
        assert temporal_score(None, None) == 0.5


class TestComputeAlignmentScore:
    def test_perfect_alignment(self):
        score = compute_alignment_score(1.0, 1.0, 1.0)
        assert score == 1.0

    def test_zero_alignment(self):
        score = compute_alignment_score(0.0, 0.0, 0.0)
        assert score == 0.0

    def test_mixed(self):
        score = compute_alignment_score(0.8, 0.6, 0.9)
        assert 0.5 < score < 1.0


class TestSpatialMatch:
    def test_same_location(self):
        loc = {"lat": 52.123, "lon": 5.123}
        assert spatial_match(loc, loc) is True

    def test_close_locations(self):
        loc_a = {"lat": 52.123, "lon": 5.123}
        loc_b = {"lat": 52.124, "lon": 5.124}
        assert spatial_match(loc_a, loc_b) is True

    def test_distant_locations(self):
        loc_a = {"lat": 52.123, "lon": 5.123}
        loc_b = {"lat": 48.856, "lon": 2.352}
        assert spatial_match(loc_a, loc_b) is False

    def test_custom_threshold(self):
        loc_a = {"lat": 52.123, "lon": 5.123}
        loc_b = {"lat": 52.133, "lon": 5.133}
        assert spatial_match(loc_a, loc_b, threshold_km=1.0) is False
        assert spatial_match(loc_a, loc_b, threshold_km=2.0) is True


class TestTemporalMatch:
    def test_same_time(self):
        ts = datetime(2026, 9, 28, 10, 0, 0)
        assert temporal_match(ts, ts) is True

    def test_within_threshold(self):
        ts_a = datetime(2026, 9, 28, 10, 0, 0)
        ts_b = datetime(2026, 9, 28, 11, 0, 0)
        assert temporal_match(ts_a, ts_b) is True

    def test_outside_threshold(self):
        ts_a = datetime(2026, 9, 28, 10, 0, 0)
        ts_b = datetime(2026, 9, 28, 14, 0, 0)
        assert temporal_match(ts_a, ts_b, threshold_hours=2.0) is False

    def test_none_timestamps(self):
        ts = datetime(2026, 9, 28, 10, 0, 0)
        assert temporal_match(None, ts) is True
        assert temporal_match(ts, None) is True


class TestComputeSourceQuality:
    def test_quality_extraction(self):
        assert compute_source_quality({"quality": 0.9}) == 0.9

    def test_default_quality(self):
        assert compute_source_quality({}) == 0.5

    def test_low_quality(self):
        assert compute_source_quality({"quality": 0.2}) == 0.2


class TestAlignEvidence:
    def test_align_all_sources(self):
        citizen = {
            "location": {"lat": 52.123, "lon": 5.123},
            "timestamp": datetime(2026, 9, 28, 10, 0, 0),
        }
        all_evidence = {
            "citizen": {},
            "sensor": {
                "location": {"lat": 52.123, "lon": 5.123},
                "timestamp": datetime(2026, 9, 28, 10, 5, 0),
                "quality": 0.9,
            },
            "satellite": {
                "location": {"lat": 52.124, "lon": 5.124},
                "timestamp": datetime(2026, 9, 28, 10, 0, 0),
                "quality": 0.7,
            },
        }
        results = align_evidence(citizen, all_evidence)
        assert len(results) == 2

        sources = {r["source"] for r in results}
        assert sources == {"sensor", "satellite"}

        for r in results:
            assert "spatial_match" in r
            assert "temporal_match" in r
            assert "source_quality" in r
            assert "alignment_score" in r
            assert 0.0 <= r["alignment_score"] <= 1.0

    def test_missing_location(self):
        citizen = {
            "location": {"lat": 52.123, "lon": 5.123},
            "timestamp": datetime(2026, 9, 28, 10, 0, 0),
        }
        all_evidence = {
            "citizen": {},
            "sensor": {
                "timestamp": datetime(2026, 9, 28, 10, 5, 0),
                "quality": 0.9,
            },
        }
        results = align_evidence(citizen, all_evidence)
        assert len(results) == 1
        assert results[0]["spatial_match"] == 0.5  # neutral

    def test_missing_timestamp(self):
        citizen = {
            "location": {"lat": 52.123, "lon": 5.123},
            "timestamp": datetime(2026, 9, 28, 10, 0, 0),
        }
        all_evidence = {
            "citizen": {},
            "sensor": {
                "location": {"lat": 52.123, "lon": 5.123},
                "quality": 0.9,
            },
        }
        results = align_evidence(citizen, all_evidence)
        assert len(results) == 1
        assert results[0]["temporal_match"] == 0.5  # neutral

    def test_low_quality_source(self):
        citizen = {
            "location": {"lat": 52.123, "lon": 5.123},
            "timestamp": datetime(2026, 9, 28, 10, 0, 0),
        }
        all_evidence = {
            "citizen": {},
            "sensor": {
                "location": {"lat": 52.123, "lon": 5.123},
                "timestamp": datetime(2026, 9, 28, 10, 0, 0),
                "quality": 0.2,
            },
        }
        results = align_evidence(citizen, all_evidence)
        assert len(results) == 1
        assert results[0]["source_quality"] == 0.2
        # alignment_score = 0.35*1.0 + 0.25*1.0 + 0.40*0.2 = 0.68
        assert results[0]["alignment_score"] == 0.68
