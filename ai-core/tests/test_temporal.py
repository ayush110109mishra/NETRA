"""
Unit tests for Temporal Intelligence Engine.
Tests proximity decay, sequential relationships, temporal bursts, and periodic recurrence.
"""

from datetime import datetime, timezone, timedelta
import pytest

from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from events.temporal import TemporalIntelligence

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)
LOC = Coordinates(latitude=26.84, longitude=80.94)


def test_temporal_proximity_within_window():
    """Verify temporal score decays gracefully as time difference increases."""
    temporal = TemporalIntelligence()
    t1 = BASE_TIME
    t2 = BASE_TIME + timedelta(minutes=15)

    delta, score, conf = temporal.calculate_temporal_score(t1, t2, window_seconds=7200.0)
    assert delta == 900.0
    assert 0.85 <= score <= 0.90
    assert conf >= 0.90


def test_temporal_proximity_outside_window():
    """Verify events separated by more than proximity window receive score 0.0."""
    temporal = TemporalIntelligence()
    t1 = BASE_TIME
    t2 = BASE_TIME + timedelta(hours=3)  # 3 hours > 2 hours window

    delta, score, conf = temporal.calculate_temporal_score(t1, t2, window_seconds=7200.0)
    assert delta == 10800.0
    assert score == 0.0
    assert conf == 0.0


def test_sequential_relationship():
    """Verify sequential detection for same entity within sequence window."""
    temporal = TemporalIntelligence()
    e1 = CanonicalEvent(
        event_id="E1", event_type="MOVEMENT", timestamp=BASE_TIME,
        location=LOC, entity_ids=["ENTITY-1"]
    )
    e2 = CanonicalEvent(
        event_id="E2", event_type="PATROL_DEVIATION", timestamp=BASE_TIME + timedelta(minutes=12),
        location=LOC, entity_ids=["ENTITY-1"]
    )
    e3 = CanonicalEvent(
        event_id="E3", event_type="PATROL_DEVIATION", timestamp=BASE_TIME + timedelta(minutes=45),
        location=LOC, entity_ids=["ENTITY-1"]
    )

    is_seq, conf = temporal.is_sequential(e1, e2, window_seconds=1800.0)
    assert is_seq is True
    assert conf >= 0.80

    # e3 is 45 minutes after e1 (> 30 mins sequence window)
    is_seq_far, _ = temporal.is_sequential(e1, e3, window_seconds=1800.0)
    assert is_seq_far is False


def test_detect_temporal_burst():
    """Verify detection of >= 3 events occurring within 10 minutes."""
    temporal = TemporalIntelligence()
    burst_events = [
        CanonicalEvent(
            event_id=f"B{i}", event_type="SENSOR_PING",
            timestamp=BASE_TIME + timedelta(minutes=i * 2),
            location=LOC, entity_ids=["RADAR-1"]
        )
        for i in range(4)
    ]
    bursts = temporal.detect_bursts(burst_events, window_seconds=600.0, min_events=3)
    assert len(bursts) == 1
    assert bursts[0]["event_count"] >= 3
    assert bursts[0]["duration_seconds"] <= 600.0


def test_detect_periodic_recurrence():
    """Verify detection of events recurring at regular intervals."""
    temporal = TemporalIntelligence()
    # 4 events exactly 15 minutes (900 seconds) apart
    recurring_events = [
        CanonicalEvent(
            event_id=f"R{i}", event_type="MOVEMENT",
            timestamp=BASE_TIME + timedelta(minutes=i * 15),
            location=LOC, entity_ids=["PATROL-1"]
        )
        for i in range(4)
    ]
    result = temporal.detect_recurrence(recurring_events, tolerance_seconds=60.0)
    assert result is not None
    assert result["detected"] is True
    assert result["interval_seconds"] == 900.0
    assert result["confidence"] >= 0.80
