"""
Tests for Phase 3 Entity Profile Aggregation.
"""

from datetime import datetime, timezone, timedelta
from models.common import Coordinates, EntityStatus, Allegiance
from models.event_intelligence import CanonicalEvent, EventSource
from models.entity_intelligence import CanonicalEntity
from entities.profile import EntityProfileAggregator

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)


def test_entity_profile_aggregation_basic():
    entity = CanonicalEntity(
        entity_id="ENTITY-TEST-01",
        entity_type="VEHICLE",
        callsign="ALPHA-1",
        allegiance=Allegiance.FRIENDLY,
        status=EntityStatus.ACTIVE,
        first_observed=BASE_TIME - timedelta(hours=24),
        last_observed=BASE_TIME,
        observation_count=4,
        event_count=4,
    )
    events = [
        CanonicalEvent(
            event_id=f"EVT-{i}",
            event_type="movement" if i < 3 else "sensor_ping",
            timestamp=BASE_TIME - timedelta(hours=24 - i * 8),
            location=Coordinates(latitude=26.85 + i * 0.01, longitude=80.95),
            entity_ids=["ENTITY-TEST-01"],
            attributes={"speed": 40.0, "activity_level": 0.3},
        )
        for i in range(4)
    ]

    profile = EntityProfileAggregator.aggregate(
        entity=entity,
        events=events,
        associated_entities_count=2,
        associated_clusters_count=1,
    )

    assert profile.entity_id == "ENTITY-TEST-01"
    assert profile.entity_type == "VEHICLE"
    assert profile.active_duration_hours == 24.0
    assert profile.unique_locations_count == 4
    assert profile.dominant_event_type == "movement"
    assert profile.associated_entities_count == 2
    assert profile.associated_clusters_count == 1


def test_entity_profile_empty_events():
    entity = CanonicalEntity(
        entity_id="ENTITY-EMPTY-02",
        entity_type="AIRCRAFT",
        callsign="GHOST",
        allegiance=Allegiance.UNKNOWN,
        status=EntityStatus.UNKNOWN,
        first_observed=BASE_TIME,
        last_observed=BASE_TIME,
        observation_count=1,
        event_count=1,
    )
    profile = EntityProfileAggregator.aggregate(entity, [])

    assert profile.entity_id == "ENTITY-EMPTY-02"
    assert profile.active_duration_hours == 0.0
    assert profile.unique_locations_count == 1
    assert profile.dominant_event_type == "UNKNOWN"
