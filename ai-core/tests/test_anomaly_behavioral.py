"""
Test suite for NETRA Phase 4 Behavioral Anomaly Detector.
Verifies activity profile drift, peak activity excursions (>= 0.85),
and posture escalation detection.
"""

from datetime import datetime, timezone
import pytest
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from anomaly.behavioral import BehavioralAnomalyDetector


@pytest.fixture
def entity():
    return CanonicalEntity(
        entity_id="ENT-BEH-TEST",
        entity_type="VEHICLE",
        first_observed=datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc),
        last_observed=datetime(2026, 9, 10, 15, 0, 0, tzinfo=timezone.utc),
        observation_count=20,
    )


@pytest.fixture
def baseline():
    return EntityBehaviorProfile(
        baseline_status="SUFFICIENT_HISTORY",
        sample_count=20,
        event_frequency_per_day=3.0,
        average_activity=0.25,
        average_speed=35.0,
    )


def test_behavioral_normal_activity(entity, baseline):
    events = [
        CanonicalEvent(
            event_id="EVT-B-NORM",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
            attributes={"activity_level": 0.28},
        )
    ]
    res = BehavioralAnomalyDetector.detect(entity, events, baseline)
    assert res.score == 0.0


def test_behavioral_peak_activity_excursion(entity, baseline):
    events = [
        CanonicalEvent(
            event_id="EVT-B-PEAK",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
            attributes={"activity_level": 0.92},
        )
    ]
    res = BehavioralAnomalyDetector.detect(entity, events, baseline)
    assert res.score >= 0.85
    assert "PEAK_ACTIVITY_EXCURSION" in res.indicators
    assert "EVT-B-PEAK" in res.evidence_event_ids


def test_behavioral_posture_escalation(entity, baseline):
    events = [
        CanonicalEvent(
            event_id="EVT-B-ALERT",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
            attributes={"operational_status": "COMBAT_READY"},
        )
    ]
    res = BehavioralAnomalyDetector.detect(entity, events, baseline)
    assert res.score >= 0.80
    assert "POSTURE_ESCALATION_COMBAT_READY" in res.indicators
