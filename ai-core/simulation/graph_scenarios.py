"""
Phase 8 Synthetic Operational Scenarios for NETRA Knowledge Graph.
ASTRAVEDA Defence Intelligence Platform - ATUL AI/ML Engineering.

Implements the 18 standardized synthetic operational scenarios (Section 42):
1. Simple Relationship
2. Multi-Hop Network
3. Repeated Association
4. Weak Association
5. Persistent Relationship
6. Stale Relationship
7. Relationship Reactivation
8. Contradictory Relationship Evidence
9. Community Detection
10. Bridge Entity
11. Disconnected Graph
12. Equal Shortest Paths
13. Source Provenance
14. Duplicate Evidence
15. Temporal Network Change
16. Full Intelligence Chain
17. Mixed Epistemic Graph
18. Idempotent Graph Growth
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Dict, List, Optional
from graph.graph_engine import KnowledgeGraphEngine
from models.knowledge_graph import EdgeType, NodeType, ProvenanceItem
from models.predictive_intelligence import EpistemicStatus

BASE_TIME = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)


def load_scenario_1_simple(engine: KnowledgeGraphEngine) -> None:
    """Scenario 1: Simple Relationship between ENTITY-01 and ENTITY-02."""
    engine.builder.ingest_entity("ENTITY-01", sector_id="SECTOR_ALPHA", first_observed=BASE_TIME)
    engine.builder.ingest_entity("ENTITY-02", sector_id="SECTOR_ALPHA", first_observed=BASE_TIME, associated_entity_ids=["ENTITY-01"])


def load_scenario_2_multihop(engine: KnowledgeGraphEngine) -> None:
    """Scenario 2: Multi-Hop Network A -> B -> C -> D."""
    for name in ["ENTITY-A", "ENTITY-B", "ENTITY-C", "ENTITY-D"]:
        engine.builder.ingest_entity(name, first_observed=BASE_TIME)
    na = engine.node_registry.get_node_by_reference("ENTITY-A")
    nb = engine.node_registry.get_node_by_reference("ENTITY-B")
    nc = engine.node_registry.get_node_by_reference("ENTITY-C")
    nd = engine.node_registry.get_node_by_reference("ENTITY-D")
    engine.edge_registry.add_edge(na.node_id, nb.node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)
    engine.edge_registry.add_edge(nb.node_id, nc.node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)
    engine.edge_registry.add_edge(nc.node_id, nd.node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)


def load_scenario_3_repeated(engine: KnowledgeGraphEngine) -> None:
    """Scenario 3: Repeated Association strengthening link over time."""
    engine.builder.ingest_entity("PATROL-01", first_observed=BASE_TIME - timedelta(hours=6), last_observed=BASE_TIME)
    engine.builder.ingest_entity("PATROL-02", first_observed=BASE_TIME - timedelta(hours=6), last_observed=BASE_TIME)
    na = engine.node_registry.get_node_by_reference("PATROL-01")
    nb = engine.node_registry.get_node_by_reference("PATROL-02")
    engine.edge_registry.add_edge(
        na.node_id,
        nb.node_id,
        EdgeType.ASSOCIATED_WITH,
        strength=0.90,
        confidence=0.95,
        evidence_ids=["EVT-101", "EVT-102", "EVT-103", "EVT-104", "EVT-105"],
        supporting_sources=["RADAR-01", "OPT-02"],
        first_observed_at=BASE_TIME - timedelta(hours=6),
        last_observed_at=BASE_TIME,
        is_directional=False,
    )


def load_scenario_4_weak(engine: KnowledgeGraphEngine) -> None:
    """Scenario 4: Weak Association."""
    engine.builder.ingest_entity("TARGET-01", first_observed=BASE_TIME)
    engine.builder.ingest_entity("TARGET-02", first_observed=BASE_TIME)
    na = engine.node_registry.get_node_by_reference("TARGET-01")
    nb = engine.node_registry.get_node_by_reference("TARGET-02")
    engine.edge_registry.add_edge(
        na.node_id,
        nb.node_id,
        EdgeType.ASSOCIATED_WITH,
        strength=0.20,
        confidence=0.35,
        evidence_ids=["SIG-WEAK-01"],
        first_observed_at=BASE_TIME,
        last_observed_at=BASE_TIME,
        is_directional=False,
    )


def load_scenario_5_persistent(engine: KnowledgeGraphEngine) -> None:
    """Scenario 5: Persistent Relationship."""
    t_start = BASE_TIME - timedelta(hours=48)
    engine.builder.ingest_entity("HQ-BASE", first_observed=t_start, last_observed=BASE_TIME)
    engine.builder.ingest_entity("OUTPOST-ALPHA", first_observed=t_start, last_observed=BASE_TIME)
    na = engine.node_registry.get_node_by_reference("HQ-BASE")
    nb = engine.node_registry.get_node_by_reference("OUTPOST-ALPHA")
    engine.edge_registry.add_edge(
        na.node_id,
        nb.node_id,
        EdgeType.ASSOCIATED_WITH,
        strength=0.88,
        confidence=0.92,
        evidence_ids=["EVT-P1", "EVT-P2", "EVT-P3", "EVT-P4"],
        supporting_sources=["TELEMETRY-HQ", "COMMS-RELAY"],
        first_observed_at=t_start,
        last_observed_at=BASE_TIME,
        is_directional=False,
    )


def load_scenario_6_stale(engine: KnowledgeGraphEngine) -> None:
    """Scenario 6: Stale Relationship (no activity for > 24 hours)."""
    t_old = BASE_TIME - timedelta(hours=40)
    engine.builder.ingest_entity("CONVOY-A", first_observed=t_old, last_observed=t_old)
    engine.builder.ingest_entity("CONVOY-B", first_observed=t_old, last_observed=t_old)
    na = engine.node_registry.get_node_by_reference("CONVOY-A")
    nb = engine.node_registry.get_node_by_reference("CONVOY-B")
    engine.edge_registry.add_edge(
        na.node_id,
        nb.node_id,
        EdgeType.ASSOCIATED_WITH,
        strength=0.60,
        evidence_ids=["EVT-OLD-1"],
        first_observed_at=t_old,
        last_observed_at=t_old,
        is_directional=False,
    )


def load_scenario_7_reactivation(engine: KnowledgeGraphEngine) -> None:
    """Scenario 7: Relationship Reactivation."""
    # Seed as stale first, then new observation at BASE_TIME
    t_dormant = BASE_TIME - timedelta(hours=36)
    engine.builder.ingest_entity("AGENT-01", first_observed=t_dormant, last_observed=BASE_TIME)
    engine.builder.ingest_entity("AGENT-02", first_observed=t_dormant, last_observed=BASE_TIME)
    na = engine.node_registry.get_node_by_reference("AGENT-01")
    nb = engine.node_registry.get_node_by_reference("AGENT-02")
    engine.edge_registry.add_edge(
        na.node_id,
        nb.node_id,
        EdgeType.ASSOCIATED_WITH,
        strength=0.85,
        evidence_ids=["EVT-OLD-REL", "EVT-NEW-PULSE"],
        first_observed_at=t_dormant,
        last_observed_at=BASE_TIME,
        is_directional=False,
    )


def load_scenario_8_contradictory(engine: KnowledgeGraphEngine) -> None:
    """Scenario 8: Contradictory Relationship Evidence."""
    engine.builder.ingest_entity("VESSEL-A", first_observed=BASE_TIME)
    engine.builder.ingest_entity("VESSEL-B", first_observed=BASE_TIME)
    na = engine.node_registry.get_node_by_reference("VESSEL-A")
    nb = engine.node_registry.get_node_by_reference("VESSEL-B")
    engine.edge_registry.add_edge(
        na.node_id,
        nb.node_id,
        EdgeType.ASSOCIATED_WITH,
        strength=0.65,
        confidence=0.50,
        evidence_ids=["AIS-TRACK-MATCH"],
        supporting_sources=["AIS-RECEIVER"],
        contradicting_evidence_ids=["RADAR-POSITION-DISCREPANCY"],
        first_observed_at=BASE_TIME,
        last_observed_at=BASE_TIME,
        is_directional=False,
    )


def load_scenario_9_community(engine: KnowledgeGraphEngine) -> None:
    """Scenario 9: Community Detection (two disjoint groups: A-B-C-D and E-F-G)."""
    # Group 1
    for name in ["UAV-1", "UAV-2", "UAV-3", "UAV-4"]:
        engine.builder.ingest_entity(name, first_observed=BASE_TIME)
    g1 = [engine.node_registry.get_node_by_reference(n) for n in ["UAV-1", "UAV-2", "UAV-3", "UAV-4"]]
    for i in range(len(g1)):
        for j in range(i + 1, len(g1)):
            engine.edge_registry.add_edge(g1[i].node_id, g1[j].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)

    # Group 2
    for name in ["RADAR-E", "RADAR-F", "RADAR-G"]:
        engine.builder.ingest_entity(name, first_observed=BASE_TIME)
    g2 = [engine.node_registry.get_node_by_reference(n) for n in ["RADAR-E", "RADAR-F", "RADAR-G"]]
    for i in range(len(g2)):
        for j in range(i + 1, len(g2)):
            engine.edge_registry.add_edge(g2[i].node_id, g2[j].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)


def load_scenario_10_bridge(engine: KnowledgeGraphEngine) -> None:
    """Scenario 10: Bridge Entity connecting two separate clusters."""
    for name in ["COMM1-A", "COMM1-B", "BRIDGE-NODE", "COMM2-X", "COMM2-Y"]:
        engine.builder.ingest_entity(name, first_observed=BASE_TIME)
    nodes = {n: engine.node_registry.get_node_by_reference(n) for n in ["COMM1-A", "COMM1-B", "BRIDGE-NODE", "COMM2-X", "COMM2-Y"]}
    engine.edge_registry.add_edge(nodes["COMM1-A"].node_id, nodes["COMM1-B"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)
    engine.edge_registry.add_edge(nodes["COMM1-B"].node_id, nodes["BRIDGE-NODE"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)
    engine.edge_registry.add_edge(nodes["BRIDGE-NODE"].node_id, nodes["COMM2-X"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)
    engine.edge_registry.add_edge(nodes["COMM2-X"].node_id, nodes["COMM2-Y"].node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)


def load_scenario_11_disconnected(engine: KnowledgeGraphEngine) -> None:
    """Scenario 11: Disconnected Graph with no path."""
    engine.builder.ingest_entity("ISOLATED-01", first_observed=BASE_TIME)
    engine.builder.ingest_entity("ISOLATED-02", first_observed=BASE_TIME)


def load_scenario_12_equal_paths(engine: KnowledgeGraphEngine) -> None:
    """Scenario 12: Equal Shortest Paths testing deterministic tie-breaking."""
    for name in ["START-NODE", "ROUTE-A", "ROUTE-B", "GOAL-NODE"]:
        engine.builder.ingest_entity(name, first_observed=BASE_TIME)
    nodes = {n: engine.node_registry.get_node_by_reference(n) for n in ["START-NODE", "ROUTE-A", "ROUTE-B", "GOAL-NODE"]}
    # Route A (confidence 0.95)
    engine.edge_registry.add_edge(nodes["START-NODE"].node_id, nodes["ROUTE-A"].node_id, EdgeType.ASSOCIATED_WITH, confidence=0.95, is_directional=False)
    engine.edge_registry.add_edge(nodes["ROUTE-A"].node_id, nodes["GOAL-NODE"].node_id, EdgeType.ASSOCIATED_WITH, confidence=0.95, is_directional=False)
    # Route B (confidence 0.80)
    engine.edge_registry.add_edge(nodes["START-NODE"].node_id, nodes["ROUTE-B"].node_id, EdgeType.ASSOCIATED_WITH, confidence=0.80, is_directional=False)
    engine.edge_registry.add_edge(nodes["ROUTE-B"].node_id, nodes["GOAL-NODE"].node_id, EdgeType.ASSOCIATED_WITH, confidence=0.80, is_directional=False)


def load_scenario_13_provenance(engine: KnowledgeGraphEngine) -> None:
    """Scenario 13: Multi-Source Provenance (RADAR + OPTICAL + TELEMETRY)."""
    engine.builder.ingest_fusion(
        fusion_id="FUS-MULTI-INT-01",
        entity_id="SURVEILLANCE-TRACK-01",
        source_ids=["RADAR-GROUND-1", "OPTICAL-POD-2", "TELEMETRY-LINK-3"],
        raw_observation_ids=["OBS-RADAR-10", "OBS-OPT-20", "OBS-TEL-30"],
        timestamp=BASE_TIME,
    )


def load_scenario_14_duplicate_evidence(engine: KnowledgeGraphEngine) -> None:
    """Scenario 14: Duplicate Evidence ingestion causing zero inflation."""
    for _ in range(3):
        engine.builder.ingest_event("EVT-DUP-01", "sensor_ping", "Duplicate ping", BASE_TIME, entity_id="UAV-DUP")


def load_scenario_15_temporal_change(engine: KnowledgeGraphEngine) -> None:
    """Scenario 15: Temporal Network Change."""
    t1 = BASE_TIME - timedelta(hours=4)
    t2 = BASE_TIME
    engine.builder.ingest_entity("UNIT-1", first_observed=t1, last_observed=t2)
    engine.builder.ingest_entity("UNIT-2", first_observed=t1, last_observed=t2)
    engine.builder.ingest_entity("UNIT-3", first_observed=t2, last_observed=t2)
    n1 = engine.node_registry.get_node_by_reference("UNIT-1")
    n2 = engine.node_registry.get_node_by_reference("UNIT-2")
    n3 = engine.node_registry.get_node_by_reference("UNIT-3")
    # At t1: UNIT-1 - UNIT-2
    engine.edge_registry.add_edge(n1.node_id, n2.node_id, EdgeType.ASSOCIATED_WITH, valid_from=t1, is_directional=False)
    # At t2: UNIT-2 - UNIT-3 added
    engine.edge_registry.add_edge(n2.node_id, n3.node_id, EdgeType.ASSOCIATED_WITH, valid_from=t2, is_directional=False)


def load_scenario_16_full_chain(engine: KnowledgeGraphEngine) -> None:
    """Scenario 16: Full Intelligence Chain (Source -> Obs -> Entity -> Event -> Anomaly -> Risk -> Forecast)."""
    # 1. Fusion + Sources
    engine.builder.ingest_fusion("FUS-CHAIN-01", "TRACK-CHAIN-01", ["SRC-RADAR-1"], ["OBS-01"], BASE_TIME)
    # 2. Event
    engine.builder.ingest_event("EVT-CHAIN-01", "airspace_incursion", "Border proximity", BASE_TIME, entity_id="TRACK-CHAIN-01")
    # 3. Anomaly
    engine.builder.ingest_anomaly("ANOM-CHAIN-01", "TRACK-CHAIN-01", 0.85, {"speed_deviation": 0.9}, BASE_TIME)
    # 4. Risk
    engine.builder.ingest_risk("RISK-CHAIN-01", "TRACK-CHAIN-01", 0.79, "HIGH", BASE_TIME, contributing_anomaly_id="ANOM-CHAIN-01")
    # 5. Forecast
    engine.builder.ingest_forecast("FCST-CHAIN-01", "TRACK-CHAIN-01", "6H", 0.82, "ESCALATING", ["ANOM-CHAIN-01", "RISK-CHAIN-01"], BASE_TIME)


def load_scenario_17_mixed_epistemic(engine: KnowledgeGraphEngine) -> None:
    """Scenario 17: Mixed Epistemic Graph validating strict 5-tier separation."""
    load_scenario_16_full_chain(engine)
    # Add an uncertain conflicting source
    n_fused = engine.node_registry.get_node_by_reference("FUS-CHAIN-01")
    n_conf_src = engine.node_registry.add_node(NodeType.SOURCE, "CONFLICT-SRC", "CONFLICT-SRC", BASE_TIME)
    engine.edge_registry.add_edge(
        n_conf_src.node_id,
        n_fused.node_id,
        EdgeType.CONTRADICTS,
        epistemic_status=EpistemicStatus.UNCERTAIN,
        contradicting_evidence_ids=["CONF-REP-99"],
        is_directional=True,
    )


def load_scenario_18_idempotent(engine: KnowledgeGraphEngine) -> None:
    """Scenario 18: Idempotent Graph Growth."""
    load_scenario_16_full_chain(engine)
    # Ingest again
    load_scenario_16_full_chain(engine)


SCENARIO_REGISTRY: Dict[str, Dict[str, Any]] = {
    "SCENARIO-01-SIMPLE-RELATIONSHIP": {
        "scenario_id": "SCENARIO-01-SIMPLE-RELATIONSHIP",
        "title": "Simple Entity-to-Entity Association",
        "loader": load_scenario_1_simple,
        "as_of": BASE_TIME,
    },
    "SCENARIO-02-MULTI-HOP-NETWORK": {
        "scenario_id": "SCENARIO-02-MULTI-HOP-NETWORK",
        "title": "Multi-Hop Traversal Network",
        "loader": load_scenario_2_multihop,
        "as_of": BASE_TIME,
    },
    "SCENARIO-03-REPEATED-ASSOCIATION": {
        "scenario_id": "SCENARIO-03-REPEATED-ASSOCIATION",
        "title": "Repeated High-Frequency Association",
        "loader": load_scenario_3_repeated,
        "as_of": BASE_TIME,
    },
    "SCENARIO-04-WEAK-ASSOCIATION": {
        "scenario_id": "SCENARIO-04-WEAK-ASSOCIATION",
        "title": "Weak Low-Confidence Association",
        "loader": load_scenario_4_weak,
        "as_of": BASE_TIME,
    },
    "SCENARIO-05-PERSISTENT-RELATIONSHIP": {
        "scenario_id": "SCENARIO-05-PERSISTENT-RELATIONSHIP",
        "title": "Persistent Multi-Window Relationship",
        "loader": load_scenario_5_persistent,
        "as_of": BASE_TIME,
    },
    "SCENARIO-06-STALE-RELATIONSHIP": {
        "scenario_id": "SCENARIO-06-STALE-RELATIONSHIP",
        "title": "Stale Inactive Relationship",
        "loader": load_scenario_6_stale,
        "as_of": BASE_TIME,
    },
    "SCENARIO-07-REACTIVATION": {
        "scenario_id": "SCENARIO-07-REACTIVATION",
        "title": "Dormant Relationship Reactivation",
        "loader": load_scenario_7_reactivation,
        "as_of": BASE_TIME,
    },
    "SCENARIO-08-CONTRADICTORY-EVIDENCE": {
        "scenario_id": "SCENARIO-08-CONTRADICTORY-EVIDENCE",
        "title": "Contradictory Sensor Evidence Preservation",
        "loader": load_scenario_8_contradictory,
        "as_of": BASE_TIME,
    },
    "SCENARIO-09-COMMUNITY-DETECTION": {
        "scenario_id": "SCENARIO-09-COMMUNITY-DETECTION",
        "title": "Disjoint Community Partitioning",
        "loader": load_scenario_9_community,
        "as_of": BASE_TIME,
    },
    "SCENARIO-10-BRIDGE-ENTITY": {
        "scenario_id": "SCENARIO-10-BRIDGE-ENTITY",
        "title": "Structural Bridge Identification",
        "loader": load_scenario_10_bridge,
        "as_of": BASE_TIME,
    },
    "SCENARIO-11-DISCONNECTED-GRAPH": {
        "scenario_id": "SCENARIO-11-DISCONNECTED-GRAPH",
        "title": "Disconnected Entities with Zero Path",
        "loader": load_scenario_11_disconnected,
        "as_of": BASE_TIME,
    },
    "SCENARIO-12-EQUAL-SHORTEST-PATHS": {
        "scenario_id": "SCENARIO-12-EQUAL-SHORTEST-PATHS",
        "title": "Equal Hop Shortest Path Tie-Breaking",
        "loader": load_scenario_12_equal_paths,
        "as_of": BASE_TIME,
    },
    "SCENARIO-13-SOURCE-PROVENANCE": {
        "scenario_id": "SCENARIO-13-SOURCE-PROVENANCE",
        "title": "Multi-INT Source Provenance",
        "loader": load_scenario_13_provenance,
        "as_of": BASE_TIME,
    },
    "SCENARIO-14-DUPLICATE-EVIDENCE": {
        "scenario_id": "SCENARIO-14-DUPLICATE-EVIDENCE",
        "title": "Duplicate Evidence Zero Growth",
        "loader": load_scenario_14_duplicate_evidence,
        "as_of": BASE_TIME,
    },
    "SCENARIO-15-TEMPORAL-NETWORK-CHANGE": {
        "scenario_id": "SCENARIO-15-TEMPORAL-NETWORK-CHANGE",
        "title": "Temporal Network Structure Evolution",
        "loader": load_scenario_15_temporal_change,
        "as_of": BASE_TIME,
    },
    "SCENARIO-16-FULL-INTELLIGENCE-CHAIN": {
        "scenario_id": "SCENARIO-16-FULL-INTELLIGENCE-CHAIN",
        "title": "Full P1-P6 Intelligence Lineage Chain",
        "loader": load_scenario_16_full_chain,
        "as_of": BASE_TIME,
    },
    "SCENARIO-17-MIXED-EPISTEMIC-GRAPH": {
        "scenario_id": "SCENARIO-17-MIXED-EPISTEMIC-GRAPH",
        "title": "Strict 5-Tier Epistemic Ledger Segregation",
        "loader": load_scenario_17_mixed_epistemic,
        "as_of": BASE_TIME,
    },
    "SCENARIO-18-IDEMPOTENT-GROWTH": {
        "scenario_id": "SCENARIO-18-IDEMPOTENT-GROWTH",
        "title": "Deterministic Idempotent Ingestion",
        "loader": load_scenario_18_idempotent,
        "as_of": BASE_TIME,
    },
}


def list_all_graph_scenarios() -> List[Dict[str, Any]]:
    """Lists metadata for all registered Phase 8 scenarios."""
    return [
        {
            "scenario_id": s["scenario_id"],
            "title": s["title"],
        }
        for s in SCENARIO_REGISTRY.values()
    ]


def load_graph_scenario(scenario_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves scenario loader by ID."""
    return SCENARIO_REGISTRY.get(scenario_id)
