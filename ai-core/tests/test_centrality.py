"""
Unit tests for NETRA Phase 8 Centrality Engine.
Verifies degree, weighted degree, and betweenness calculations, including bridge entity identification.
"""

from datetime import datetime, timezone
import pytest

from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry
from graph.graph_builder import KnowledgeGraphBuilder
from graph.centrality import CentralityEngine
from models.knowledge_graph import EdgeType


@pytest.fixture
def centrality_setup():
    nr = NodeRegistry()
    er = EdgeRegistry()
    gb = KnowledgeGraphBuilder(nr, er)
    ce = CentralityEngine(nr, er)
    return nr, er, gb, ce


def test_bridge_entity_centrality(centrality_setup):
    nr, er, gb, ce = centrality_setup
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    # Topology: Two clusters {A, B} and {D, E} connected only through bridge C:
    # A - B - C - D - E
    for name in ["A", "B", "C", "D", "E"]:
        gb.ingest_entity(name, first_observed=now)

    nodes = {name: nr.get_node_by_reference(name) for name in ["A", "B", "C", "D", "E"]}

    er.add_edge(nodes["A"].node_id, nodes["B"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)
    er.add_edge(nodes["B"].node_id, nodes["C"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)
    er.add_edge(nodes["C"].node_id, nodes["D"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)
    er.add_edge(nodes["D"].node_id, nodes["E"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)

    results = ce.calculate_centralities()
    res_map = {r.label: r for r in results}

    # C is the central bridge, must have the highest betweenness
    assert res_map["C"].betweenness_centrality > res_map["A"].betweenness_centrality
    assert res_map["C"].betweenness_centrality > res_map["B"].betweenness_centrality
    assert res_map["C"].structural_role in ("BRIDGE", "HUB")
