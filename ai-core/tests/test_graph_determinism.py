"""
Phase 8 Mandatory 50-Run Bit-for-Bit Determinism Test for NETRA Knowledge Graph.
Executes 50 independent graph pipeline runs on a complex multi-source, multi-entity,
contradictory-evidence scenario with pinned as_of and validates identical SHA-256 hashes.
"""

from datetime import datetime, timezone, timedelta
import hashlib
import json
import pytest

from config import default_config
from graph.graph_engine import KnowledgeGraphEngine
from models.knowledge_graph import EdgeType, NodeType, ProvenanceItem
from models.predictive_intelligence import EpistemicStatus

PINNED_AS_OF = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)


def build_complex_scenario(engine: KnowledgeGraphEngine, as_of: datetime) -> None:
    """Builds a rich multi-dimensional graph scenario."""
    # 1. Entities
    for name in ["ALPHA-01", "BRAVO-02", "CHARLIE-03", "DELTA-04", "ECHO-05"]:
        engine.builder.ingest_entity(
            entity_id=name,
            entity_type="PLATFORM",
            sector_id="SECTOR_NORTH",
            first_observed=as_of - timedelta(hours=4),
            last_observed=as_of,
        )

    na = engine.node_registry.get_node_by_reference("ALPHA-01")
    nb = engine.node_registry.get_node_by_reference("BRAVO-02")
    nc = engine.node_registry.get_node_by_reference("CHARLIE-03")
    nd = engine.node_registry.get_node_by_reference("DELTA-04")
    ne = engine.node_registry.get_node_by_reference("ECHO-05")

    # 2. Competing candidate paths: A-B-D (conf 0.92) vs A-C-D (conf 0.85)
    engine.edge_registry.add_edge(na.node_id, nb.node_id, EdgeType.ASSOCIATED_WITH, confidence=0.92, is_directional=False)
    engine.edge_registry.add_edge(nb.node_id, nd.node_id, EdgeType.ASSOCIATED_WITH, confidence=0.92, is_directional=False)

    engine.edge_registry.add_edge(na.node_id, nc.node_id, EdgeType.ASSOCIATED_WITH, confidence=0.85, is_directional=False)
    engine.edge_registry.add_edge(nc.node_id, nd.node_id, EdgeType.ASSOCIATED_WITH, confidence=0.85, is_directional=False)

    # 3. Contradictory edge D-E
    engine.edge_registry.add_edge(
        nd.node_id,
        ne.node_id,
        EdgeType.ASSOCIATED_WITH,
        strength=0.70,
        confidence=0.60,
        evidence_ids=["RADAR-CORROB-1"],
        contradicting_evidence_ids=["OPTICAL-DISCREPANCY-1"],
        is_directional=False,
    )

    # 4. Ingest Event
    engine.builder.ingest_event(
        event_id="EVT-DET-01",
        event_type="reconnaissance",
        description="Airspace reconnaissance detected",
        timestamp=as_of - timedelta(hours=1),
        entity_id="ALPHA-01",
        sector_id="SECTOR_NORTH",
    )

    # 5. Ingest Anomaly, Risk, Fusion, Forecast
    engine.builder.ingest_anomaly("ANOM-DET-01", "ALPHA-01", 0.84, {"speed": 0.9}, as_of - timedelta(hours=1))
    engine.builder.ingest_risk("RISK-DET-01", "ALPHA-01", 0.76, "HIGH", as_of - timedelta(hours=1), contributing_anomaly_id="ANOM-DET-01")
    engine.builder.ingest_fusion("FUS-DET-01", "ALPHA-01", ["RADAR-1", "OPT-2"], ["OBS-1"], as_of - timedelta(hours=1))
    engine.builder.ingest_forecast("FCST-DET-01", "ALPHA-01", "6H", 0.88, "HIGH_ACTIVITY", ["ANOM-DET-01"], as_of - timedelta(hours=1))


def run_single_iteration(iteration_num: int) -> str:
    """Executes a single graph analysis run and returns SHA-256 hex digest of canonical JSON."""
    engine = KnowledgeGraphEngine(default_config)
    build_complex_scenario(engine, PINNED_AS_OF)

    stats = engine.get_statistics(as_of=PINNED_AS_OF)
    path = engine.shortest_path("ALPHA-01", "DELTA-04", as_of=PINNED_AS_OF)
    cents = engine.centrality()
    comms = engine.communities()
    assessment = engine.assess(as_of=PINNED_AS_OF)
    snap = engine.snapshot(PINNED_AS_OF)

    canonical_payload = {
        "as_of": PINNED_AS_OF.isoformat(),
        "stats": stats.model_dump(),
        "path": path.model_dump(),
        "cents": [c.model_dump() for c in cents],
        "comms": [cm.model_dump() for cm in comms],
        "assessment": assessment.model_dump(),
        "snapshot_id": snap.snapshot_id,
        "nodes": [n.node_id for n in snap.nodes],
        "edges": [e.edge_id for e in snap.edges],
    }

    serialized = json.dumps(canonical_payload, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def test_50_run_determinism():
    """
    Executes 50 consecutive runs of the complete Knowledge Graph analytical pipeline.
    All 50 SHA-256 hashes must be bit-for-bit identical (50/50 passes).
    """
    hashes = []
    for i in range(50):
        h = run_single_iteration(i)
        hashes.append(h)

    unique_hashes = set(hashes)
    assert len(unique_hashes) == 1, f"Determinism failure: found {len(unique_hashes)} distinct hashes: {unique_hashes}"
    assert len(hashes) == 50
    print(f"\n[50-RUN DETERMINISM PASSED]: 50/50 identical runs! SHA-256: {hashes[0]}")
