"""
Unit tests for Multi-Dimensional Event Correlation Engine.
Includes critical FALSE-CORRELATION tests (Section 24) to ensure the system
never assumes causation from isolated spatial or temporal co-occurrences.
"""

from datetime import datetime, timezone, timedelta
import pytest

from models.common import Coordinates, RelationshipStrength, RelationshipType
from models.event_intelligence import CanonicalEvent
from events.correlation import MultiDimensionalCorrelator

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)
LOC1 = Coordinates(latitude=26.8467, longitude=80.9462)
LOC_DISTANT = Coordinates(latitude=27.8000, longitude=81.8000)  # > 100 km away


def test_strong_multidimensional_correlation():
    """Verify same entity, close in time, and close in space yields STRONG correlation."""
    correlator = MultiDimensionalCorrelator()
    e1 = CanonicalEvent(
        event_id="EVT-1", event_type="MOVEMENT", timestamp=BASE_TIME,
        location=LOC1, entity_ids=["ENTITY-ALPHA"],
        attributes={"speed": 50.0, "activity_level": 0.60}
    )
    e2 = CanonicalEvent(
        event_id="EVT-2", event_type="PATROL_DEVIATION", timestamp=BASE_TIME + timedelta(minutes=10),
        location=Coordinates(latitude=26.8480, longitude=80.9480), entity_ids=["ENTITY-ALPHA"],
        attributes={"speed": 70.0, "activity_level": 0.75}
    )

    corr = correlator.correlate_pair(e1, e2)
    assert corr.correlation_score >= 0.75
    assert corr.strength in [RelationshipStrength.STRONG, RelationshipStrength.VERY_STRONG]
    assert RelationshipType.SAME_ENTITY in corr.relationships
    assert RelationshipType.TEMPORAL_PROXIMITY in corr.relationships
    assert RelationshipType.SPATIAL_PROXIMITY in corr.relationships
    assert corr.confidence >= 0.85


def test_false_correlation_same_location_different_time_different_entity():
    """
    CRITICAL FALSE-CORRELATION TEST:
    Same location, BUT 8 hours later and different entities.
    MUST NOT produce a strong relationship!
    """
    correlator = MultiDimensionalCorrelator()
    e1 = CanonicalEvent(
        event_id="EVT-LOC-1", event_type="MOVEMENT", timestamp=BASE_TIME,
        location=LOC1, entity_ids=["ENTITY-MORNING"],
        attributes={"speed": 40.0, "activity_level": 0.3}
    )
    e2 = CanonicalEvent(
        event_id="EVT-LOC-2", event_type="MOVEMENT", timestamp=BASE_TIME + timedelta(hours=8),
        location=LOC1, entity_ids=["ENTITY-EVENING"],
        attributes={"speed": 20.0, "activity_level": 0.2}
    )

    corr = correlator.correlate_pair(e1, e2)
    # Temporal is 0 (outside 2hr window), Entity is 0. Spatial is 1.0 (weight 0.20).
    # Total score should be strictly WEAK or VERY_WEAK (< 0.40)
    assert corr.correlation_score < 0.40
    assert corr.strength in [RelationshipStrength.VERY_WEAK, RelationshipStrength.WEAK]


def test_false_correlation_same_time_distant_locations_different_entity():
    """
    CRITICAL FALSE-CORRELATION TEST:
    Same time, BUT 100 km apart and different entities.
    MUST NOT produce a strong relationship!
    """
    correlator = MultiDimensionalCorrelator()
    e1 = CanonicalEvent(
        event_id="EVT-TIME-1", event_type="MOVEMENT", timestamp=BASE_TIME,
        location=LOC1, entity_ids=["ENTITY-SECTOR-A"],
        attributes={"speed": 40.0, "activity_level": 0.3}
    )
    e2 = CanonicalEvent(
        event_id="EVT-TIME-2", event_type="MOVEMENT", timestamp=BASE_TIME + timedelta(seconds=10),
        location=LOC_DISTANT, entity_ids=["ENTITY-SECTOR-Z"],
        attributes={"speed": 40.0, "activity_level": 0.3}
    )

    corr = correlator.correlate_pair(e1, e2)
    # Spatial is 0, Entity is 0. Temporal is 1.0 (weight 0.25).
    assert corr.correlation_score < 0.45
    assert corr.strength in [RelationshipStrength.VERY_WEAK, RelationshipStrength.WEAK]


def test_false_correlation_type_similarity_alone():
    """
    CRITICAL FALSE-CORRELATION TEST:
    Matching event types alone (distant in time, distant in space, different entities)
    must produce VERY_WEAK correlation.
    """
    correlator = MultiDimensionalCorrelator()
    e1 = CanonicalEvent(
        event_id="EVT-TYPE-1", event_type="RADAR_ANOMALY", timestamp=BASE_TIME,
        location=LOC1, entity_ids=["ENTITY-A"],
    )
    e2 = CanonicalEvent(
        event_id="EVT-TYPE-2", event_type="RADAR_ANOMALY", timestamp=BASE_TIME + timedelta(hours=12),
        location=LOC_DISTANT, entity_ids=["ENTITY-B"],
    )

    corr = correlator.correlate_pair(e1, e2)
    # Temporal: 0, Spatial: 0, Entity: 0. Type: 0.15 * 1.0 = 0.15.
    assert corr.correlation_score <= 0.24
    assert corr.strength == RelationshipStrength.VERY_WEAK


def test_relationship_strength_bands():
    """Verify mathematical mapping to categorical strength bands."""
    correlator = MultiDimensionalCorrelator()
    assert correlator.map_strength(0.10) == RelationshipStrength.VERY_WEAK
    assert correlator.map_strength(0.35) == RelationshipStrength.WEAK
    assert correlator.map_strength(0.60) == RelationshipStrength.MODERATE
    assert correlator.map_strength(0.82) == RelationshipStrength.STRONG
    assert correlator.map_strength(0.95) == RelationshipStrength.VERY_STRONG
