"""
Unit tests for NETRA Phase 8 Edge Registry.
Verifies deterministic edge identity, symmetric deduplication, contradiction preservation,
and adjacency indexing.
"""

from datetime import datetime, timezone
import pytest

from graph.edge_registry import EdgeRegistry, generate_edge_id
from models.knowledge_graph import EdgeType, ProvenanceItem
from models.predictive_intelligence import EpistemicStatus


@pytest.fixture
def edge_registry():
    return EdgeRegistry()


def test_deterministic_edge_id_symmetric():
    # Symmetric edge A-B vs B-A must yield identical IDs
    id_ab = generate_edge_id("NODE-A", "NODE-B", EdgeType.ASSOCIATED_WITH, is_directional=False)
    id_ba = generate_edge_id("NODE-B", "NODE-A", EdgeType.ASSOCIATED_WITH, is_directional=False)
    assert id_ab == id_ba

    # Directional edge A->B vs B->A must yield different IDs
    id_dir_ab = generate_edge_id("NODE-A", "NODE-B", EdgeType.OBSERVED_BY, is_directional=True)
    id_dir_ba = generate_edge_id("NODE-B", "NODE-A", EdgeType.OBSERVED_BY, is_directional=True)
    assert id_dir_ab != id_dir_ba


def test_edge_symmetric_deduplication(edge_registry):
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)
    e1 = edge_registry.add_edge(
        source_node_id="NODE-ENTITY-1",
        target_node_id="NODE-ENTITY-2",
        edge_type=EdgeType.ASSOCIATED_WITH,
        strength=0.70,
        evidence_ids=["EVT-01"],
        is_directional=False,
    )
    assert edge_registry.count() == 1

    # Add reverse edge
    e2 = edge_registry.add_edge(
        source_node_id="NODE-ENTITY-2",
        target_node_id="NODE-ENTITY-1",
        edge_type=EdgeType.ASSOCIATED_WITH,
        strength=0.85,
        evidence_ids=["EVT-02"],
        is_directional=False,
    )
    assert edge_registry.count() == 1
    assert e1.edge_id == e2.edge_id
    assert e2.strength == 0.85
    assert set(e2.evidence_ids) == {"EVT-01", "EVT-02"}


def test_contradiction_preservation(edge_registry):
    # Conflicting evidence must NOT be dropped, and epistemic status updated to UNCERTAIN
    e = edge_registry.add_edge(
        source_node_id="NODE-A",
        target_node_id="NODE-B",
        edge_type=EdgeType.ASSOCIATED_WITH,
        evidence_ids=["EVT-SUPPORT-1"],
        contradicting_evidence_ids=["EVT-CONFLICT-1"],
        is_directional=False,
    )
    assert e.epistemic_status == EpistemicStatus.UNCERTAIN
    assert "EVT-SUPPORT-1" in e.evidence_ids
    assert "EVT-CONFLICT-1" in e.contradicting_evidence_ids


def test_adjacency_indexing(edge_registry):
    edge_registry.add_edge(
        source_node_id="NODE-A",
        target_node_id="NODE-B",
        edge_type=EdgeType.ASSOCIATED_WITH,
        is_directional=False,
    )
    edge_registry.add_edge(
        source_node_id="NODE-B",
        target_node_id="NODE-C",
        edge_type=EdgeType.ASSOCIATED_WITH,
        is_directional=False,
    )

    incident_b = edge_registry.get_incident_edges("NODE-B")
    assert len(incident_b) == 2

    between_ab = edge_registry.get_edges_between("NODE-A", "NODE-B")
    assert len(between_ab) == 1
    assert between_ab[0].edge_type == EdgeType.ASSOCIATED_WITH
