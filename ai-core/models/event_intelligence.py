"""
Phase 2 Event Intelligence Data Schemas for NETRA.
Defines canonical events, multi-dimensional correlations, clusters, patterns,
baseline drift, deduplication results, and structured multi-event assessments.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

from models.common import (
    Coordinates,
    EventSource,
    RelationshipType,
    RelationshipStrength,
    SeverityLevel,
    RiskLevel,
    ClassificationType,
)


class CanonicalEvent(BaseModel):
    """
    Standardized, normalized synthetic event representation.
    Ensures consistent downstream analysis regardless of raw input format.
    """
    event_id: str = Field(..., description="Unique event identifier (e.g. EVT-SYNTH-001)")
    event_type: str = Field(..., description="Canonical event category (e.g. MOVEMENT, PATROL_DEVIATION)")
    timestamp: datetime = Field(..., description="UTC observation timestamp")
    location: Coordinates = Field(..., description="Normalized geospatial coordinates")
    entity_ids: List[str] = Field(default_factory=list, description="Associated entity identifiers")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Normalized telemetry metrics (speed, heading, etc.)")
    source: EventSource = Field(default_factory=EventSource, description="Source attribution metadata")
    raw_event: Optional[Dict[str, Any]] = Field(default=None, description="Original raw event for auditability")
    normalization_version: str = Field(default="2.0.0", description="Schema normalization version")

    @property
    def coordinates(self) -> Coordinates:
        return self.location

    @property
    def entity_id(self) -> str:
        return self.entity_ids[0] if self.entity_ids else "UNKNOWN"


class DuplicateAnalysisResult(BaseModel):
    """Event deduplication assessment for a single event."""
    event_id: str = Field(..., description="Analyzed event ID")
    is_duplicate: bool = Field(default=False, description="Whether event is an exact or near duplicate")
    duplicate_of: Optional[str] = Field(default=None, description="ID of the original event this duplicates")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Deduplication confidence")
    reasons: List[str] = Field(default_factory=list, description="Audit criteria supporting deduplication")


class CorrelationComponents(BaseModel):
    """Individual mathematical dimensions of the multi-dimensional correlation score."""
    temporal: float = Field(..., ge=0.0, le=1.0, description="Temporal proximity score")
    spatial: float = Field(..., ge=0.0, le=1.0, description="Spatial proximity score")
    entity: float = Field(..., ge=0.0, le=1.0, description="Entity overlap score")
    type_similarity: float = Field(..., ge=0.0, le=1.0, description="Taxonomy type compatibility")
    attribute_similarity: float = Field(..., ge=0.0, le=1.0, description="Telemetry attribute proximity")


class EventCorrelation(BaseModel):
    """Evidence-backed multi-dimensional correlation between two events."""
    source_event_id: str = Field(..., description="First event ID")
    target_event_id: str = Field(..., description="Second event ID")
    correlation_score: float = Field(..., ge=0.0, le=1.0, description="Aggregate correlation score [0.0 - 1.0]")
    strength: RelationshipStrength = Field(..., description="Categorical strength band (VERY_WEAK to VERY_STRONG)")
    components: CorrelationComponents = Field(..., description="Mathematical factor breakdown")
    relationships: List[RelationshipType] = Field(default_factory=list, description="Specific detected relationships")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this detected link")
    reasoning: str = Field(..., description="Human-readable explanation of why these events are associated")


class EventCluster(BaseModel):
    """Coherent cluster of strongly correlated synthetic events."""
    cluster_id: str = Field(..., description="Unique cluster identifier (e.g. CLUSTER-SYNTH-001)")
    event_ids: List[str] = Field(..., description="Event IDs comprising this cluster")
    event_count: int = Field(..., ge=1, description="Total number of events in cluster")
    unique_entities: List[str] = Field(default_factory=list, description="Entities involved in cluster")
    event_types: List[str] = Field(default_factory=list, description="Unique event types observed")
    start_time: datetime = Field(..., description="Earliest event timestamp")
    end_time: datetime = Field(..., description="Latest event timestamp")
    duration_seconds: float = Field(..., ge=0.0, description="Time span of the cluster")
    spatial_extent: Dict[str, Any] = Field(default_factory=dict, description="Bounding box and centroid coordinates")
    cohesion_score: float = Field(..., ge=0.0, le=1.0, description="Average internal correlation score")
    average_risk: float = Field(..., ge=0.0, le=1.0, description="Mean risk score across cluster events")
    average_confidence: float = Field(..., ge=0.0, le=1.0, description="Mean confidence score")
    average_severity: SeverityLevel = Field(..., description="Representative cluster severity")


class EventPattern(BaseModel):
    """Recognized synthetic behavioral pattern across events."""
    pattern_detected: bool = Field(default=True, description="Whether pattern was confirmed")
    pattern_type: str = Field(..., description="Type of pattern (e.g. SEQUENTIAL_ESCALATION, TEMPORAL_BURST, PERIODIC_PATROL)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Pattern confidence score")
    event_ids: List[str] = Field(default_factory=list, description="Events participating in the pattern")
    description: str = Field(..., description="Explainable description of the observed pattern")


class BaselineDriftResult(BaseModel):
    """Analytical indicator evaluating deviation between historical, recent, and current baselines."""
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized drift magnitude [0.0 - 1.0]")
    direction: str = Field(..., description="Trend direction: INCREASE, DECREASE, or STABLE")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Reliability of baseline evaluation")
    description: str = Field(..., description="Explainable operational assessment of the drift")


class StructuredAssessment(BaseModel):
    """
    Phase 2 Structured Assessment.
    Explicitly separates factual observations from inferences and uncertainties.
    """
    summary: str = Field(..., description="High-level operational summary")
    observed: List[str] = Field(default_factory=list, description="Direct factual observations from input data")
    inferred: List[str] = Field(default_factory=list, description="Model-derived associations, patterns, and assessments")
    uncertain: List[str] = Field(default_factory=list, description="Explicit operational caveats, missing data, and non-causal warnings")


class MultiEventContextInput(BaseModel):
    """Optional operational sector context for multi-event batch analysis."""
    sector_id: Optional[str] = Field(default=None, description="Operational sector designation")
    historical_baseline_activity: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Long-term historical activity baseline")
    recent_baseline_activity: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Recent window activity baseline")


class MultiEventAnalyzeRequest(BaseModel):
    """
    Request payload for POST /api/v1/intelligence/events/analyze.
    Accepts a batch of synthetic events and optional sector context.
    """
    events: List[Dict[str, Any]] = Field(..., min_length=1, description="List of raw or canonical synthetic events")
    context: Optional[MultiEventContextInput] = Field(default=None, description="Optional sector baseline context")


class MultiEventAnalyzeResponse(BaseModel):
    """
    Response payload for POST /api/v1/intelligence/events/analyze.
    Machine-readable multi-event intelligence picture for Ayush's operational frontend.
    """
    analysis_id: str = Field(..., description="Unique deterministic analysis identifier")
    timestamp: datetime = Field(..., description="Execution timestamp (UTC)")
    event_count: int = Field(..., ge=1, description="Total events analyzed")
    normalized_events: List[CanonicalEvent] = Field(..., description="Standardized canonical event representations")
    duplicates: List[DuplicateAnalysisResult] = Field(default_factory=list, description="Deduplication assessments")
    correlations: List[EventCorrelation] = Field(default_factory=list, description="Pairwise evidence-backed correlations")
    clusters: List[EventCluster] = Field(default_factory=list, description="Detected operational event clusters")
    patterns: List[EventPattern] = Field(default_factory=list, description="Detected behavioral sequences or bursts")
    baseline_drift: BaselineDriftResult = Field(..., description="Sector baseline drift assessment")
    assessment: StructuredAssessment = Field(..., description="Separated OBSERVED, INFERRED, UNCERTAIN assessment")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Audit and performance metadata")
