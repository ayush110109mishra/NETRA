"""
Unit tests for NETRA Phase 8 Provenance Engine.
Verifies orphan prevention, integrity validation, and evidence lineage.
"""

from datetime import datetime, timezone
import pytest

from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry
from graph.provenance import ProvenanceEngine
from models.knowledge_graph import EdgeType, NodeType, ProvenanceItem
from models.predictive_intelligence import EpistemicStatus


@pytest.fixture
def registries():
    nr = NodeRegistry()
    er = EdgeRegistry()
    return nr, er


def test_orphan_edge_detection(registries):
    nr, er = registries
    engine = ProvenanceEngine(nr, er)
    now = datetime.now(timezone.utc)

    # Add only one node
    node_a = nr.add_node(NodeType.ENTITY, "A", "A", now)

    # Add edge pointing to non-existent node B
    er.add_edge(
        source_node_id=node_a.node_id,
        target_node_id="NODE-ENTITY-NONEXISTENT",
        edge_type=EdgeType.ASSOCIATED_WITH,
        evidence_ids=["EVT-01"],
    )

    val = engine.validate_graph()
    assert val["is_valid"] is False
    assert len(val["orphan_edges"]) == 1


def test_valid_graph_validation(registries):
    nr, er = registries
    engine = ProvenanceEngine(nr, er)
    now = datetime.now(timezone.utc)

    node_a = nr.add_node(NodeType.ENTITY, "A", "A", now)
    node_b = nr.add_node(NodeType.ENTITY, "B", "B", now)

    p = ProvenanceItem(evidence_id="EVT-01", epistemic_status=EpistemicStatus.OBSERVED)
    er.add_edge(
        source_node_id=node_a.node_id,
        target_node_id=node_b.node_id,
        edge_type=EdgeType.ASSOCIATED_WITH,
        evidence_ids=["EVT-01"],
        provenance=[p],
        is_directional=False,
    )

    val = engine.validate_graph()
    assert val["is_valid"] is True
    assert len(val["orphan_edges"]) == 0
    assert len(val["invalid_temporal_edges"]) == 0


def test_full_evidence_trail(registries):
    nr, er = registries
    engine = ProvenanceEngine(nr, er)
    now = datetime.now(timezone.utc)

    p1 = ProvenanceItem(evidence_id="RADAR-01", epistemic_status=EpistemicStatus.OBSERVED)
    node_a = nr.add_node(NodeType.ENTITY, "A", "A", now, provenance=[p1])
    node_b = nr.add_node(NodeType.ENTITY, "B", "B", now)

    p2 = ProvenanceItem(evidence_id="OPT-02", epistemic_status=EpistemicStatus.OBSERVED)
    er.add_edge(
        source_node_id=node_a.node_id,
        target_node_id=node_b.node_id,
        edge_type=EdgeType.ASSOCIATED_WITH,
        evidence_ids=["FUS-01"],
        provenance=[p2],
        is_directional=False,
    )

    trail = engine.get_full_evidence_trail(node_a.node_id)
    assert set(trail) == {"RADAR-01", "OPT-02", "FUS-01"}
