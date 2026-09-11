"""
Tests for Phase 3 Behavioral Baseline Engine.
"""

from datetime import datetime, timezone, timedelta
from models.common import Coordinates, EntityStatus, Allegiance
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity
from entities.baseline import BehavioralBaselineEngine

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)


def test_baseline_cold_start_under_three_events():
    engine = BehavioralBaselineEngine()
    entity = CanonicalEntity(
        entity_id="ENTITY-COLD",
        entity_type="VEHICLE",
        first_observed=BASE_TIME,
        last_observed=BASE_TIME,
        observation_count=2,
        event_count=2,
    )
    events = [
        CanonicalEvent(
            event_id="EVT-1",
            event_type="movement",
            timestamp=BASE_TIME,
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENTITY-COLD"],
            attributes={"speed": 35.0, "activity_level": 0.3},
        ),
        CanonicalEvent(
            event_id="EVT-2",
            event_type="movement",
            timestamp=BASE_TIME + timedelta(hours=1),
            location=Coordinates(latitude=26.86, longitude=80.96),
            entity_ids=["ENTITY-COLD"],
            attributes={"speed": 45.0, "activity_level": 0.4},
        ),
    ]

    baseline = engine.compute_baseline(entity, events)

    assert baseline.baseline_status == "INSUFFICIENT_HISTORY"
    assert baseline.sample_count == 2
    assert baseline.average_speed == 40.0
    assert baseline.average_activity == 0.35


def test_baseline_sufficient_history():
    engine = BehavioralBaselineEngine()
    entity = CanonicalEntity(
        entity_id="ENTITY-NORM",
        entity_type="VEHICLE",
        first_observed=BASE_TIME - timedelta(hours=48),
        last_observed=BASE_TIME,
        observation_count=5,
        event_count=5,
    )
    events = [
        CanonicalEvent(
            event_id=f"EVT-{i}",
            event_type="movement" if i < 4 else "patrol",
            timestamp=BASE_TIME - timedelta(hours=48 - i * 12),
            location=Coordinates(latitude=26.85 + i * 0.005, longitude=80.95),
            entity_ids=["ENTITY-NORM"],
            attributes={"speed": 30.0 + i * 5, "activity_level": 0.2 + i * 0.05},
        )
        for i in range(5)
    ]

    baseline = engine.compute_baseline(entity, events)

    assert baseline.baseline_status == "SUFFICIENT_HISTORY"
    assert baseline.sample_count == 5
    assert baseline.average_speed == 40.0
    assert baseline.average_activity == 0.30
    assert baseline.event_frequency_per_day > 0.0
    assert "movement" in baseline.event_type_distribution
    assert baseline.event_type_distribution["movement"] == 0.8
    assert baseline.event_type_distribution["patrol"] == 0.2
