"""
Tests for Entity Confidence Engine in NETRA.
"""

from datetime import datetime, timezone, timedelta
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent, EventSource
from models.entity_intelligence import CanonicalEntity
from entities.baseline import BehavioralBaselineEngine
from entities.confidence import EntityConfidenceEngine
from config import NetraConfig, EntityConfidenceWeights

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)


def test_confidence_weights_validation():
    weights = EntityConfidenceWeights(
        observation_depth=0.35,
        time_span_depth=0.25,
        completeness=0.25,
        source_reliability=0.15,
    )
    weights.validate()


def test_confidence_cold_start_cap():
    cfg = NetraConfig()
    engine = EntityConfidenceEngine(cfg)
    baseline_engine = BehavioralBaselineEngine(cfg.entity)

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
            attributes={"speed": 40.0, "activity_level": 0.30, "heading_deg": 90.0},
            source=EventSource(source_id="S1", reliability_score=0.99),
        )
    ]
    baseline = baseline_engine.compute_baseline(entity, events)
    conf = engine.compute_confidence(entity, events, baseline)

    # Must be strictly capped at 0.35
    assert conf.score <= 0.35
    assert conf.level == "LOW"
    assert any(f.factor == "COLD_START_RESTRICTION" for f in conf.factors)


def test_confidence_contradiction_penalties():
    cfg = NetraConfig()
    engine = EntityConfidenceEngine(cfg)
    baseline_engine = BehavioralBaselineEngine(cfg.entity)

    entity = CanonicalEntity(
        entity_id="ENTITY-CONFLICT",
        entity_type="VEHICLE",
        first_observed=BASE_TIME - timedelta(hours=48),
        last_observed=BASE_TIME,
    )
    # 4 baseline events + 2 conflicting events within 30s
    events = [
        CanonicalEvent(
            event_id=f"EVT-BASE-{i}",
            event_type="movement",
            timestamp=BASE_TIME - timedelta(hours=48 - i * 10),
            location=Coordinates(latitude=26.85 + i * 0.002, longitude=80.95),
            entity_ids=["ENTITY-CONFLICT"],
            attributes={"speed": 40.0, "activity_level": 0.30, "heading_deg": 90.0},
            source=EventSource(source_id="S1", reliability_score=0.90),
        )
        for i in range(4)
    ]
    # Add two events 30s apart, 20 km away
    events.extend([
        CanonicalEvent(
            event_id="EVT-CONF-1",
            event_type="movement",
            timestamp=BASE_TIME,
            location=Coordinates(latitude=26.8500, longitude=80.9500),
            entity_ids=["ENTITY-CONFLICT"],
            attributes={"speed": 35.0, "activity_level": 0.30, "heading_deg": 90.0},
            source=EventSource(source_id="RADAR-NORTH", reliability_score=0.90),
        ),
        CanonicalEvent(
            event_id="EVT-CONF-2",
            event_type="movement",
            timestamp=BASE_TIME + timedelta(seconds=30),
            location=Coordinates(latitude=27.1500, longitude=81.2500),  # > 30 km in 30s
            entity_ids=["ENTITY-CONFLICT"],
            attributes={"speed": 135.0, "activity_level": 0.85, "heading_deg": 270.0},
            source=EventSource(source_id="OPTICAL-SOUTH", reliability_score=0.80),
        ),
    ])

    baseline = baseline_engine.compute_baseline(entity, events)
    conf = engine.compute_confidence(entity, events, baseline)

    assert len(conf.contradictions) > 0
    assert any(c.feature in ["location", "speed"] for c in conf.contradictions)
