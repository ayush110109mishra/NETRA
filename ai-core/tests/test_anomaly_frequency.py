"""
Test suite for NETRA Phase 4 Frequency Anomaly Detector.
Verifies event density surges, high-density bursts, cadence increases,
and activity drop detection.
"""

from datetime import datetime, timezone, timedelta
import pytest
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from anomaly.frequency import FrequencyAnomalyDetector


@pytest.fixture
def test_entity():
    return CanonicalEntity(
        entity_id="ENT-FREQ-TEST",
        entity_type="PATROL_UNIT",
        first_observed=datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc),
        last_observed=datetime(2026, 9, 10, 15, 0, 0, tzinfo=timezone.utc),
        observation_count=20,
    )


@pytest.fixture
def low_rate_baseline():
    return EntityBehaviorProfile(
        baseline_status="SUFFICIENT_HISTORY",
        sample_count=20,
        event_frequency_per_day=2.0,
        average_activity=0.30,
        average_speed=30.0,
    )


def test_frequency_normal_cadence(test_entity, low_rate_baseline):
    # 2 events separated by 12 hours (rate = 2/day, matches baseline)
    t0 = datetime(2026, 9, 11, 6, 0, 0, tzinfo=timezone.utc)
    events = [
        CanonicalEvent(
            event_id="EVT-F-1",
            event_type="patrol",
            timestamp=t0,
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[test_entity.entity_id],
        ),
        CanonicalEvent(
            event_id="EVT-F-2",
            event_type="patrol",
            timestamp=t0 + timedelta(hours=12),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[test_entity.entity_id],
        ),
    ]
    res = FrequencyAnomalyDetector.detect(test_entity, events, low_rate_baseline)
    assert res.score == 0.0


def test_frequency_surge(test_entity, low_rate_baseline):
    # 6 events within 15 minutes
    t0 = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)
    events = [
        CanonicalEvent(
            event_id=f"EVT-SURGE-{i}",
            event_type="patrol",
            timestamp=t0 + timedelta(minutes=i * 2),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[test_entity.entity_id],
        )
        for i in range(6)
    ]
    res = FrequencyAnomalyDetector.detect(test_entity, events, low_rate_baseline)
    assert res.score >= 0.80
    assert "FREQUENCY_SURGE" in res.indicators or "HIGH_DENSITY_BURST" in res.indicators
    assert len(res.evidence_event_ids) == 6


def test_frequency_activity_collapse(test_entity):
    high_baseline = EntityBehaviorProfile(
        baseline_status="SUFFICIENT_HISTORY",
        sample_count=100,
        event_frequency_per_day=30.0,
        average_activity=0.80,
        average_speed=40.0,
    )
    # Only 1 single event when 30/day was expected
    events = [
        CanonicalEvent(
            event_id="EVT-SOLO",
            event_type="patrol",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[test_entity.entity_id],
        )
    ]
    res = FrequencyAnomalyDetector.detect(test_entity, events, high_baseline)
    assert "ABNORMAL_ACTIVITY_DROP" in res.indicators
    assert res.score >= 0.35
