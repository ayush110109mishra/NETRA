"""
Tests for Behavioral Change Detection in NETRA Entity Intelligence.
"""

from datetime import datetime, timezone, timedelta
from models.common import Coordinates, EntityStatus
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity
from entities.baseline import BehavioralBaselineEngine
from entities.change_detection import BehavioralChangeDetector

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)


def test_no_changes_on_cold_start():
    baseline_engine = BehavioralBaselineEngine()
    detector = BehavioralChangeDetector()

    entity = CanonicalEntity(
        entity_id="ENTITY-COLD",
        entity_type="VEHICLE",
        first_observed=BASE_TIME,
        last_observed=BASE_TIME,
    )
    events = [
        CanonicalEvent(
            event_id="EVT-1",
            event_type="movement",
            timestamp=BASE_TIME,
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENTITY-COLD"],
            attributes={"speed": 120.0},
        )
    ]
    baseline = baseline_engine.compute_baseline(entity, events)
    report = detector.detect_changes(entity, baseline, events)

    assert not report.detected
    assert report.score == 0.0
    assert len(report.changes) == 0


def test_detect_speed_surge():
    baseline_engine = BehavioralBaselineEngine()
    detector = BehavioralChangeDetector()

    entity = CanonicalEntity(
        entity_id="ENTITY-SPEED",
        entity_type="VEHICLE",
        first_observed=BASE_TIME - timedelta(hours=48),
        last_observed=BASE_TIME,
    )
    # 4 baseline events with speed ~30 km/h
    events = [
        CanonicalEvent(
            event_id=f"EVT-BASE-{i}",
            event_type="movement",
            timestamp=BASE_TIME - timedelta(hours=48 - i * 10),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENTITY-SPEED"],
            attributes={"speed": 30.0},
        )
        for i in range(4)
    ]
    baseline = baseline_engine.compute_baseline(entity, events)

    # Add recent event with speed 95 km/h
    events.append(
        CanonicalEvent(
            event_id="EVT-FAST",
            event_type="movement",
            timestamp=BASE_TIME,
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENTITY-SPEED"],
            attributes={"speed": 95.0},
        )
    )

    report = detector.detect_changes(entity, baseline, events)

    assert report.detected
    assert report.score > 0.0
    speed_changes = [c for c in report.changes if c.feature == "speed"]
    assert len(speed_changes) == 1
    assert speed_changes[0].direction == "INCREASE"
    assert "EVT-FAST" in speed_changes[0].evidence_event_ids


def test_detect_spatial_expansion():
    baseline_engine = BehavioralBaselineEngine()
    detector = BehavioralChangeDetector()

    entity = CanonicalEntity(
        entity_id="ENTITY-EXPAND",
        entity_type="VEHICLE",
        first_observed=BASE_TIME - timedelta(hours=48),
        last_observed=BASE_TIME,
    )
    # Baseline events clustered within 2km
    events = [
        CanonicalEvent(
            event_id=f"EVT-BASE-{i}",
            event_type="movement",
            timestamp=BASE_TIME - timedelta(hours=48 - i * 10),
            location=Coordinates(latitude=26.85 + i * 0.001, longitude=80.95),
            entity_ids=["ENTITY-EXPAND"],
            attributes={"speed": 30.0},
        )
        for i in range(4)
    ]
    baseline = baseline_engine.compute_baseline(entity, events)

    # Recent event 50km away
    events.append(
        CanonicalEvent(
            event_id="EVT-DISTANT",
            event_type="movement",
            timestamp=BASE_TIME,
            location=Coordinates(latitude=27.35, longitude=81.45),
            entity_ids=["ENTITY-EXPAND"],
            attributes={"speed": 30.0},
        )
    )

    report = detector.detect_changes(entity, baseline, events)

    assert report.detected
    spatial_changes = [c for c in report.changes if c.feature == "spatial_expansion"]
    assert len(spatial_changes) == 1
    assert "EVT-DISTANT" in spatial_changes[0].evidence_event_ids


def test_detect_novel_event_type():
    baseline_engine = BehavioralBaselineEngine()
    detector = BehavioralChangeDetector()

    entity = CanonicalEntity(
        entity_id="ENTITY-TYPE",
        entity_type="AIRCRAFT",
        first_observed=BASE_TIME - timedelta(hours=48),
        last_observed=BASE_TIME,
    )
    # Baseline all movement
    events = [
        CanonicalEvent(
            event_id=f"EVT-BASE-{i}",
            event_type="movement",
            timestamp=BASE_TIME - timedelta(hours=48 - i * 10),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENTITY-TYPE"],
            attributes={"speed": 300.0},
        )
        for i in range(4)
    ]
    baseline = baseline_engine.compute_baseline(entity, events)

    # Add recent electronic_emission event
    events.append(
        CanonicalEvent(
            event_id="EVT-EW",
            event_type="electronic_emission",
            timestamp=BASE_TIME,
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENTITY-TYPE"],
            attributes={"speed": 300.0},
        )
    )

    report = detector.detect_changes(entity, baseline, events)

    assert report.detected
    type_changes = [c for c in report.changes if c.feature == "event_type"]
    assert len(type_changes) == 1
    assert type_changes[0].direction == "NEW"
    assert "EVT-EW" in type_changes[0].evidence_event_ids
