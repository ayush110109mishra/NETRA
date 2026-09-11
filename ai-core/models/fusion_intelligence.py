"""
Phase 5 Multi-Source Intelligence Fusion Data Schemas for NETRA.
Defines canonical observations, source registries, source health, alignment,
entity resolution, corroboration, conflict records, evidence ledger,
fused observations, epistemic four-tier assessments, and API contracts.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from models.common import Coordinates


class SourceType(str, Enum):
    """Supported synthetic source classifications."""
    RADAR = "RADAR"
    OPTICAL = "OPTICAL"
    TELEMETRY = "TELEMETRY"
    SIGNAL = "SIGNAL"
    EVENT = "EVENT"
    SENSOR_A = "SENSOR_A"
    SENSOR_B = "SENSOR_B"
    HISTORICAL = "HISTORICAL"
    UNKNOWN = "UNKNOWN"


class SourceStatus(str, Enum):
    """Operational health status of a sensor or feed."""
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    INACTIVE = "INACTIVE"
    DROPOUT = "DROPOUT"
    UNKNOWN = "UNKNOWN"


class ConflictType(str, Enum):
    """Categorization of inter-source contradictions."""
    POSITION = "POSITION"
    VELOCITY = "VELOCITY"
    EVENT_TYPE = "EVENT_TYPE"
    STATUS = "STATUS"
    TEMPORAL = "TEMPORAL"


class ConflictStatus(str, Enum):
    """State of conflict arbitration."""
    NONE = "NONE"
    PARTIAL = "PARTIAL"
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


class SpatialAlignmentLevel(str, Enum):
    """Spatial relationship between multi-source observations."""
    AGREEMENT = "AGREEMENT"
    PARTIAL_AGREEMENT = "PARTIAL_AGREEMENT"
    CONFLICT = "CONFLICT"


class EntityResolutionStatus(str, Enum):
    """Status of resolving an observation signature to a synthetic entity."""
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"


class EpistemicCategory(str, Enum):
    """Rigorous epistemic boundaries for intelligence assessments."""
    OBSERVED = "OBSERVED"
    FUSED = "FUSED"
    INFERRED = "INFERRED"
    UNCERTAIN = "UNCERTAIN"


class SourceMetadata(BaseModel):
    """Metadata record for a registered intelligence source/sensor."""
    source_id: str = Field(..., description="Unique source identifier (e.g. RADAR_01)")
    source_type: SourceType = Field(..., description="Source classification type")
    source_name: str = Field(..., description="Human-readable source designation")
    reliability: float = Field(..., ge=0.0, le=1.0, description="Base declared source reliability [0.0 - 1.0]")
    independence_group: str = Field(..., description="Independence cluster to prevent duplicate feed double counting")
    spatial_accuracy_km: float = Field(default=0.10, ge=0.0, description="Nominal 1-sigma spatial error in km")
    temporal_accuracy_sec: float = Field(default=1.0, ge=0.0, description="Nominal timestamp accuracy in seconds")
    status: SourceStatus = Field(default=SourceStatus.ACTIVE, description="Source lifecycle state")
    last_seen: Optional[datetime] = Field(default=None, description="UTC timestamp of last received observation")
    observation_count: int = Field(default=0, ge=0, description="Total observations processed from this source")
    contradiction_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Rate of conflicting reports")
    freshness_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Freshness evaluation factor")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom sensor configuration or parameters")


class SourceHealth(BaseModel):
    """Dynamic source health and reliability evaluation."""
    source_id: str = Field(..., description="Reporting source ID")
    source_type: str = Field(..., description="Source category")
    status: SourceStatus = Field(..., description="Operational status")
    reliability_score: float = Field(..., ge=0.0, le=1.0, description="Calibrated reliability score")
    is_stale: bool = Field(default=False, description="Whether source reports are considered stale")
    is_dropout: bool = Field(default=False, description="Whether source has experienced sudden dropout")
    observation_count: int = Field(default=0, ge=0, description="Number of observations analyzed")
    contradiction_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Ratio of conflicting reports")
    reliability_trend: str = Field(default="STABLE", description="Trend direction (IMPROVING, DEGRADING, STABLE)")
    factors: Dict[str, float] = Field(default_factory=dict, description="Factor breakdown of reliability calculation")
    explanation: str = Field(..., description="Analytical explanation of source health")


class Velocity(BaseModel):
    """Kinematic state specification."""
    speed_kmh: float = Field(..., ge=0.0, description="Speed in km/h")
    heading_deg: Optional[float] = Field(default=None, ge=0.0, le=360.0, description="Heading in degrees (0 - 360)")


class NormalizationTraceItem(BaseModel):
    """Audit entry documenting transformation of a single observation attribute."""
    field: str = Field(..., description="Canonical field name")
    original_field: str = Field(..., description="Raw field name from source payload")
    original_value: Any = Field(default=None, description="Raw value before transformation")
    normalized_value: Any = Field(default=None, description="Value after normalization")
    conversion: Optional[str] = Field(default=None, description="Applied conversion rule (e.g. knots -> km/h)")


class CanonicalObservation(BaseModel):
    """
    Standardized synthetic observation representation.
    Preserves complete provenance, normalization trace, and raw payload.
    """
    observation_id: str = Field(..., description="Deterministic observation identifier")
    source_id: str = Field(..., description="Identifier of reporting source")
    source_type: str = Field(..., description="Classification of reporting source")
    timestamp: datetime = Field(..., description="UTC observation timestamp")
    received_at: datetime = Field(..., description="UTC ingestion timestamp")
    entity_hint: Optional[str] = Field(default=None, description="Source-level track or target ID hint")
    position: Optional[Coordinates] = Field(default=None, description="Normalized coordinates")
    position_uncertainty_km: float = Field(default=0.10, ge=0.0, description="Estimated spatial uncertainty radius in km")
    velocity: Optional[Velocity] = Field(default=None, description="Normalized kinematic state")
    event_type: Optional[str] = Field(default=None, description="Normalized event type classification")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Domain attributes")
    quality: float = Field(default=1.0, ge=0.0, le=1.0, description="Base observation quality score")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Audit lineage metadata")
    normalization_trace: List[NormalizationTraceItem] = Field(default_factory=list, description="Audit trail of conversions")
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="Original un-normalized payload")


class TemporalAlignmentResult(BaseModel):
    """Assessment of temporal compatibility between two observations."""
    obs1_id: str = Field(..., description="First observation ID")
    obs2_id: str = Field(..., description="Second observation ID")
    delta_seconds: float = Field(..., description="Absolute time difference in seconds")
    compatibility_score: float = Field(..., ge=0.0, le=1.0, description="Temporal compatibility [0.0 - 1.0]")
    is_compatible: bool = Field(..., description="Whether observations fall within fusion window")
    is_stale: bool = Field(default=False, description="Whether either observation is stale")
    explanation: str = Field(..., description="Analytical explanation of temporal alignment")


class SpatialAlignmentResult(BaseModel):
    """Assessment of spatial compatibility between two observations."""
    obs1_id: str = Field(..., description="First observation ID")
    obs2_id: str = Field(..., description="Second observation ID")
    distance_km: float = Field(..., ge=0.0, description="Great circle distance in kilometers")
    alignment_level: SpatialAlignmentLevel = Field(..., description="Spatial agreement category")
    spatial_compatibility_score: float = Field(..., ge=0.0, le=1.0, description="Spatial compatibility [0.0 - 1.0]")
    uncertainty_overlap: bool = Field(..., description="Whether spatial uncertainty circles intersect")
    explanation: str = Field(..., description="Analytical explanation of spatial alignment")


class EntityResolutionResult(BaseModel):
    """Deterministic resolution of an observation to a synthetic entity."""
    resolved_entity_id: str = Field(..., description="Matched canonical entity ID or ENTITY_UNRESOLVED")
    status: EntityResolutionStatus = Field(..., description="Resolution status (RESOLVED, AMBIGUOUS, UNRESOLVED)")
    match_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of entity match [0.0 - 1.0]")
    resolution_factors: Dict[str, float] = Field(default_factory=dict, description="Factor weights supporting match")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Competing candidate entities if ambiguous")
    explanation: str = Field(..., description="Analytical rationale for resolution decision")


class CorroborationResult(BaseModel):
    """Assessment of multi-source corroboration and independence."""
    corroboration_score: float = Field(..., ge=0.0, le=1.0, description="Independent corroboration factor [0.0 - 1.0]")
    supporting_sources: List[str] = Field(default_factory=list, description="List of source IDs agreeing on observation")
    independent_source_count: int = Field(default=0, ge=0, description="Count of distinct independence groups")
    duplicate_source_count: int = Field(default=0, ge=0, description="Count of redundant/duplicate source feeds")
    independence_groups: List[str] = Field(default_factory=list, description="Unique independence groups represented")
    explanation: str = Field(..., description="Analytical rationale regarding source agreement and independence")


class ConflictRecord(BaseModel):
    """Documented contradiction between reporting sources."""
    conflict_id: str = Field(..., description="Unique conflict identifier")
    conflict_type: ConflictType = Field(..., description="Classification of contradiction")
    severity: float = Field(..., ge=0.0, le=1.0, description="Contradiction severity [0.0 - 1.0]")
    sources: List[str] = Field(default_factory=list, description="Sources involved in contradiction")
    observation_ids: List[str] = Field(default_factory=list, description="Observation IDs exhibiting discrepancy")
    status: ConflictStatus = Field(default=ConflictStatus.UNRESOLVED, description="Arbitration state")
    claims: Dict[str, Any] = Field(default_factory=dict, description="Preserved claims from all conflicting sources")
    resolution_method: Optional[str] = Field(default=None, description="Arbitration rule applied (e.g. RELIABILITY_WEIGHTED)")
    resolved_claim: Optional[Any] = Field(default=None, description="Adopted baseline value if resolved")
    unresolved_uncertainty: float = Field(default=0.0, ge=0.0, le=1.0, description="Remaining uncertainty due to conflict")
    explanation: str = Field(..., description="Analytical explanation of conflict and arbitration")


class EvidenceRecord(BaseModel):
    """Immutable audit record linking fused intelligence to raw source observations."""
    evidence_id: str = Field(..., description="Unique evidence tracking identifier")
    source_observations: List[str] = Field(default_factory=list, description="IDs of raw observations contributing to evidence")
    derived_from: List[str] = Field(default_factory=list, description="Intermediate processing IDs (resolutions, alignments)")
    evidence_quality: float = Field(..., ge=0.0, le=1.0, description="Evidence quality metric [0.0 - 1.0]")
    lineage_path: List[str] = Field(default_factory=list, description="Step-by-step pipeline transformations")


class FusedObservation(BaseModel):
    """Synthesized, high-confidence state representation derived from multi-source fusion."""
    fused_observation_id: str = Field(..., description="Unique fused observation identifier")
    entity_id: str = Field(..., description="Associated canonical synthetic entity ID")
    fused_timestamp: datetime = Field(..., description="Fused consensus UTC timestamp")
    fused_position: Optional[Coordinates] = Field(default=None, description="Reliability-weighted geospatial coordinate")
    position_uncertainty_km: float = Field(default=0.10, ge=0.0, description="Fused position uncertainty radius")
    fused_velocity: Optional[Velocity] = Field(default=None, description="Fused kinematic speed and heading")
    fused_event_type: Optional[str] = Field(default=None, description="Consensus event classification")
    supporting_sources: List[str] = Field(default_factory=list, description="All sources contributing to fused record")
    independent_source_count: int = Field(default=1, ge=1, description="Number of distinct independent sources agreeing")
    agreement_score: float = Field(..., ge=0.0, le=1.0, description="Inter-source agreement level [0.0 - 1.0]")
    conflict_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Residual conflict penalty [0.0 - 1.0]")
    evidence_quality: float = Field(..., ge=0.0, le=1.0, description="Overall evidence quality [0.0 - 1.0]")
    fusion_confidence: float = Field(..., ge=0.0, le=1.0, description="Calibrated confidence in fused assessment")
    source_claims: Dict[str, Any] = Field(default_factory=dict, description="Detailed claims from each contributing sensor")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Audit lineage references")
    explanation: str = Field(..., description="Human-readable synthesis explanation")


class FusionAssessment(BaseModel):
    """Four-tier epistemic breakdown of multi-source intelligence."""
    summary: str = Field(..., description="Operational summary of multi-source fusion findings")
    observed: List[str] = Field(default_factory=list, description="Directly reported single-source sensor observations")
    fused: List[str] = Field(default_factory=list, description="Multi-source corroborated findings")
    inferred: List[str] = Field(default_factory=list, description="Analytically derived inferences and resolutions")
    uncertain: List[str] = Field(default_factory=list, description="Contradictions, unresolved ambiguities, or gaps")
    epistemic_ledger: Dict[str, List[str]] = Field(default_factory=dict, description="Category-indexed audit map")


class FusionAnalyzeRequest(BaseModel):
    """Request payload for multi-source observation fusion."""
    observations: List[Dict[str, Any]] = Field(..., min_length=1, description="List of raw or semi-structured observations")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional sector or operational context")
    target_entity_id: Optional[str] = Field(default=None, description="Optional target entity ID filter")
    enable_phase4_integration: bool = Field(default=True, description="Whether to execute Phase 4 anomaly & risk analysis on fused result")


class FusionAnalyzeResponse(BaseModel):
    """Comprehensive response envelope for multi-source intelligence fusion."""
    schema_version: str = Field(default="phase5-v1", description="Phase 5 response schema version")
    analysis_id: str = Field(..., description="Deterministic analysis run identifier")
    status: str = Field(default="SUCCESS", description="Analysis status")
    normalized_observations: List[CanonicalObservation] = Field(default_factory=list, description="Normalized observation records")
    fused_observations: List[FusedObservation] = Field(default_factory=list, description="Synthesized multi-source observations")
    conflicts: List[ConflictRecord] = Field(default_factory=list, description="Detected sensor contradictions and resolutions")
    corroboration: CorroborationResult = Field(..., description="Multi-source corroboration metrics")
    evidence_ledger: List[EvidenceRecord] = Field(default_factory=list, description="Immutable evidence lineage records")
    source_health_summary: Dict[str, SourceHealth] = Field(default_factory=dict, description="Health and reliability metrics by source")
    confidence_summary: Dict[str, Any] = Field(default_factory=dict, description="Calibrated confidence breakdown")
    assessment: FusionAssessment = Field(..., description="Epistemic four-tier intelligence assessment")
    phase4_anomaly_assessment: Optional[Any] = Field(default=None, description="Optional integrated Phase 4 anomaly & risk analysis")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Run execution metadata and environment context")


class EntityFusedIntelligenceResponse(BaseModel):
    """Entity-centric fused intelligence profile for dashboard display."""
    entity_id: str = Field(..., description="Canonical entity ID")
    fused_observations: List[FusedObservation] = Field(default_factory=list, description="Fused observations for this entity")
    supporting_sources: List[str] = Field(default_factory=list, description="All sources reporting on this entity")
    independent_source_count: int = Field(default=1, ge=1, description="Independent source count")
    conflicts: List[ConflictRecord] = Field(default_factory=list, description="Active or resolved conflicts concerning this entity")
    evidence: List[EvidenceRecord] = Field(default_factory=list, description="Associated evidence records")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall fused intelligence confidence")
    anomaly_integration: Optional[Dict[str, Any]] = Field(default=None, description="Phase 4 anomaly summary if available")
    risk_integration: Optional[Dict[str, Any]] = Field(default=None, description="Phase 4 risk summary if available")
