"""
Unit tests for Event Deduplication Engine.
Tests exact ID duplicates, near-duplicate telemetry, distinct events, and audit reasons.
"""

from datetime import datetime, timezone, timedelta
import pytest

from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from events.deduplication import EventDeduplicator

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)
LOC = Coordinates(latitude=26.8467, longitude=80.9462)


def test_exact_id_duplicate():
    """Verify identical event ID is flagged as exact duplicate."""
    dedup = EventDeduplicator()
    e1 = CanonicalEvent(event_id="EVT-1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC)
    e2 = CanonicalEvent(event_id="EVT-1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC)

    results = dedup.analyze_duplicates([e1, e2])
    assert results[0].is_duplicate is False
    assert results[1].is_duplicate is True
    assert results[1].duplicate_of == "EVT-1"
    assert "identical_event_id" in results[1].reasons


def test_exact_telemetry_duplicate():
    """Verify same entity, same type within 5s and 50m is flagged."""
    dedup = EventDeduplicator()
    # ~15 meters away
    loc_near = Coordinates(latitude=26.8468, longitude=80.9463)
    e1 = CanonicalEvent(event_id="EVT-1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, entity_ids=["E-1"])
    e2 = CanonicalEvent(event_id="EVT-2", event_type="MOVEMENT", timestamp=BASE_TIME + timedelta(seconds=3), location=loc_near, entity_ids=["E-1"])

    results = dedup.analyze_duplicates([e1, e2])
    assert results[1].is_duplicate is True
    assert results[1].duplicate_of == "EVT-1"
    assert "same_entity" in results[1].reasons
    assert "same_location" in results[1].reasons


def test_near_duplicate():
    """Verify same entity, same type within 45s and 150m is flagged as near duplicate."""
    dedup = EventDeduplicator()
    loc_150m = Coordinates(latitude=26.8480, longitude=80.9462)
    e1 = CanonicalEvent(event_id="EVT-1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, entity_ids=["E-1"])
    e2 = CanonicalEvent(event_id="EVT-2", event_type="MOVEMENT", timestamp=BASE_TIME + timedelta(seconds=30), location=loc_150m, entity_ids=["E-1"])

    results = dedup.analyze_duplicates([e1, e2])
    assert results[1].is_duplicate is True
    assert results[1].duplicate_of == "EVT-1"
    assert "near_location" in results[1].reasons


def test_non_duplicate_different_entity():
    """Verify different entities at same location and time are NOT duplicates."""
    dedup = EventDeduplicator()
    e1 = CanonicalEvent(event_id="EVT-1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, entity_ids=["ENTITY-ALPHA"])
    e2 = CanonicalEvent(event_id="EVT-2", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, entity_ids=["ENTITY-BRAVO"])

    results = dedup.analyze_duplicates([e1, e2])
    assert results[0].is_duplicate is False
    assert results[1].is_duplicate is False
