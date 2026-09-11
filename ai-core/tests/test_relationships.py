"""
Unit tests for NETRA Event & Entity Relationship Detection.
Verifies spatial, temporal, same-entity, and sequential correlation rules.
"""

from datetime import datetime, timezone, timedelta
import pytest

from models.common import Coordinates, RelationshipType
from models.input import (
    EventInput,
    EntityInput,
    ContextEntityInput,
    ContextEventInput,
)
from events.relationships import detect_event_relationships
from entities.relationships import detect_entity_relationships

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)
PRIMARY_LOC = Coordinates(latitude=26.8467, longitude=80.9462)


def test_event_relationships_same_entity_and_sequential():
    """Verify same entity actions within 30 mins are flagged as SEQUENTIAL."""
    primary_event = EventInput(
        event_id="EVT-001",
        event_type="movement",
        description="Lead unit movement",
        timestamp=BASE_TIME,
    )
    context_events = [
        ContextEventInput(
            event_id="EVT-002",
            event_type="sensor_ping",
            entity_id="ENTITY-010",
            location=PRIMARY_LOC,
            timestamp=BASE_TIME + timedelta(minutes=10),
        )
    ]
    results = detect_event_relationships(
        primary_event=primary_event,
        primary_entity_id="ENTITY-010",
        primary_location=PRIMARY_LOC,
        context_events=context_events,
    )
    assert len(results) == 1
    assert results[0].event_id == "EVT-002"
    assert results[0].relationship == RelationshipType.SEQUENTIAL
    assert results[0].confidence > 0.85


def test_event_relationships_same_location():
    """Verify events at identical/near location with different entity are flagged as SAME_LOCATION."""
    primary_event = EventInput(
        event_id="EVT-001",
        event_type="movement",
        description="Lead unit movement",
        timestamp=BASE_TIME,
    )
    context_events = [
        ContextEventInput(
            event_id="EVT-003",
            event_type="patrol_deviation",
            entity_id="ENTITY-DIFFERENT",
            location=Coordinates(latitude=26.8468, longitude=80.9463),  # ~15 meters away
            timestamp=BASE_TIME + timedelta(hours=3),
        )
    ]
    results = detect_event_relationships(
        primary_event=primary_event,
        primary_entity_id="ENTITY-010",
        primary_location=PRIMARY_LOC,
        context_events=context_events,
    )
    assert len(results) == 1
    assert results[0].event_id == "EVT-003"
    assert results[0].relationship in [RelationshipType.SAME_LOCATION, RelationshipType.SPATIAL_PROXIMITY]


def test_event_relationships_empty_context():
    """Verify empty context events list returns empty list."""
    primary_event = EventInput(
        event_id="EVT-001",
        event_type="movement",
        description="Solo movement",
        timestamp=BASE_TIME,
    )
    results = detect_event_relationships(
        primary_event=primary_event,
        primary_entity_id="ENTITY-010",
        primary_location=PRIMARY_LOC,
        context_events=[],
    )
    assert results == []


def test_entity_relationships_spatial_proximity():
    """Verify entities within 15 km are flagged with SPATIAL_PROXIMITY."""
    primary_entity = EntityInput(
        entity_id="ENTITY-001",
        entity_type="vehicle",
    )
    # Location ~3 km away
    nearby_loc = Coordinates(latitude=26.8700, longitude=80.9462)
    context_entities = [
        ContextEntityInput(
            entity_id="ENTITY-002",
            entity_type="vehicle",
            location=nearby_loc,
            last_seen=BASE_TIME,
        )
    ]
    results = detect_entity_relationships(
        primary_entity=primary_entity,
        primary_location=PRIMARY_LOC,
        primary_timestamp=BASE_TIME,
        context_entities=context_entities,
    )
    assert len(results) == 1
    assert results[0].entity_id == "ENTITY-002"
    assert results[0].relationship == RelationshipType.SPATIAL_PROXIMITY
    assert results[0].confidence >= 0.70
