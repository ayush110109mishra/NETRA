"""
Test suite for NETRA Phase 4 Kinematic Anomaly Detector.
Verifies velocity envelope checks, speed spikes vs baseline, ground speed limits,
and implied velocities between successive coordinates.
"""

from datetime import datetime, timezone, timedelta
import pytest
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from anomaly.kinematic import KinematicAnomalyDetector


@pytest.fixture
def ground_entity():
    return CanonicalEntity(
        entity_id="ENT-KINE-GROUND",
        entity_type="VEHICLE",
        first_observed=datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc),
        last_observed=datetime(2026, 9, 10, 15, 0, 0, tzinfo=timezone.utc),
        observation_count=20,
    )


@pytest.fixture
def base_profile():
    return EntityBehaviorProfile(
        baseline_status="SUFFICIENT_HISTORY",
        sample_count=20,
        event_frequency_per_day=3.0,
        average_activity=0.30,
        average_speed=38.0,
    )


def test_kinematic_normal_speed(ground_entity, base_profile):
    events = [
        CanonicalEvent(
            event_id="EVT-K-NORM",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[ground_entity.entity_id],
            attributes={"speed": 42.0},
        )
    ]
    res = KinematicAnomalyDetector.detect(ground_entity, events, base_profile)
    assert res.score == 0.0
    assert len(res.indicators) == 0


def test_kinematic_ground_speed_excess(ground_entity, base_profile):
    events = [
        CanonicalEvent(
            event_id="EVT-K-OVERSPEED",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[ground_entity.entity_id],
            attributes={"speed": 145.0},
        )
    ]
    res = KinematicAnomalyDetector.detect(ground_entity, events, base_profile)
    assert res.score >= 0.70
    assert "GROUND_SPEED_EXCESS" in res.indicators
    assert "EVT-K-OVERSPEED" in res.evidence_event_ids


def test_kinematic_speed_spike_vs_baseline(ground_entity, base_profile):
    # Baseline is 38 km/h. Speed 100 km/h (> 2.5x baseline)
    events = [
        CanonicalEvent(
            event_id="EVT-K-SPIKE",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[ground_entity.entity_id],
            attributes={"speed": 105.0},
        )
    ]
    res = KinematicAnomalyDetector.detect(ground_entity, events, base_profile)
    assert res.score >= 0.50
    assert "KINEMATIC_SPEED_SPIKE" in res.indicators


def test_kinematic_consecutive_implied_overspeed(ground_entity, base_profile):
    t0 = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)
    # 25 km covered in 10 minutes (implied speed 150 km/h)
    events = [
        CanonicalEvent(
            event_id="EVT-IMP-1",
            event_type="movement",
            timestamp=t0,
            location=Coordinates(latitude=26.8500, longitude=80.9500),
            entity_ids=[ground_entity.entity_id],
        ),
        CanonicalEvent(
            event_id="EVT-IMP-2",
            event_type="movement",
            timestamp=t0 + timedelta(minutes=10),
            location=Coordinates(latitude=27.0750, longitude=80.9500),
            entity_ids=[ground_entity.entity_id],
        ),
    ]
    res = KinematicAnomalyDetector.detect(ground_entity, events, base_profile)
    assert res.score >= 0.80
    assert "IMPLIED_GROUND_OVERSPEED" in res.indicators
