"""
Tests for Entity Anomaly Engine in NETRA.
"""

from datetime import datetime, timezone, timedelta
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import (
    CanonicalEntity,
    BehavioralChangeItem,
    BehavioralChangeReport,
)
from entities.baseline import BehavioralBaselineEngine
from entities.anomaly import EntityAnomalyEngine

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)


def test_anomaly_low_on_nominal_behavior():
    baseline_engine = BehavioralBaselineEngine()
    entity = CanonicalEntity(
        entity_id="ENTITY-NOMINAL",
        entity_type="VEHICLE",
        first_observed=BASE_TIME - timedelta(hours=24),
        last_observed=BASE_TIME,
    )
    events = [
        CanonicalEvent(
            event_id=f"EVT-{i}",
            event_type="movement",
            timestamp=BASE_TIME - timedelta(hours=24 - i * 8),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENTITY-NOMINAL"],
            attributes={"speed": 40.0, "activity_level": 0.25},
        )
        for i in range(4)
    ]
    baseline = baseline_engine.compute_baseline(entity, events)
    changes = BehavioralChangeReport(detected=False, score=0.0, changes=[])
    
    anomaly = EntityAnomalyEngine.assess_anomaly(entity, baseline, changes, events[-1:])

    assert anomaly.score <= 0.15
    assert anomaly.level == "LOW"
    assert len(anomaly.indicators) == 0


def test_anomaly_critical_on_multiple_indicators():
    baseline_engine = BehavioralBaselineEngine()
    entity = CanonicalEntity(
        entity_id="ENTITY-CRIT",
        entity_type="VEHICLE",
        first_observed=BASE_TIME - timedelta(hours=48),
        last_observed=BASE_TIME,
    )
    events = [
        CanonicalEvent(
            event_id="EVT-DEV",
            event_type="patrol_deviation",
            timestamp=BASE_TIME,
            location=Coordinates(latitude=26.95, longitude=81.05),
            entity_ids=["ENTITY-CRIT"],
            attributes={"speed": 125.0, "activity_level": 0.95},
        )
    ]
    baseline = baseline_engine.compute_baseline(entity, events)

    changes = BehavioralChangeReport(
        detected=True,
        score=0.90,
        changes=[
            BehavioralChangeItem(
                feature="speed",
                direction="INCREASE",
                magnitude=2.5,
                description="Speed increased by 250%",
                evidence_event_ids=["EVT-DEV"],
            ),
            BehavioralChangeItem(
                feature="spatial_expansion",
                direction="INCREASE",
                magnitude=2.0,
                description="Expanded 200%",
                evidence_event_ids=["EVT-DEV"],
            ),
        ],
    )

    anomaly = EntityAnomalyEngine.assess_anomaly(entity, baseline, changes, events)

    assert anomaly.score >= 0.80
    assert anomaly.level == "CRITICAL"
    indicator_names = [ind.indicator for ind in anomaly.indicators]
    assert "SPEED_SURGE" in indicator_names
    assert "SPATIAL_EXPANSION" in indicator_names
    assert "GROUND_SPEED_EXCESS" in indicator_names
