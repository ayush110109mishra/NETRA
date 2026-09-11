"""
Unit tests for Event Clustering Engine.
Tests cluster formation from correlation links, multi-cluster separation,
isolated event exclusions, cohesion scores, and feature aggregation.
"""

from datetime import datetime, timezone, timedelta
import pytest

from models.common import Coordinates, RelationshipStrength, SeverityLevel
from models.event_intelligence import CanonicalEvent, EventCorrelation, CorrelationComponents
from events.clustering import EventClusterer

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)
LOC = Coordinates(latitude=26.84, longitude=80.94)


def test_single_cluster_formation():
    """Verify strongly correlated events form a single cluster with accurate features."""
    clusterer = EventClusterer()
    events = [
        CanonicalEvent(event_id="E1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, entity_ids=["ENT-1"]),
        CanonicalEvent(event_id="E2", event_type="PATROL_DEVIATION", timestamp=BASE_TIME + timedelta(minutes=10), location=LOC, entity_ids=["ENT-1"]),
    ]
    correlations = [
        EventCorrelation(
            source_event_id="E1", target_event_id="E2", correlation_score=0.85,
            strength=RelationshipStrength.STRONG,
            components=CorrelationComponents(temporal=0.9, spatial=1.0, entity=1.0, type_similarity=0.75, attribute_similarity=0.7),
            confidence=0.90, reasoning="Strong association"
        )
    ]

    clusters = clusterer.cluster_events(events, correlations)
    assert len(clusters) == 1
    c = clusters[0]
    assert c.cluster_id == "CLUSTER-SYNTH-001"
    assert c.event_count == 2
    assert "E1" in c.event_ids and "E2" in c.event_ids
    assert c.unique_entities == ["ENT-1"]
    assert c.cohesion_score == 0.85
    assert c.duration_seconds == 600.0


def test_isolated_events_excluded_from_clusters():
    """Verify events with correlation below threshold (< 0.60) do not form clusters."""
    clusterer = EventClusterer()
    events = [
        CanonicalEvent(event_id="E1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, entity_ids=["ENT-1"]),
        CanonicalEvent(event_id="E2", event_type="MOVEMENT", timestamp=BASE_TIME + timedelta(hours=5), location=LOC, entity_ids=["ENT-2"]),
    ]
    correlations = [
        EventCorrelation(
            source_event_id="E1", target_event_id="E2", correlation_score=0.25,
            strength=RelationshipStrength.WEAK,
            components=CorrelationComponents(temporal=0.0, spatial=1.0, entity=0.0, type_similarity=1.0, attribute_similarity=0.5),
            confidence=0.70, reasoning="Weak association"
        )
    ]

    clusters = clusterer.cluster_events(events, correlations)
    assert len(clusters) == 0


def test_multiple_independent_clusters():
    """Verify two distinct sets of events form two independent clusters."""
    clusterer = EventClusterer()
    events = [
        # Group 1 (A & B)
        CanonicalEvent(event_id="A1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, entity_ids=["ENT-A"]),
        CanonicalEvent(event_id="A2", event_type="MOVEMENT", timestamp=BASE_TIME + timedelta(minutes=5), location=LOC, entity_ids=["ENT-A"]),
        # Group 2 (X & Y)
        CanonicalEvent(event_id="X1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, entity_ids=["ENT-X"]),
        CanonicalEvent(event_id="X2", event_type="MOVEMENT", timestamp=BASE_TIME + timedelta(minutes=5), location=LOC, entity_ids=["ENT-X"]),
    ]
    correlations = [
        # Strong link within Group 1
        EventCorrelation(
            source_event_id="A1", target_event_id="A2", correlation_score=0.90,
            strength=RelationshipStrength.VERY_STRONG,
            components=CorrelationComponents(temporal=1.0, spatial=1.0, entity=1.0, type_similarity=1.0, attribute_similarity=0.8),
            confidence=0.95, reasoning="A1-A2"
        ),
        # Strong link within Group 2
        EventCorrelation(
            source_event_id="X1", target_event_id="X2", correlation_score=0.88,
            strength=RelationshipStrength.STRONG,
            components=CorrelationComponents(temporal=1.0, spatial=1.0, entity=1.0, type_similarity=1.0, attribute_similarity=0.8),
            confidence=0.95, reasoning="X1-X2"
        ),
        # Weak link between groups
        EventCorrelation(
            source_event_id="A1", target_event_id="X1", correlation_score=0.20,
            strength=RelationshipStrength.VERY_WEAK,
            components=CorrelationComponents(temporal=1.0, spatial=1.0, entity=0.0, type_similarity=1.0, attribute_similarity=0.0),
            confidence=0.60, reasoning="Between"
        ),
    ]

    clusters = clusterer.cluster_events(events, correlations)
    assert len(clusters) == 2
    c_ids = [c.cluster_id for c in clusters]
    assert "CLUSTER-SYNTH-001" in c_ids
    assert "CLUSTER-SYNTH-002" in c_ids
