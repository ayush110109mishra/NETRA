"""
Unit tests for NETRA Phase 8 Relationship Intelligence & Change Detection.
Verifies scoring attribution, lifecycle status, contradiction handling, and temporal delta detection.
"""

from datetime import datetime, timezone, timedelta
import pytest

from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry
from graph.graph_builder import KnowledgeGraphBuilder
from graph.relationship_intelligence import RelationshipIntelligenceEngine
from graph.relationship_change import RelationshipChangeEngine
from models.knowledge_graph import EdgeType, RelationshipChangeType, RelationshipStatus


@pytest.fixture
def graph_setup():
    nr = NodeRegistry()
    er = EdgeRegistry()
    gb = KnowledgeGraphBuilder(nr, er)
    rel_eng = RelationshipIntelligenceEngine(nr, er)
    change_eng = RelationshipChangeEngine(rel_eng)
    return nr, er, gb, rel_eng, change_eng


def test_relationship_evaluation_and_why(graph_setup):
    nr, er, gb, rel_eng, change_eng = graph_setup
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)

    gb.ingest_entity("ENTITY-01", first_observed=now - timedelta(hours=3), last_observed=now)
    gb.ingest_entity("ENTITY-02", first_observed=now - timedelta(hours=3), last_observed=now)

    na = nr.get_node_by_reference("ENTITY-01")
    nb = nr.get_node_by_reference("ENTITY-02")

    # Add association edge with 3 evidence items
    er.add_edge(
        source_node_id=na.node_id,
        target_node_id=nb.node_id,
        edge_type=EdgeType.ASSOCIATED_WITH,
        strength=0.80,
        confidence=0.90,
        evidence_ids=["EVT-01", "EVT-02", "EVT-03"],
        supporting_sources=["RADAR-A", "OPT-B"],
        first_observed_at=now - timedelta(hours=3),
        last_observed_at=now,
        is_directional=False,
    )

    detail = rel_eng.evaluate_relationship("ENTITY-01", "ENTITY-02", as_of=now)
    assert detail is not None
    assert detail.strength > 0.50
    assert detail.status in (RelationshipStatus.ACTIVE, RelationshipStatus.PERSISTENT)
    assert detail.is_disputed is False
    assert len(detail.why) >= 2


def test_contradiction_handling_in_scoring(graph_setup):
    nr, er, gb, rel_eng, change_eng = graph_setup
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)

    gb.ingest_entity("ENTITY-A", first_observed=now, last_observed=now)
    gb.ingest_entity("ENTITY-B", first_observed=now, last_observed=now)
    na = nr.get_node_by_reference("ENTITY-A")
    nb = nr.get_node_by_reference("ENTITY-B")

    # Add edge with contradictions
    er.add_edge(
        source_node_id=na.node_id,
        target_node_id=nb.node_id,
        edge_type=EdgeType.ASSOCIATED_WITH,
        strength=0.75,
        evidence_ids=["EVT-01"],
        contradicting_evidence_ids=["CONFLICT-01"],
        first_observed_at=now,
        last_observed_at=now,
        is_directional=False,
    )

    detail = rel_eng.evaluate_relationship("ENTITY-A", "ENTITY-B", as_of=now)
    assert detail is not None
    assert detail.is_disputed is True
    assert detail.status == RelationshipStatus.DISPUTED
    assert "CONFLICT-01" in detail.contradicting_evidence


def test_relationship_change_detection(graph_setup):
    nr, er, gb, rel_eng, change_eng = graph_setup
    t1 = datetime(2026, 9, 12, 8, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)

    gb.ingest_entity("ENTITY-1", first_observed=t1, last_observed=t1)
    gb.ingest_entity("ENTITY-2", first_observed=t1, last_observed=t1)
    na = nr.get_node_by_reference("ENTITY-1")
    nb = nr.get_node_by_reference("ENTITY-2")

    # At t1: initial edge
    er.add_edge(
        source_node_id=na.node_id,
        target_node_id=nb.node_id,
        edge_type=EdgeType.ASSOCIATED_WITH,
        strength=0.30,
        evidence_ids=["EVT-1"],
        first_observed_at=t1,
        last_observed_at=t1,
        is_directional=False,
    )

    # Fast forward: at t2 more evidence added, strengthening relationship
    er.add_edge(
        source_node_id=na.node_id,
        target_node_id=nb.node_id,
        edge_type=EdgeType.ASSOCIATED_WITH,
        strength=0.85,
        evidence_ids=["EVT-2", "EVT-3", "EVT-4"],
        first_observed_at=t1,
        last_observed_at=t2,
        is_directional=False,
    )

    changes = change_eng.detect_changes(t1=t1, t2=t2)
    assert len(changes) >= 1
    # Should detect STRENGTHENED
    strengthened = [c for c in changes if c.change == RelationshipChangeType.STRENGTHENED]
    assert len(strengthened) == 1
    assert strengthened[0].previous_strength < strengthened[0].current_strength
