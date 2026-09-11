"""
Tests for Entity Network Builder in NETRA.
"""

from datetime import datetime, timezone, timedelta
from models.common import Coordinates, RelationshipType, SeverityLevel
from models.event_intelligence import CanonicalEvent, EventCluster
from entities.network import EntityNetworkBuilder

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)


def test_network_co_occurrence_and_repeated_association():
    events = [
        CanonicalEvent(
            event_id="EVT-1",
            event_type="movement",
            timestamp=BASE_TIME - timedelta(hours=10),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENT-ALPHA", "ENT-BETA"],
        ),
        CanonicalEvent(
            event_id="EVT-2",
            event_type="patrol",
            timestamp=BASE_TIME - timedelta(hours=5),
            location=Coordinates(latitude=26.86, longitude=80.96),
            entity_ids=["ENT-ALPHA", "ENT-BETA"],
        ),
    ]

    relationships = EntityNetworkBuilder.build_relationships(
        target_entity_id="ENT-ALPHA",
        all_events=events,
    )

    assert len(relationships) == 1
    edge = relationships[0]
    assert edge.entity_id == "ENT-BETA"
    assert edge.relationship_type == RelationshipType.REPEATED_ASSOCIATION
    assert edge.co_occurrence_count == 2
    assert "EVT-1" in edge.evidence_event_ids
    assert "EVT-2" in edge.evidence_event_ids


def test_network_shared_cluster():
    cluster = EventCluster(
        cluster_id="CLUS-01",
        event_ids=["EVT-1", "EVT-2"],
        event_count=2,
        unique_entities=["ENT-ALPHA", "ENT-GAMMA"],
        event_types=["movement"],
        start_time=BASE_TIME,
        end_time=BASE_TIME + timedelta(minutes=30),
        duration_seconds=1800.0,
        spatial_extent={"centroid": {"latitude": 26.85, "longitude": 80.95}},
        cohesion_score=0.90,
        average_risk=0.30,
        average_confidence=0.85,
        average_severity=SeverityLevel.LOW,
    )

    events = [
        CanonicalEvent(
            event_id="EVT-1",
            event_type="movement",
            timestamp=BASE_TIME,
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENT-ALPHA"],
        ),
        CanonicalEvent(
            event_id="EVT-2",
            event_type="movement",
            timestamp=BASE_TIME + timedelta(minutes=30),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENT-GAMMA"],
        ),
    ]

    relationships = EntityNetworkBuilder.build_relationships(
        target_entity_id="ENT-ALPHA",
        all_events=events,
        clusters=[cluster],
    )

    assert len(relationships) == 1
    edge = relationships[0]
    assert edge.entity_id == "ENT-GAMMA"
    assert edge.relationship_type in [RelationshipType.SHARED_CLUSTER, RelationshipType.SPATIAL_ASSOCIATION]
    assert edge.score > 0.60
