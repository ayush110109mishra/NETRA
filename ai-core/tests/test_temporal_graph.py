"""
Unit tests for NETRA Phase 8 Temporal Graph Engine.
Verifies point-in-time snapshots, deterministic snapshot IDs, and active node/edge filtering.
"""

from datetime import datetime, timezone, timedelta
import pytest

from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry
from graph.temporal_graph import TemporalGraphEngine
from models.knowledge_graph import EdgeType, NodeType


@pytest.fixture
def registries():
    nr = NodeRegistry()
    er = EdgeRegistry()
    return nr, er


def test_deterministic_snapshot_id(registries):
    nr, er = registries
    engine = TemporalGraphEngine(nr, er)
    t = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)

    na = nr.add_node(NodeType.ENTITY, "A", "A", t)
    nb = nr.add_node(NodeType.ENTITY, "B", "B", t)
    er.add_edge(na.node_id, nb.node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)

    snap1 = engine.get_snapshot(t)
    # Clear cache and recompute
    engine._snapshot_cache.clear()
    snap2 = engine.get_snapshot(t)

    assert snap1.snapshot_id == snap2.snapshot_id
    assert snap1.node_count == 2
    assert snap1.edge_count == 1


def test_temporal_snapshot_filtering(registries):
    nr, er = registries
    engine = TemporalGraphEngine(nr, er)

    t1 = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 9, 12, 14, 0, 0, tzinfo=timezone.utc)
    t3 = datetime(2026, 9, 12, 18, 0, 0, tzinfo=timezone.utc)

    na = nr.add_node(NodeType.ENTITY, "A", "A", t1, valid_from=t1, valid_to=t3)
    nb = nr.add_node(NodeType.ENTITY, "B", "B", t1, valid_from=t1, valid_to=t2)  # Expires at t2

    er.add_edge(na.node_id, nb.node_id, EdgeType.ASSOCIATED_WITH, valid_from=t1, valid_to=t2, is_directional=False)

    # At 12:00, both A and B are active
    snap_noon = engine.get_snapshot(datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc))
    assert snap_noon.node_count == 2
    assert snap_noon.edge_count == 1

    # At 16:00, B has expired, so edge AB is also inactive
    snap_4pm = engine.get_snapshot(datetime(2026, 9, 12, 16, 0, 0, tzinfo=timezone.utc))
    assert snap_4pm.node_count == 1
    assert snap_4pm.nodes[0].label == "A"
    assert snap_4pm.edge_count == 0
