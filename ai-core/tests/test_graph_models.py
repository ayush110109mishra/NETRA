"""
Unit tests for NETRA Phase 8 Knowledge Graph Models & Configuration.
"""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from config import default_config, RelationshipWeights
from models.knowledge_graph import (
    NodeType,
    EdgeType,
    RelationshipStatus,
    RelationshipChangeType,
    ProvenanceItem,
    GraphNode,
    GraphEdge,
    GraphSnapshot,
    GraphStatistics,
    RelationshipDetail,
    PathResult,
    CommunityResult,
    CentralityResult,
    RelationshipChange,
    GraphAssessment,
    GraphAnalyzeRequest,
    GraphAnalyzeResponse,
)
from models.predictive_intelligence import EpistemicStatus


def test_config_phase8_settings():
    assert default_config.version == "8.0.0"
    assert default_config.graph.max_depth == 3
    assert default_config.graph.max_nodes == 500
    assert default_config.relationship_intelligence.weights.correlation_strength == 0.25
    assert default_config.relationship_intelligence.contradiction_penalty_factor == 0.30
    assert default_config.path_config.max_search_depth == 4
    assert default_config.community_config.min_community_size == 2
    assert default_config.temporal_graph.default_validity_duration_seconds == 86400.0


def test_relationship_weights_sum_validation():
    # Sum must be 1.0
    with pytest.raises(ValueError, match="must sum to 1.0"):
        weights = RelationshipWeights(correlation_strength=0.50)
        weights.validate()


def test_graph_node_and_edge_instantiation():
    now = datetime.now(timezone.utc)
    prov = ProvenanceItem(
        evidence_id="EVT-001",
        epistemic_status=EpistemicStatus.OBSERVED,
        source_type="RADAR",
        description="Radar observation"
    )
    node = GraphNode(
        node_id="NODE-ENTITY-12345",
        node_type=NodeType.ENTITY,
        label="ENTITY-01",
        created_at=now,
        confidence=0.95,
        epistemic_status=EpistemicStatus.OBSERVED,
        provenance=[prov],
        latitude=34.0,
        longitude=74.5,
        sector_id="SECTOR_ALPHA",
    )
    assert node.node_id == "NODE-ENTITY-12345"
    assert node.node_type == NodeType.ENTITY
    assert node.confidence == 0.95
    assert node.provenance[0].source_type == "RADAR"

    edge = GraphEdge(
        edge_id="EDGE-001",
        source_node_id=node.node_id,
        target_node_id="NODE-ENTITY-67890",
        edge_type=EdgeType.ASSOCIATED_WITH,
        strength=0.82,
        confidence=0.88,
        epistemic_status=EpistemicStatus.INFERRED,
        first_observed_at=now,
        last_observed_at=now,
        evidence_ids=["EVT-001", "FUS-001"],
        supporting_sources=["RADAR-01", "OPT-02"],
        contradicting_evidence_ids=[],
        is_directional=False,
    )
    assert edge.strength == 0.82
    assert edge.confidence == 0.88
    assert edge.is_directional is False


def test_graph_confidence_bounds():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        GraphNode(
            node_id="NODE-1",
            node_type=NodeType.ENTITY,
            label="E1",
            created_at=now,
            confidence=1.5,
        )

    with pytest.raises(ValidationError):
        GraphEdge(
            edge_id="E-1",
            source_node_id="N1",
            target_node_id="N2",
            edge_type=EdgeType.ASSOCIATED_WITH,
            confidence=-0.1,
        )


def test_graph_assessment_and_response_schemas():
    now = datetime.now(timezone.utc)
    assessment = GraphAssessment(
        observed=["Node A verified"],
        fused=["Corroborated by 2 sources"],
        inferred=["Associated with Node B"],
        predicted=["Forecasted activity surge"],
        uncertain=["Disputed location"],
        summary="Test assessment",
    )
    response = GraphAnalyzeResponse(
        graph_id="GRAPH-TEST-001",
        as_of=now,
        statistics=GraphStatistics(node_count=2, edge_count=1),
        nodes=[],
        edges=[],
        assessment=assessment,
    )
    assert response.graph_id == "GRAPH-TEST-001"
    assert len(response.assessment.observed) == 1
    assert response.version == "8.0.0"
