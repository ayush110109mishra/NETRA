"""
Unit tests for NETRA Phase 6 Temporal State Sequence Representation.
Tests chronological ordering, irregular observation handling, categorical state mapping,
and sampling regularity calculation.
"""

from datetime import datetime, timezone, timedelta
import pytest

from models.common import Coordinates, EventSource
from models.event_intelligence import CanonicalEvent
from prediction.temporal_state import TemporalStateManager


def test_empty_events_sequence():
    seq = TemporalStateManager.build_sequence(entity_id="ENT-EMPTY", events=[])
    assert seq.entity_id == "ENT-EMPTY"
    assert seq.sample_count == 0
    assert seq.sampling_regularity == 1.0
    assert seq.points == []


def test_regular_interval_sequence():
    t0 = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        CanonicalEvent(
            event_id=f"EVT-REG-{i}",
            event_type="ROUTINE_PING",
            timestamp=t0 + timedelta(minutes=i * 10),
            location=Coordinates(latitude=34.0, longitude=74.5),
            entity_ids=["ENT-REG"],
            attributes={"activity_level": 0.50},
            source=EventSource(source_id="S1", source_type="RADAR", reliability=0.9),
        )
        for i in range(5)
    ]
    seq = TemporalStateManager.build_sequence(entity_id="ENT-REG", events=events, metric_key="activity_level")
    assert seq.sample_count == 5
    assert len(seq.points) == 5
    # For perfectly regular intervals, standard deviation is 0.0 -> regularity = 1.0
    assert seq.sampling_regularity == 1.0
    for pt in seq.points:
        assert pt.state == "NOMINAL"


def test_irregular_interval_sequence():
    t0 = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)
    # Deliberately irregular intervals: 2m, 20m, 5m, 60m
    offsets = [0, 2, 22, 27, 87]
    events = [
        CanonicalEvent(
            event_id=f"EVT-IRR-{i}",
            event_type="IRREGULAR_PING",
            timestamp=t0 + timedelta(minutes=offsets[i]),
            location=Coordinates(latitude=34.0, longitude=74.5),
            entity_ids=["ENT-IRR"],
            attributes={"activity_level": 0.20 if i == 0 else 0.88},
            source=EventSource(source_id="S1", source_type="RADAR", reliability=0.9),
        )
        for i in range(len(offsets))
    ]
    seq = TemporalStateManager.build_sequence(entity_id="ENT-IRR", events=events, metric_key="activity_level")
    assert seq.sample_count == 5
    assert seq.sampling_regularity < 0.95
    assert seq.points[0].state == "LOW"
    assert seq.points[1].state == "CRITICAL"

