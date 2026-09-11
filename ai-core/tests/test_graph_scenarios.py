"""
Unit and integration tests for all 18 NETRA Phase 8 Synthetic Scenarios.
"""

from datetime import datetime, timezone, timedelta
import pytest

from config import default_config
from graph.graph_engine import KnowledgeGraphEngine
from simulation.graph_scenarios import (
    SCENARIO_REGISTRY,
    load_graph_scenario,
    list_all_graph_scenarios,
)
from models.knowledge_graph import RelationshipStatus, RelationshipChangeType


@pytest.fixture
def engine():
    return KnowledgeGraphEngine(default_config)


def test_scenario_catalog():
    scenarios = list_all_graph_scenarios()
    assert len(scenarios) == 18


@pytest.mark.parametrize("scenario_id", list(SCENARIO_REGISTRY.keys()))
def test_all_18_scenarios_execute(engine, scenario_id):
    scenario = load_graph_scenario(scenario_id)
    assert scenario is not None

    engine.clear()
    scenario["loader"](engine)
    as_of = scenario["as_of"]

    # Verify basic invariants across every scenario
    stats = engine.get_statistics(as_of=as_of)
    assert stats.node_count > 0

    validation = engine.provenance.validate_graph()
    assert validation["is_valid"] is True, f"Graph validation failed on {scenario_id}: {validation}"


def test_scenario_09_community_detection(engine):
    engine.clear()
    load_graph_scenario("SCENARIO-09-COMMUNITY-DETECTION")["loader"](engine)
    comms = engine.communities()
    assert len(comms) == 2


def test_scenario_10_bridge_entity(engine):
    engine.clear()
    load_graph_scenario("SCENARIO-10-BRIDGE-ENTITY")["loader"](engine)
    cents = engine.centrality()
    bridge_node = next(c for c in cents if c.label == "BRIDGE-NODE")
    assert bridge_node.structural_role in ("BRIDGE", "HUB")
    assert bridge_node.betweenness_centrality > 0.10


def test_scenario_11_disconnected(engine):
    engine.clear()
    load_graph_scenario("SCENARIO-11-DISCONNECTED-GRAPH")["loader"](engine)
    path = engine.shortest_path("ISOLATED-01", "ISOLATED-02")
    assert path.path_found is False


def test_scenario_12_equal_shortest_paths(engine):
    engine.clear()
    load_graph_scenario("SCENARIO-12-EQUAL-SHORTEST-PATHS")["loader"](engine)
    path = engine.shortest_path("START-NODE", "GOAL-NODE")
    assert path.path_found is True
    assert path.hop_count == 2
    # Route A has higher confidence (0.95 vs 0.80), must be selected by tie-break
    node_a = engine.node_registry.get_node_by_reference("ROUTE-A")
    assert node_a.node_id in path.nodes


def test_scenario_14_duplicate_evidence_idempotency(engine):
    engine.clear()
    load_graph_scenario("SCENARIO-14-DUPLICATE-EVIDENCE")["loader"](engine)
    stats = engine.get_statistics()
    # UAV-DUP + EVENT = 2 nodes, 1 edge (not 6 nodes!)
    assert stats.node_count == 2
    assert stats.event_count == 1
    assert stats.edge_count == 1


def test_scenario_18_idempotent_growth(engine):
    engine.clear()
    load_graph_scenario("SCENARIO-18-IDEMPOTENT-GROWTH")["loader"](engine)
    stats = engine.get_statistics()
    node_count_after_first = stats.node_count
    edge_count_after_first = stats.edge_count

    # Load again
    load_graph_scenario("SCENARIO-18-IDEMPOTENT-GROWTH")["loader"](engine)
    stats_after_second = engine.get_statistics()

    assert stats_after_second.node_count == node_count_after_first
    assert stats_after_second.edge_count == edge_count_after_first
