"""
Phase 3 Entity Intelligence Data Schemas for NETRA.
Defines canonical entities, behavioral baselines, change detection, anomaly models,
risk & confidence profiles, timeline models, and Focus Mode contracts.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

from models.common import (
    Coordinates,
    EntityStatus,
    Allegiance,
    RelationshipType,
    RelationshipStrength,
    SeverityLevel,
    RiskLevel,
)


class CanonicalEntity(BaseModel):
    """Core entity identity and lifecycle status."""
    entity_id: str = Field(..., description="Unique entity identifier (e.g. ENTITY-SYNTH-047)")
    entity_type: str = Field(..., description="Platform classification (e.g. VEHICLE, AIRCRAFT, VESSEL, RADAR_STATION)")
    callsign: Optional[str] = Field(default=None, description="Tactical callsign")
    allegiance: Allegiance = Field(default=Allegiance.UNKNOWN, description="Simulated allegiance marker")
    status: EntityStatus = Field(default=EntityStatus.UNKNOWN, description="Lifecycle operational state")
    first_observed: datetime = Field(..., description="Initial detection timestamp (UTC)")
    last_observed: datetime = Field(..., description="Most recent observation timestamp (UTC)")
    observation_count: int = Field(default=1, ge=1, description="Total telemetry reports received")
    event_count: int = Field(default=1, ge=1, description="Total discrete synthetic events participated in")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Platform characteristics")

    @property
    def associated_entity_ids(self) -> List[str]:
        return self.attributes.get("associated_entity_ids", [])


class EntityProfile(BaseModel):
    """High-level descriptive overview of the entity."""
    entity_id: str = Field(..., description="Entity ID")
    entity_type: str = Field(..., description="Platform classification")
    active_duration_hours: float = Field(..., ge=0.0, description="Active observation span in hours")
    unique_locations_count: int = Field(default=1, ge=1, description="Number of distinct coordinate points visited")
    dominant_event_type: str = Field(..., description="Most frequently observed event category")
    associated_entities_count: int = Field(default=0, ge=0, description="Number of unique correlated entities")
    associated_clusters_count: int = Field(default=0, ge=0, description="Number of activity clusters involved in")


class EntitySpatialBehavior(BaseModel):
    """Spatial concentration and movement profile."""
    centroid: Coordinates = Field(..., description="Mean geographic coordinate of activity")
    bounding_radius_km: float = Field(..., ge=0.0, description="Max historical distance from centroid")
    spatial_concentration: float = Field(..., ge=0.0, le=1.0, description="Concentration index (1.0 = tightly clustered)")
    frequent_sectors: List[str] = Field(default_factory=list, description="Primary operational sectors")


class EntityTemporalBehavior(BaseModel):
    """Temporal activity patterns and periodicity."""
    peak_activity_hour: int = Field(..., ge=0, le=23, description="Peak UTC hour of observed activity")
    average_inter_event_minutes: float = Field(..., ge=0.0, description="Mean interval between consecutive events")
    hourly_distribution: Dict[int, float] = Field(default_factory=dict, description="Activity probability by hour [0-23]")


class EntityBehaviorProfile(BaseModel):
    """Established normal synthetic baseline."""
    baseline_status: str = Field(..., description="SUFFICIENT_HISTORY or INSUFFICIENT_HISTORY (cold-start)")
    sample_count: int = Field(..., ge=0, description="Number of events establishing this baseline")
    event_frequency_per_day: float = Field(..., ge=0.0, description="Average events recorded per 24 hours")
    average_activity: float = Field(..., ge=0.0, le=1.0, description="Baseline normalized activity level")
    average_speed: float = Field(..., ge=0.0, description="Baseline speed in km/h")
    spatial: Optional[EntitySpatialBehavior] = Field(default=None, description="Spatial behavior metrics")
    temporal: Optional[EntityTemporalBehavior] = Field(default=None, description="Temporal behavior metrics")
    event_type_distribution: Dict[str, float] = Field(default_factory=dict, description="Probability distribution of event types")


class BehavioralChangeItem(BaseModel):
    """An individual observed shift from baseline."""
    feature: str = Field(..., description="Feature that shifted (e.g. speed, frequency, spatial_expansion, event_type)")
    direction: str = Field(..., description="Direction of change: INCREASE, DECREASE, STABLE, or NEW")
    magnitude: float = Field(..., ge=0.0, description="Relative magnitude of shift")
    description: str = Field(..., description="Explainable description of the behavioral change")
    evidence_event_ids: List[str] = Field(default_factory=list, description="Source event IDs demonstrating the change")


class BehavioralChangeReport(BaseModel):
    """Comprehensive evaluation of recent deviations from established baseline."""
    detected: bool = Field(default=False, description="Whether significant behavioral shift was detected")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall shift severity score [0.0 - 1.0]")
    changes: List[BehavioralChangeItem] = Field(default_factory=list, description="Specific detected behavioral changes")


class EntityAnomalyIndicator(BaseModel):
    """Specific contributing anomaly indicator."""
    indicator: str = Field(..., description="Indicator name (e.g. speed_surge, spatial_expansion, frequency_spike)")
    score: float = Field(..., ge=0.0, le=1.0, description="Anomaly magnitude [0.0 - 1.0]")
    description: str = Field(..., description="Human-readable explanation of the anomaly")
    evidence_event_ids: List[str] = Field(default_factory=list, description="Underlying synthetic evidence events")


class EntityAnomalyAssessment(BaseModel):
    """Entity-level anomaly rating."""
    score: float = Field(..., ge=0.0, le=1.0, description="Aggregate anomaly score [0.0 - 1.0]")
    level: str = Field(..., description="Categorical rating: LOW, MEDIUM, HIGH, CRITICAL")
    indicators: List[EntityAnomalyIndicator] = Field(default_factory=list, description="Active anomaly indicators")


class EntityRiskFactor(BaseModel):
    """Individual contributor to the entity-level risk score."""
    factor: str = Field(..., description="Factor name (e.g. behavioral_deviation, event_risk, anomaly_score)")
    contribution: float = Field(..., ge=0.0, le=1.0, description="Weighted contribution to overall risk")
    description: str = Field(..., description="Explainable rationale")


class EntityRiskProfile(BaseModel):
    """Entity analytical risk state (Phase 3)."""
    score: float = Field(..., ge=0.0, le=1.0, description="Aggregate risk score [0.0 - 1.0]")
    level: RiskLevel = Field(..., description="Categorical risk rating: LOW, MEDIUM, HIGH, CRITICAL")
    factors: List[EntityRiskFactor] = Field(default_factory=list, description="Factor breakdown")
    risk_model_version: str = Field(default="phase3-v1", description="Risk calculation algorithm version")


class EntityConfidenceFactor(BaseModel):
    """Contributor to confidence."""
    factor: str = Field(..., description="Factor name")
    score: float = Field(..., ge=0.0, le=1.0, description="Factor score")
    description: str = Field(..., description="Rationale")


class EntityConfidenceContradiction(BaseModel):
    """Explicit contradiction detected across sensor feeds."""
    feature: str = Field(..., description="Conflicting telemetry feature")
    sources: List[str] = Field(default_factory=list, description="Reporting sources in disagreement")
    confidence_impact: float = Field(..., description="Deduction applied to confidence score")
    description: str = Field(..., description="Nature of the conflict")


class EntityConfidenceProfile(BaseModel):
    """Reliability assessment of entity intelligence."""
    score: float = Field(..., ge=0.0, le=1.0, description="Aggregate confidence score [0.0 - 1.0]")
    level: str = Field(..., description="Confidence level: LOW, MEDIUM, HIGH")
    factors: List[EntityConfidenceFactor] = Field(default_factory=list, description="Supporting quality factors")
    contradictions: List[EntityConfidenceContradiction] = Field(default_factory=list, description="Contradictions flagged")


class EntityRelationshipEdge(BaseModel):
    """Evidence-backed relationship link with another entity."""
    entity_id: str = Field(..., description="Associated entity ID")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    score: float = Field(..., ge=0.0, le=1.0, description="Association strength score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in association")
    co_occurrence_count: int = Field(default=1, ge=1, description="Number of events both entities appeared in")
    evidence_event_ids: List[str] = Field(default_factory=list, description="Events demonstrating the association")


class EntityClusterMembership(BaseModel):
    """Participation in Phase 2 operational activity clusters."""
    cluster_id: str = Field(..., description="Cluster identifier")
    event_count: int = Field(..., ge=1, description="Events by this entity inside the cluster")
    cohesion: float = Field(..., ge=0.0, le=1.0, description="Cluster internal cohesion score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Cluster confidence")


class EntityPatternOccurrence(BaseModel):
    """Behavioral patterns involving this entity."""
    pattern_type: str = Field(..., description="Type of pattern (e.g. SEQUENTIAL_ESCALATION, TEMPORAL_BURST)")
    occurrences: int = Field(default=1, ge=1, description="Times observed")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Pattern confidence")


class EntityTimelineItem(BaseModel):
    """Chronological event entry for Focus Mode timeline."""
    event_id: str = Field(..., description="Event identifier")
    event_type: str = Field(..., description="Canonical event type")
    timestamp: datetime = Field(..., description="Event timestamp (UTC)")
    location: Coordinates = Field(..., description="Event coordinates")
    severity: SeverityLevel = Field(default=SeverityLevel.LOW, description="Assessed event severity")
    risk: float = Field(default=0.20, ge=0.0, le=1.0, description="Assessed event risk")
    description: str = Field(..., description="Event summary")


class EntityMapContext(BaseModel):
    """Contextual geospatial data for 30% map visualization in Focus Mode."""
    centroid: Coordinates = Field(..., description="Primary centroid coordinate")
    bounding_radius_km: float = Field(..., ge=0.0, description="Operational bounding radius in km")
    observed_coordinates: List[Coordinates] = Field(default_factory=list, description="Historical coordinate points")
    associated_entity_locations: List[Dict[str, Any]] = Field(default_factory=list, description="Locations of correlated entities")


class FourTierAssessment(BaseModel):
    """
    Phase 3 Four-Tier Assessment.
    Strictly separates OBSERVED, INFERRED, PREDICTED, and UNCERTAIN statements.
    """
    summary: str = Field(..., description="Concise executive intelligence summary")
    observed: List[str] = Field(default_factory=list, description="Direct factual observations from synthetic data")
    inferred: List[str] = Field(default_factory=list, description="Model-derived behavioral assessments and correlations")
    predicted: List[str] = Field(default_factory=list, description="Analytical projections based on current patterns")
    uncertain: List[str] = Field(default_factory=list, description="Operational caveats, non-causal warnings, and data gaps")

    @property
    def operational_summary(self) -> str:
        return self.summary


class EntityIntelligenceResponse(BaseModel):
    """
    Master Focus Mode Response for GET /api/v1/intelligence/entities/{entity_id}.
    Provides complete structured context for Ayush's operational frontend in a single call.
    """
    entity: CanonicalEntity
    profile: EntityProfile
    behavior: EntityBehaviorProfile
    changes: BehavioralChangeReport
    anomalies: EntityAnomalyAssessment
    risk: EntityRiskProfile
    confidence: EntityConfidenceProfile
    relationships: List[EntityRelationshipEdge]
    clusters: List[EntityClusterMembership]
    patterns: List[EntityPatternOccurrence]
    timeline: List[EntityTimelineItem]
    map_context: EntityMapContext
    assessment: FourTierAssessment
    metadata: Dict[str, Any] = Field(default_factory=dict)


# --- Entity Comparison Models ---

class EntityCompareRequest(BaseModel):
    """Request payload for POST /api/v1/intelligence/entities/compare."""
    entity_ids: List[str] = Field(..., min_length=2, description="Two or more entity IDs to compare side-by-side")


class EntityCompareItem(BaseModel):
    """Side-by-side comparative metrics for a single entity."""
    entity_id: str
    entity_type: str
    status: EntityStatus
    event_count: int
    event_frequency_per_day: float
    average_activity: float
    average_speed: float
    dominant_event_type: str
    anomaly_score: float
    risk_score: float
    confidence_score: float


class EntityCompareResponse(BaseModel):
    """Response payload for POST /api/v1/intelligence/entities/compare."""
    entities: List[EntityCompareItem]
    comparison_summary: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


# --- Entity Search / Roster Model ---

class EntitySearchResponse(BaseModel):
    """Response payload for GET /api/v1/intelligence/entities."""
    total_count: int
    entities: List[CanonicalEntity]
    metadata: Dict[str, Any] = Field(default_factory=dict)
