"""
Unit tests for Pattern Detection Engine.
Tests sequential escalation, temporal bursts, multi-entity coordination, and periodicity.
"""

from datetime import datetime, timezone, timedelta
import pytest

from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from events.patterns import PatternDetector

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)
LOC = Coordinates(latitude=26.84, longitude=80.94)


def test_detect_sequential_escalation():
    """Verify chronological escalation from MOVEMENT -> PATROL_DEVIATION -> PERIMETER_PROXIMITY."""
    detector = PatternDetector()
    events = [
        CanonicalEvent(event_id="E1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, entity_ids=["T1"]),
        CanonicalEvent(event_id="E2", event_type="PATROL_DEVIATION", timestamp=BASE_TIME + timedelta(minutes=10), location=LOC, entity_ids=["T1"]),
        CanonicalEvent(event_id="E3", event_type="PERIMETER_PROXIMITY", timestamp=BASE_TIME + timedelta(minutes=20), location=LOC, entity_ids=["T1"]),
    ]
    patterns = detector.detect_patterns(events)
    types = [p.pattern_type for p in patterns]
    assert "SEQUENTIAL_ESCALATION" in types


def test_detect_temporal_burst_pattern():
    """Verify flurry of events within short window flags TEMPORAL_BURST."""
    detector = PatternDetector()
    events = [
        CanonicalEvent(event_id=f"B{i}", event_type="SENSOR_PING", timestamp=BASE_TIME + timedelta(minutes=i), location=LOC, entity_ids=["T1"])
        for i in range(4)
    ]
    patterns = detector.detect_patterns(events)
    types = [p.pattern_type for p in patterns]
    assert "TEMPORAL_BURST" in types


def test_detect_multi_entity_coordination():
    """Verify multiple distinct entities operating in tight spatial-temporal radius flags coordination."""
    detector = PatternDetector()
    events = [
        CanonicalEvent(event_id="C1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, entity_ids=["LEADER"]),
        CanonicalEvent(event_id="C2", event_type="MOVEMENT", timestamp=BASE_TIME + timedelta(minutes=5), location=Coordinates(latitude=26.842, longitude=80.942), entity_ids=["WINGMAN"]),
    ]
    patterns = detector.detect_patterns(events)
    types = [p.pattern_type for p in patterns]
    assert "MULTI_ENTITY_COORDINATION" in types
