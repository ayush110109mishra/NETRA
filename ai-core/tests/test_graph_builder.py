"""
Unit tests for NETRA Phase 8 Knowledge Graph Builder.
Verifies cross-phase ingestion (P1-P7), edge creation, idempotency, and reference integrity.
"""

from datetime import datetime, timezone
import pytest

from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry
from graph.graph_builder import KnowledgeGraphBuilder
from graph.provenance import ProvenanceEngine
from models.knowledge_graph import EdgeType, NodeType
from models.predictive_intelligence import EpistemicStatus


@pytest.fixture
def builder():
    nr = NodeRegistry()
    er = EdgeRegistry()
    return KnowledgeGraphBuilder(nr, er), nr, er


def test_builder_entity_and_event_ingestion(builder):
    gb, nr, er = builder
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    # Ingest entity
    ent_node = gb.ingest_entity(
        entity_id="ENTITY-01",
        entity_type="SURVEILLANCE_UAV",
        sector_id="SECTOR_ALPHA",
        first_observed=now,
    )
    assert ent_node.node_type == NodeType.ENTITY
    assert nr.count() == 2  # ENTITY + SECTOR
    assert er.count() == 1  # LOCATED_IN

    # Ingest event
    ev_node = gb.ingest_event(
        event_id="EVT-100",
        event_type="radar_lock",
        description="Radar illumination detected",
        timestamp=now,
        entity_id="ENTITY-01",
        sector_id="SECTOR_ALPHA",
    )
    assert ev_node.node_type == NodeType.EVENT
    assert nr.count() == 3  # ENTITY, SECTOR, EVENT
    assert er.count() == 3  # ENTITY->SECTOR, ENTITY->EVENT (GENERATED), EVENT->SECTOR (LOCATED_IN)


def test_builder_full_lineage_ingestion(builder):
    gb, nr, er = builder
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)

    # Full chain: Source -> Fusion -> Entity -> Anomaly -> Risk -> Forecast
    gb.ingest_fusion(
        fusion_id="FUS-01",
        entity_id="ENTITY-01",
        source_ids=["RADAR-A", "OPT-B"],
        raw_observation_ids=["OBS-1", "OBS-2"],
        timestamp=now,
    )
    gb.ingest_anomaly(
        anomaly_id="ANOM-01",
        entity_id="ENTITY-01",
        anomaly_score=0.82,
        timestamp=now,
    )
    gb.ingest_risk(
        risk_id="RISK-01",
        entity_id="ENTITY-01",
        risk_score=0.78,
        contributing_anomaly_id="ANOM-01",
        timestamp=now,
    )
    gb.ingest_forecast(
        forecast_id="FCST-01",
        entity_id="ENTITY-01",
        horizon="6H",
        probability=0.85,
        predicted_state="ELEVATED_ACTIVITY",
        timestamp=now,
    )

    validator = ProvenanceEngine(nr, er)
    val_report = validator.validate_graph()
    assert val_report["is_valid"] is True
    assert len(val_report["orphan_edges"]) == 0


def test_builder_idempotency(builder):
    gb, nr, er = builder
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)

    # Ingest entity and event twice
    for _ in range(2):
        gb.ingest_entity("ENTITY-01", sector_id="SECTOR_ALPHA", first_observed=now)
        gb.ingest_event("EVT-01", "movement", "Moving north", now, entity_id="ENTITY-01", sector_id="SECTOR_ALPHA")

    assert nr.count() == 3  # ENTITY, SECTOR, EVENT (not doubled!)
    assert er.count() == 3  # LOCATED_IN (2), GENERATED (1) (not doubled!)
