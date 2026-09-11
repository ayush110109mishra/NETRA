"""
Test suite for NETRA Phase 4 Temporal Anomaly Detector.
Verifies hour-of-day deviations, temporal bursts, off-schedule operational windows,
and evidence event linkage.
"""

from datetime import datetime, timezone, timedelta
import pytest
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent, EventSource
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile, EntityTemporalBehavior
from anomaly.temporal import TemporalAnomalyDetector


@pytest.fixture
def base_entity():
    return CanonicalEntity(
        entity_id="ENT-TEMP-TEST",
        entity_type="VEHICLE",
        first_observed=datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc),
        last_observed=datetime(2026, 9, 10, 15, 0, 0, tzinfo=timezone.utc),
        observation_count=20,
    )


@pytest.fixture
def daytime_baseline():
    # Historical distribution strictly daytime (10:00 - 15:00)
    hourly_dist = {10: 5, 11: 8, 12: 10, 13: 8, 14: 6, 15: 4}
    return EntityBehaviorProfile(
        baseline_status="SUFFICIENT_HISTORY",
        sample_count=41,
        event_frequency_per_day=4.0,
        average_activity=0.35,
        average_speed=40.0,
        temporal=EntityTemporalBehavior(
            peak_activity_hour=12,
            average_inter_event_minutes=60.0,
            hourly_distribution=hourly_dist,
        ),
    )


def test_temporal_normal_operations(base_entity, daytime_baseline):
    # Events during normal daytime hours
    events = [
        CanonicalEvent(
            event_id=f"EVT-T-NORM-{i}",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 11, i * 10, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[base_entity.entity_id],
        )
        for i in range(3)
    ]
    res = TemporalAnomalyDetector.detect(base_entity, events, daytime_baseline)
    assert res.dimension == "temporal"
    assert res.score == 0.0
    assert len(res.indicators) == 0


def test_temporal_unexpected_night_hours(base_entity, daytime_baseline):
    # Events at 02:00 AM where baseline has 0 probability
    events = [
        CanonicalEvent(
            event_id=f"EVT-T-NIGHT-{i}",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 2, i * 15, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[base_entity.entity_id],
        )
        for i in range(2)
    ]
    res = TemporalAnomalyDetector.detect(base_entity, events, daytime_baseline)
    assert res.dimension == "temporal"
    assert res.score >= 0.50
    assert "UNEXPECTED_OPERATIONAL_HOURS" in res.indicators
    assert "EVT-T-NIGHT-0" in res.evidence_event_ids


def test_temporal_burst_detection(base_entity, daytime_baseline):
    # 4 events within 3 minutes (180s)
    base_ts = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)
    events = [
        CanonicalEvent(
            event_id=f"EVT-T-BURST-{i}",
            event_type="movement",
            timestamp=base_ts + timedelta(seconds=i * 30),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[base_entity.entity_id],
        )
        for i in range(4)
    ]
    res = TemporalAnomalyDetector.detect(base_entity, events, daytime_baseline)
    assert res.score >= 0.70
    assert "TEMPORAL_BURST" in res.indicators
    assert len(res.evidence_event_ids) == 4


def test_temporal_empty_events_and_cold_start(base_entity):
    res_empty = TemporalAnomalyDetector.detect(base_entity, [])
    assert res_empty.score == 0.0
    assert res_empty.indicators == []

    # Single event without baseline
    events = [
        CanonicalEvent(
            event_id="EVT-T-COLD",
            event_type="movement",
            timestamp=datetime.now(timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[base_entity.entity_id],
        )
    ]
    res_cold = TemporalAnomalyDetector.detect(base_entity, events, None)
    assert res_cold.score == 0.0
    assert res_cold.confidence <= 0.60
