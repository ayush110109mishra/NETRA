"""
Test suite for NETRA Phase 4 Confidence Calibration Engine.
Verifies decoupling from anomaly magnitude, multi-sensor bonus, contradiction penalties,
and strict cold-start gating (fewer than 3 observations MUST NOT receive confidence > 0.35).
"""

from datetime import datetime, timezone, timedelta
import pytest
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent, EventSource
from models.entity_intelligence import CanonicalEntity
from models.anomaly_intelligence import AnomalyConfirmationLevel
from anomaly.calibration import ConfidenceCalibrator


def test_confidence_cold_start_gate():
    # Only 2 observations -> Confidence MUST NOT exceed 0.35
    entity = CanonicalEntity(
        entity_id="ENT-COLD-START",
        entity_type="VEHICLE",
        first_observed=datetime.now(timezone.utc),
        last_observed=datetime.now(timezone.utc),
        observation_count=2,
    )
    events = [
        CanonicalEvent(
            event_id="EVT-CS-1",
            event_type="movement",
            timestamp=datetime.now(timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
            source=EventSource(source_id="S1", reliability=0.99),
        ),
        CanonicalEvent(
            event_id="EVT-CS-2",
            event_type="movement",
            timestamp=datetime.now(timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
            source=EventSource(source_id="S2", reliability=0.99),
        ),
    ]
    cal_conf, level, audit = ConfidenceCalibrator.calibrate(entity, events)
    assert cal_conf <= 0.35
    assert audit["cold_start_applied"] is True
    assert level == AnomalyConfirmationLevel.UNCONFIRMED


def test_confidence_sensor_diversity_bonus():
    # 5 observations from 3 distinct sensors
    entity = CanonicalEntity(
        entity_id="ENT-MULTI-SENSOR",
        entity_type="VEHICLE",
        first_observed=datetime.now(timezone.utc),
        last_observed=datetime.now(timezone.utc),
        observation_count=10,
    )
    sensors = ["RADAR", "OPTICAL", "SIGINT"]
    events = [
        CanonicalEvent(
            event_id=f"EVT-MS-{i}",
            event_type="movement",
            timestamp=datetime.now(timezone.utc) + timedelta(minutes=i),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
            source=EventSource(source_id=f"SRC-{i}", source_type=sensors[i % 3], reliability=0.90),
        )
        for i in range(5)
    ]
    cal_conf, level, audit = ConfidenceCalibrator.calibrate(entity, events)
    assert cal_conf >= 0.75
    assert audit["distinct_sensor_count"] == 3
    assert level in [AnomalyConfirmationLevel.CORROBORATED, AnomalyConfirmationLevel.STRONGLY_CORROBORATED]


def test_confidence_contradiction_penalty():
    entity = CanonicalEntity(
        entity_id="ENT-CONFLICT",
        entity_type="VEHICLE",
        first_observed=datetime.now(timezone.utc),
        last_observed=datetime.now(timezone.utc),
        observation_count=10,
    )
    t0 = datetime.now(timezone.utc)
    # One sensor reports 150 km/h, another reports 10 km/h within 30s
    events = [
        CanonicalEvent(
            event_id="EVT-C1",
            event_type="movement",
            timestamp=t0,
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
            attributes={"speed": 150.0},
            source=EventSource(source_id="S1", source_type="RADAR", reliability=0.85),
        ),
        CanonicalEvent(
            event_id="EVT-C2",
            event_type="movement",
            timestamp=t0 + timedelta(seconds=20),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
            attributes={"speed": 10.0},
            source=EventSource(source_id="S2", source_type="OPTICAL", reliability=0.85),
        ),
        CanonicalEvent(
            event_id="EVT-C3",
            event_type="movement",
            timestamp=t0 + timedelta(minutes=2),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
            attributes={"speed": 10.0},
            source=EventSource(source_id="S3", source_type="OPTICAL", reliability=0.85),
        ),
    ]
    cal_conf, level, audit = ConfidenceCalibrator.calibrate(entity, events)
    assert audit["has_contradiction"] is True
    # Penalty of 0.35 heavily reduces confidence
    assert cal_conf < 0.60
