"""
Unit tests for NETRA Phase 8 KnowledgeGraphEngine.
Verifies statistics generation, 5-tier epistemic assessments, ego-networks, and snapshots.
"""

from datetime import datetime, timezone
import pytest

from config import default_config
from graph.graph_engine import KnowledgeGraphEngine
from models.knowledge_graph import NodeType


@pytest.fixture
def graph_engine():
    return KnowledgeGraphEngine(default_config)


def test_graph_engine_lifecycle_and_statistics(graph_engine):
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    # Ingest entities and events
    graph_engine.builder.ingest_entity("ENTITY-01", sector_id="SECTOR_ALPHA", first_observed=now)
    graph_engine.builder.ingest_entity("ENTITY-02", sector_id="SECTOR_ALPHA", first_observed=now, associated_entity_ids=["ENTITY-01"])
    graph_engine.builder.ingest_event("EVT-10", "patrol", "Routine patrol", now, entity_id="ENTITY-01", sector_id="SECTOR_ALPHA")

    stats = graph_engine.get_statistics()
    assert stats.entity_count == 2
    assert stats.event_count == 1
    assert stats.edge_count >= 2

    # Assess
    assessment = graph_engine.assess()
    assert len(assessment.observed) >= 2
    assert "knowledge graph tracks 2 entities" in assessment.summary.lower()


def test_graph_engine_entity_network(graph_engine):
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    graph_engine.builder.ingest_entity("UAV-1", associated_entity_ids=["COMMAND-POST"], first_observed=now)
    graph_engine.builder.ingest_entity("UAV-2", associated_entity_ids=["COMMAND-POST"], first_observed=now)

    network = graph_engine.entity_network("COMMAND-POST", depth=1, as_of=now)
    assert network["focus_entity"] == "COMMAND-POST"
    assert network["network_statistics"]["neighbor_entity_count"] == 2
    assert len(network["relationships"]) == 2
