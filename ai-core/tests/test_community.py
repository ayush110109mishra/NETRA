"""
Unit tests for NETRA Phase 8 Community Engine.
Verifies deterministic community detection, density, and connected components.
"""

from datetime import datetime, timezone
import pytest

from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry
from graph.graph_builder import KnowledgeGraphBuilder
from graph.community import CommunityEngine
from models.knowledge_graph import EdgeType


@pytest.fixture
def community_setup():
    nr = NodeRegistry()
    er = EdgeRegistry()
    gb = KnowledgeGraphBuilder(nr, er)
    comm_eng = CommunityEngine(nr, er)
    return nr, er, gb, comm_eng


def test_disjoint_communities(community_setup):
    nr, er, gb, comm_eng = community_setup
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    # Community 1: A-B-C
    for name in ["A", "B", "C"]:
        gb.ingest_entity(name, first_observed=now)
    nodes1 = {name: nr.get_node_by_reference(name) for name in ["A", "B", "C"]}
    er.add_edge(nodes1["A"].node_id, nodes1["B"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)
    er.add_edge(nodes1["B"].node_id, nodes1["C"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)
    er.add_edge(nodes1["A"].node_id, nodes1["C"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)

    # Community 2: X-Y
    for name in ["X", "Y"]:
        gb.ingest_entity(name, first_observed=now)
    nodes2 = {name: nr.get_node_by_reference(name) for name in ["X", "Y"]}
    er.add_edge(nodes2["X"].node_id, nodes2["Y"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)

    comms = comm_eng.detect_communities()
    assert len(comms) == 2

    # Verify members
    member_sets = [set(c.member_entities) for c in comms]
    assert {"A", "B", "C"} in member_sets
    assert {"X", "Y"} in member_sets
