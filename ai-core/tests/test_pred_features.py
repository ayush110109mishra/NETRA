"""
Unit tests for NETRA Phase 6 Feature Engineering.
Validates multi-dimensional feature extraction across temporal, kinematic, spatial,
behavioral, Phase 4 anomaly/risk, and Phase 5 fusion feeds with full lineage provenance.
"""

from datetime import datetime, timezone, timedelta
import pytest

from models.common import Coordinates, EventSource
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityProfile
from prediction.feature_engineering import FeatureExtractor


@pytest.fixture
def sample_events():
    t0 = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)
    events = []
    for i in range(6):
        events.append(
            CanonicalEvent(
                event_id=f"EVT-FT-{i}",
                event_type="SURVEILLANCE_SWEEP",
                timestamp=t0 + timedelta(minutes=i * 15),
                location=Coordinates(latitude=34.0 + i * 0.01, longitude=74.5 + i * 0.01),
                entity_ids=["ENT-01"],
                attributes={
                    "speed": 30.0 + i * 5.0,
                    "heading_deg": 90.0,
                    "activity_level": 0.40 + i * 0.05,
                    "anomaly_score": 0.20 + i * 0.05,
                },
                source=EventSource(
                    source_id=f"RADAR_{i % 2 + 1}",
                    source_type="RADAR",
                    reliability=0.90,
                ),
            )
        )
    return events


def test_feature_extraction_empty_events():
    features = FeatureExtractor.extract_features(events=[])
    assert features == []


def test_feature_extraction_temporal_and_kinematic(sample_events):
    features = FeatureExtractor.extract_features(events=sample_events)
    assert len(features) > 0

    feat_names = {f.feature_name for f in features}
    assert "temporal_event_frequency" in feat_names
    assert "temporal_inter_event_interval_mean" in feat_names
    assert "kinematic_mean_speed" in feat_names
    assert "kinematic_speed_trend_delta" in feat_names
    assert "spatial_centroid_displacement" in feat_names
    assert "behavioral_activity_level_current" in feat_names


    # Check provenance
    for f in features:
        assert isinstance(f.derived_from, list)
        assert len(f.derived_from) > 0
        assert 0.0 <= f.normalized_value <= 1.0


def test_feature_extraction_with_anomaly_and_fusion(sample_events):
    class DummyFusedObs:
        def __init__(self):
            self.fusion_confidence = 0.88
            self.agreement_score = 0.92
            self.independent_source_count = 3

    fused_obs = [DummyFusedObs(), DummyFusedObs()]
    anomaly_assessment = {
        "anomaly_score": 0.72,
        "risk_score": 0.65,
        "persistence_factor": 0.85,
    }

    features = FeatureExtractor.extract_features(
        events=sample_events,
        anomaly_assessment=anomaly_assessment,
        fused_observations=fused_obs,
    )
    feat_dict = {f.feature_name: f for f in features}

    assert "anomaly_overall_score" in feat_dict
    assert feat_dict["anomaly_overall_score"].value == 0.72
    assert "anomaly_risk_score" in feat_dict
    assert feat_dict["anomaly_risk_score"].value == 0.65
    assert "fusion_mean_confidence" in feat_dict
    assert feat_dict["fusion_mean_confidence"].value == 0.88
    assert "fusion_independent_sources" in feat_dict
    assert feat_dict["fusion_independent_sources"].value == 3
