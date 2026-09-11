"""
Unit tests for NETRA Phase 8 Node Registry.
Verifies deterministic identity, deduplication, idempotency, type filtering, and temporal validity.
"""

from datetime import datetime, timezone, timedelta
import pytest

from graph.node_registry import NodeRegistry, generate_node_id
from models.knowledge_graph import NodeType, ProvenanceItem
from models.predictive_intelligence import EpistemicStatus


@pytest.fixture
def node_registry():
    return NodeRegistry()


def test_deterministic_node_id():
    id1 = generate_node_id(NodeType.ENTITY, "ENTITY-01")
    id2 = generate_node_id(NodeType.ENTITY, "ENTITY-01")
    id3 = generate_node_id(NodeType.ENTITY, "ENTITY-02")
    assert id1 == id2
    assert id1 != id3
    assert id1.startswith("NODE-ENTITY-")


def test_node_deduplication_and_idempotency(node_registry):
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)
    p1 = ProvenanceItem(evidence_id="EVT-01", epistemic_status=EpistemicStatus.OBSERVED)
    p2 = ProvenanceItem(evidence_id="EVT-02", epistemic_status=EpistemicStatus.OBSERVED)

    n1 = node_registry.add_node(
        node_type=NodeType.ENTITY,
        label="ENTITY-01",
        canonical_reference="ENTITY-01",
        created_at=now,
        confidence=0.80,
        provenance=[p1],
    )
    assert node_registry.count() == 1

    # Add same node again with additional provenance
    n2 = node_registry.add_node(
        node_type=NodeType.ENTITY,
        label="ENTITY-01",
        canonical_reference="ENTITY-01",
        created_at=now + timedelta(minutes=5),
        confidence=0.85,
        provenance=[p2],
    )
    assert node_registry.count() == 1
    assert n1.node_id == n2.node_id
    assert n2.confidence == 0.85
    assert len(n2.provenance) == 2
    assert [p.evidence_id for p in n2.provenance] == ["EVT-01", "EVT-02"]


def test_node_temporal_filtering(node_registry):
    t1 = datetime(2026, 9, 12, 8, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    t3 = datetime(2026, 9, 12, 16, 0, 0, tzinfo=timezone.utc)

    node_registry.add_node(
        node_type=NodeType.EVENT,
        label="Morning Event",
        canonical_reference="EVT-MORNING",
        created_at=t1,
        valid_from=t1,
        valid_to=t2,
    )
    node_registry.add_node(
        node_type=NodeType.EVENT,
        label="Afternoon Event",
        canonical_reference="EVT-AFTERNOON",
        created_at=t2,
        valid_from=t2,
        valid_to=t3,
    )

    # At 9:00, only morning event is active
    active_9am = node_registry.get_active_nodes(datetime(2026, 9, 12, 9, 0, 0, tzinfo=timezone.utc))
    assert len(active_9am) == 1
    assert active_9am[0].label == "Morning Event"

    # At 14:00, only afternoon event is active
    active_2pm = node_registry.get_active_nodes(datetime(2026, 9, 12, 14, 0, 0, tzinfo=timezone.utc))
    assert len(active_2pm) == 1
    assert active_2pm[0].label == "Afternoon Event"


def test_node_type_filtering(node_registry):
    now = datetime.now(timezone.utc)
    node_registry.add_node(NodeType.ENTITY, "E1", "E1", now)
    node_registry.add_node(NodeType.ENTITY, "E2", "E2", now)
    node_registry.add_node(NodeType.SOURCE, "S1", "S1", now)

    entities = node_registry.get_nodes_by_type(NodeType.ENTITY)
    sources = node_registry.get_nodes_by_type(NodeType.SOURCE)
    anomalies = node_registry.get_nodes_by_type(NodeType.ANOMALY)

    assert len(entities) == 2
    assert len(sources) == 1
    assert len(anomalies) == 0
