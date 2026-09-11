"""
Phase 8 Knowledge Graph & Relationship Intelligence Data Models & Schemas.
ASTRAVEDA Defence Intelligence Platform - ATUL AI/ML Engineering.

Defines schemas for nodes, edges, provenance, temporal validity, snapshots,
relationship scoring, change detection, path analysis, centrality, communities,
and API request/response contracts.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from models.predictive_intelligence import EpistemicStatus


class NodeType(str, Enum):
    """Canonical graph node taxonomy."""
    ENTITY = "ENTITY"
    EVENT = "EVENT"
    OBSERVATION = "OBSERVATION"
    FUSED_OBSERVATION = "FUSED_OBSERVATION"
    ANOMALY = "ANOMALY"
    RISK = "RISK"
    FORECAST = "FORECAST"
    SOURCE = "SOURCE"
    CLUSTER = "CLUSTER"
    PATTERN = "PATTERN"
    EVIDENCE = "EVIDENCE"
    SECTOR = "SECTOR"
    BASELINE = "BASELINE"
    CONFLICT = "CONFLICT"


class EdgeType(str, Enum):
    """Canonical graph edge taxonomy."""
    OBSERVED_BY = "OBSERVED_BY"
    SOURCED_FROM = "SOURCED_FROM"
    GENERATED = "GENERATED"
    DERIVED_FROM = "DERIVED_FROM"
    RELATED_TO = "RELATED_TO"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    CORRELATED_WITH = "CORRELATED_WITH"
    MEMBER_OF = "MEMBER_OF"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    HAS_ANOMALY = "HAS_ANOMALY"
    HAS_RISK = "HAS_RISK"
    HAS_FORECAST = "HAS_FORECAST"
    CONTRIBUTES_TO = "CONTRIBUTES_TO"
    PREDICTS = "PREDICTS"
    LOCATED_IN = "LOCATED_IN"
    TEMPORALLY_FOLLOWS = "TEMPORALLY_FOLLOWS"
    SPATIALLY_NEAR = "SPATIALLY_NEAR"
    RESOLVED_AS = "RESOLVED_AS"
    PART_OF_CLUSTER = "PART_OF_CLUSTER"
    EVIDENCE_FOR = "EVIDENCE_FOR"
    EVIDENCE_AGAINST = "EVIDENCE_AGAINST"


class RelationshipStatus(str, Enum):
    """Lifecycle status of an entity relationship."""
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    PERSISTENT = "PERSISTENT"
    WEAKENING = "WEAKENING"
    STRENGTHENING = "STRENGTHENING"
    STALE = "STALE"
    DISPUTED = "DISPUTED"
    ENDED = "ENDED"


class RelationshipChangeType(str, Enum):
    """Types of detected relationship modifications over time."""
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    STRENGTHENED = "STRENGTHENED"
    WEAKENED = "WEAKENED"
    REACTIVATED = "REACTIVATED"
    BECAME_STALE = "BECAME_STALE"
    BECAME_DISPUTED = "BECAME_DISPUTED"
    RESOLVED = "RESOLVED"


class ProvenanceItem(BaseModel):
    """Individual provenance record for an edge or node fact."""
    evidence_id: str = Field(..., description="Canonical ID of originating telemetry or analytical output")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.OBSERVED, description="Epistemic status tier")
    source_type: Optional[str] = Field(default=None, description="Sensor/source classification (e.g. RADAR, OPTICAL)")
    description: Optional[str] = Field(default=None, description="Contextual note")


class TemporalValidity(BaseModel):
    """Interval over which a graph fact remains operationally valid."""
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class GraphNode(BaseModel):
    """Represents a unified intelligence entity, event, source or analytical artifact in the graph."""
    node_id: str = Field(..., description="Deterministic canonical node ID")
    node_type: NodeType = Field(..., description="Categorical node type")
    label: str = Field(..., description="Human-readable node label")
    created_at: datetime = Field(..., description="Creation timestamp")
    valid_from: Optional[datetime] = Field(default=None, description="Start of validity interval")
    valid_to: Optional[datetime] = Field(default=None, description="End of validity interval")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in this node's factual validity")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.OBSERVED, description="Epistemic tier")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary typed metadata")
    provenance: List[ProvenanceItem] = Field(default_factory=list, description="Lineage supporting this node")
    latitude: Optional[float] = Field(default=None, description="Optional latitude for map context")
    longitude: Optional[float] = Field(default=None, description="Optional longitude for map context")
    sector_id: Optional[str] = Field(default=None, description="Operational sector designation")


class GraphEdge(BaseModel):
    """Represents an evidence-grounded or structural relationship connecting two graph nodes."""
    edge_id: str = Field(..., description="Deterministic canonical edge ID")
    source_node_id: str = Field(..., description="Source node canonical ID")
    target_node_id: str = Field(..., description="Target node canonical ID")
    edge_type: EdgeType = Field(..., description="Relationship semantic type")
    strength: float = Field(default=1.0, ge=0.0, le=1.0, description="Normalized relationship strength [0.0 - 1.0]")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in this relationship")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.OBSERVED, description="Epistemic tier")
    valid_from: Optional[datetime] = Field(default=None, description="Start of temporal validity")
    valid_to: Optional[datetime] = Field(default=None, description="End of temporal validity")
    first_observed_at: Optional[datetime] = Field(default=None, description="Earliest supporting observation")
    last_observed_at: Optional[datetime] = Field(default=None, description="Most recent supporting observation")
    evidence_ids: List[str] = Field(default_factory=list, description="IDs of underlying supporting evidence")
    supporting_sources: List[str] = Field(default_factory=list, description="IDs of distinct supporting sensors/sources")
    contradicting_evidence_ids: List[str] = Field(default_factory=list, description="IDs of conflicting evidence")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    provenance: List[ProvenanceItem] = Field(default_factory=list, description="Evidence lineage records")
    is_directional: bool = Field(default=True, description="True if edge has directed semantics, False if symmetric")


class GraphSnapshot(BaseModel):
    """Reproducible point-in-time state of the knowledge graph."""
    snapshot_id: str = Field(..., description="Deterministic hash ID of snapshot")
    as_of: datetime = Field(..., description="Temporal evaluation anchor")
    nodes: List[GraphNode] = Field(default_factory=list, description="Active nodes as of timestamp")
    edges: List[GraphEdge] = Field(default_factory=list, description="Active edges as of timestamp")
    node_count: int = Field(default=0, description="Total active nodes")
    edge_count: int = Field(default=0, description="Total active edges")
    created_at: datetime = Field(..., description="Snapshot capture timestamp")


class GraphStatistics(BaseModel):
    """Descriptive structural metrics of the graph (strictly non-threat)."""
    node_count: int = Field(default=0, description="Total nodes")
    edge_count: int = Field(default=0, description="Total edges")
    entity_count: int = Field(default=0, description="Total ENTITY nodes")
    event_count: int = Field(default=0, description="Total EVENT nodes")
    source_count: int = Field(default=0, description="Total SOURCE nodes")
    anomaly_count: int = Field(default=0, description="Total ANOMALY nodes")
    forecast_count: int = Field(default=0, description="Total FORECAST nodes")
    community_count: int = Field(default=0, description="Total detected communities")
    connected_component_count: int = Field(default=0, description="Connected components count")
    graph_density: float = Field(default=0.0, description="Ratio of existing edges to potential edges")
    average_degree: float = Field(default=0.0, description="Average node degree")
    isolated_node_count: int = Field(default=0, description="Nodes with zero incident edges")


class RelationshipDetail(BaseModel):
    """Comprehensive analytical assessment of an entity-to-entity relationship."""
    relationship_id: str = Field(..., description="Canonical ID of relationship")
    source_entity_id: str = Field(..., description="Origin entity ID")
    target_entity_id: str = Field(..., description="Destination entity ID")
    relationship_type: str = Field(..., description="Dominant relationship classification")
    strength: float = Field(..., ge=0.0, le=1.0, description="Aggregated relationship strength")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Aggregated confidence")
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    observation_count: int = 0
    supporting_event_count: int = 0
    independent_source_count: int = 0
    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)
    temporal_persistence_seconds: float = 0.0
    recency_score: float = 1.0
    status: RelationshipStatus = RelationshipStatus.ACTIVE
    why: List[str] = Field(default_factory=list, description="Human-readable explainability points")
    is_disputed: bool = False


class PathResult(BaseModel):
    """Deterministic, evidence-grounded traversable path between two entities."""
    path_found: bool = Field(..., description="True if a valid traversable path exists")
    source: str = Field(..., description="Source entity ID")
    target: str = Field(..., description="Target entity ID")
    nodes: List[str] = Field(default_factory=list, description="Ordered sequence of node IDs along path")
    edges: List[str] = Field(default_factory=list, description="Ordered sequence of edge IDs along path")
    hop_count: int = Field(default=0, description="Number of traversal hops")
    path_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Bottleneck/conservative path confidence")
    weakest_link: Optional[str] = Field(default=None, description="Edge ID with lowest confidence along path")
    supporting_evidence: List[str] = Field(default_factory=list, description="Cumulative evidence IDs along path")
    epistemic_breakdown: Dict[str, int] = Field(default_factory=dict, description="Count of edges per epistemic tier")
    explanation: str = Field(default="", description="Narrative path synthesis")


class CommunityResult(BaseModel):
    """Structural network cluster/community partition (strictly non-allegiance)."""
    community_id: str = Field(..., description="Deterministic community ID")
    member_nodes: List[str] = Field(default_factory=list, description="All node IDs in community")
    member_entities: List[str] = Field(default_factory=list, description="Entity node IDs in community")
    internal_edge_count: int = Field(default=0, description="Edges between members")
    external_edge_count: int = Field(default=0, description="Edges connecting to non-members")
    density: float = Field(default=0.0, description="Internal subgraph edge density")
    average_relationship_strength: float = Field(default=0.0, description="Mean strength of internal edges")
    supporting_evidence: List[str] = Field(default_factory=list, description="Underlying evidence IDs")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Structural cluster confidence")


class CentralityResult(BaseModel):
    """Structural importance metric for a node (strictly non-threat)."""
    node_id: str = Field(..., description="Target node ID")
    node_type: NodeType = Field(..., description="Node classification")
    label: str = Field(..., description="Node label")
    degree_centrality: float = Field(default=0.0, ge=0.0, description="Normalized degree centrality")
    weighted_degree: float = Field(default=0.0, ge=0.0, description="Sum of incident edge strengths")
    betweenness_centrality: float = Field(default=0.0, ge=0.0, description="Deterministic betweenness score")
    structural_role: str = Field(default="PERIPHERAL", description="Structural category: BRIDGE, HUB, PERIPHERAL")


class RelationshipChange(BaseModel):
    """Detected modification in relationship state or strength between snapshots."""
    entity_id: str = Field(..., description="Primary entity affected")
    change: RelationshipChangeType = Field(..., description="Categorical change type")
    relationship: str = Field(..., description="Canonical relationship identifier string")
    previous_strength: Optional[float] = None
    current_strength: Optional[float] = None
    supporting_evidence: List[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class GraphAssessment(BaseModel):
    """5-Tier Epistemic graph intelligence assessment."""
    observed: List[str] = Field(default_factory=list, description="Facts directly verified by telemetry")
    fused: List[str] = Field(default_factory=list, description="Multi-sensor corroborated facts")
    inferred: List[str] = Field(default_factory=list, description="Analytically derived associations & clusters")
    predicted: List[str] = Field(default_factory=list, description="Forecasted future connections or activity")
    uncertain: List[str] = Field(default_factory=list, description="Conflicting or low-confidence connections")
    summary: str = Field(default="", description="Executive intelligence synthesis")


# --- API Request and Response Models ---

class GraphAnalyzeRequest(BaseModel):
    """Request envelope for graph construction and analysis."""
    as_of: Optional[datetime] = Field(default=None, description="Point-in-time temporal evaluation anchor")
    entity_ids: Optional[List[str]] = Field(default=None, description="Optional entity filter scope")
    node_types: Optional[List[NodeType]] = Field(default=None, description="Filter by node types")
    edge_types: Optional[List[EdgeType]] = Field(default=None, description="Filter by edge types")
    min_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum edge confidence filter")
    depth: int = Field(default=1, ge=1, le=3, description="Traversal search depth")
    limit: int = Field(default=500, ge=1, le=1000, description="Maximum returned nodes/edges")


class GraphAnalyzeResponse(BaseModel):
    """Response envelope for full graph intelligence analysis."""
    graph_id: str = Field(..., description="Deterministic graph execution ID")
    as_of: datetime = Field(..., description="Temporal anchor used for evaluation")
    statistics: GraphStatistics = Field(default_factory=GraphStatistics)
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    relationships: List[RelationshipDetail] = Field(default_factory=list)
    communities: List[CommunityResult] = Field(default_factory=list)
    centrality: List[CentralityResult] = Field(default_factory=list)
    changes: List[RelationshipChange] = Field(default_factory=list)
    assessment: GraphAssessment = Field(default_factory=GraphAssessment)
    provenance: Dict[str, List[ProvenanceItem]] = Field(default_factory=dict)
    epistemic_ledger: Dict[str, List[str]] = Field(default_factory=dict)
    version: str = Field(default="8.0.0", description="Intelligence Core version")
    truncated: bool = Field(default=False, description="True if response was capped by limits")
    truncation_reason: Optional[str] = None


class EntityNetworkResponse(BaseModel):
    """Response envelope for focused entity ego-network query."""
    focus_entity: str = Field(..., description="Target entity ID")
    neighbors: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    relationships: List[RelationshipDetail] = Field(default_factory=list)
    clusters: List[CommunityResult] = Field(default_factory=list)
    supporting_evidence: List[str] = Field(default_factory=list)
    relationship_changes: List[RelationshipChange] = Field(default_factory=list)
    network_statistics: Dict[str, Any] = Field(default_factory=dict)
    assessment: GraphAssessment = Field(default_factory=GraphAssessment)


class GraphChangesResponse(BaseModel):
    """Response envelope for temporal relationship changes."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    changes: List[RelationshipChange] = Field(default_factory=list)
    summary: Dict[str, int] = Field(default_factory=dict)


class GraphSnapshotResponse(BaseModel):
    """Response envelope for point-in-time snapshot."""
    snapshot: GraphSnapshot
