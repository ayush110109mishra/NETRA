"""
Unit tests for NETRA Phase 8 Path Analysis Engine.
Verifies multi-hop path finding, deterministic tie-breaking, bottleneck confidence, and disjoint graphs.
"""

from datetime import datetime, timezone
import pytest

from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry
from graph.graph_builder import KnowledgeGraphBuilder
from graph.path_analysis import PathAnalysisEngine
from models.knowledge_graph import EdgeType


@pytest.fixture
def path_engine():
    nr = NodeRegistry()
    er = EdgeRegistry()
    gb = KnowledgeGraphBuilder(nr, er)
    pe = PathAnalysisEngine(nr, er)
    return nr, er, gb, pe


def test_shortest_path_multi_hop(path_engine):
    nr, er, gb, pe = path_engine
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    # Build chain: A -> B -> C
    gb.ingest_entity("ENTITY-A", first_observed=now)
    gb.ingest_entity("ENTITY-B", first_observed=now)
    gb.ingest_entity("ENTITY-C", first_observed=now)

    na = nr.get_node_by_reference("ENTITY-A")
    nb = nr.get_node_by_reference("ENTITY-B")
    nc = nr.get_node_by_reference("ENTITY-C")

    er.add_edge(na.node_id, nb.node_id, EdgeType.ASSOCIATED_WITH, strength=0.8, confidence=0.9, evidence_ids=["EVT-1"], is_directional=False)
    er.add_edge(nb.node_id, nc.node_id, EdgeType.ASSOCIATED_WITH, strength=0.7, confidence=0.8, evidence_ids=["EVT-2"], is_directional=False)

    res = pe.find_shortest_path("ENTITY-A", "ENTITY-C")
    assert res.path_found is True
    assert res.hop_count == 2
    assert res.path_confidence == 0.8  # Bottleneck (min(0.9, 0.8))
    assert set(res.supporting_evidence) == {"EVT-1", "EVT-2"}


def test_disconnected_path(path_engine):
    nr, er, gb, pe = path_engine
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    gb.ingest_entity("ENTITY-X", first_observed=now)
    gb.ingest_entity("ENTITY-Y", first_observed=now)

    res = pe.find_shortest_path("ENTITY-X", "ENTITY-Y")
    assert res.path_found is False
    assert "No evidence-supported path was found" in res.explanation


def test_deterministic_tie_breaking(path_engine):
    nr, er, gb, pe = path_engine
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    # Diamond graph:
    #      B (conf 0.9)
    #    /   \
    #   A     D
    #    \   /
    #      C (conf 0.8)
    gb.ingest_entity("A", first_observed=now)
    gb.ingest_entity("B", first_observed=now)
    gb.ingest_entity("C", first_observed=now)
    gb.ingest_entity("D", first_observed=now)

    na = nr.get_node_by_reference("A")
    nb = nr.get_node_by_reference("B")
    nc = nr.get_node_by_reference("C")
    nd = nr.get_node_by_reference("D")

    # Path 1 via B: higher confidence
    er.add_edge(na.node_id, nb.node_id, EdgeType.ASSOCIATED_WITH, confidence=0.9, is_directional=False)
    er.add_edge(nb.node_id, nd.node_id, EdgeType.ASSOCIATED_WITH, confidence=0.9, is_directional=False)

    # Path 2 via C: lower confidence
    er.add_edge(na.node_id, nc.node_id, EdgeType.ASSOCIATED_WITH, confidence=0.8, is_directional=False)
    er.add_edge(nc.node_id, nd.node_id, EdgeType.ASSOCIATED_WITH, confidence=0.8, is_directional=False)

    # Repeat search 5 times to ensure 100% determinism selecting path via B
    for _ in range(5):
        res = pe.find_shortest_path("A", "D")
        assert res.path_found is True
        assert res.hop_count == 2
        assert nb.node_id in res.nodes
        assert nc.node_id not in res.nodes
        assert res.path_confidence == 0.9
