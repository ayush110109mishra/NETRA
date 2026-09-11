"""
Phase 4 Advanced Anomaly Intelligence Data Schemas for NETRA.
Defines multi-dimensional anomaly detection models, dimension scores, mathematical attribution,
anomaly persistence states, trends, confirmation levels, and analysis API contracts.
"""

from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

from models.common import Coordinates
from models.entity_intelligence import FourTierAssessment
from models.risk_intelligence import Phase4RiskProfile


class AnomalyLevel(str, Enum):
    """Normalized categorical anomaly level."""
    NOMINAL = "NOMINAL"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyPersistenceState(str, Enum):
    """Behavioral persistence state of detected anomalies."""
    TRANSIENT = "TRANSIENT"
    PERSISTENT = "PERSISTENT"
    RECURRING = "RECURRING"
    ESCALATING = "ESCALATING"
    DECLINING = "DECLINING"


class AnomalyConfirmationLevel(str, Enum):
    """Evidence quality rating supporting the anomaly."""
    UNCONFIRMED = "UNCONFIRMED"
    SUPPORTED = "SUPPORTED"
    CORROBORATED = "CORROBORATED"
    STRONGLY_CORROBORATED = "STRONGLY_CORROBORATED"


class AnomalyLifecycle(str, Enum):
    """Operational lifecycle progression of an anomaly condition."""
    DETECTED = "DETECTED"
    ACTIVE = "ACTIVE"
    PERSISTING = "PERSISTING"
    RESOLVING = "RESOLVING"
    RESOLVED = "RESOLVED"


class TrendDirection(str, Enum):
    """Directional trend of anomaly metrics over time."""
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    STABLE = "STABLE"
    UNKNOWN = "UNKNOWN"


class DimensionScoreItem(BaseModel):
    """Score and audit indicators for a single analytical dimension."""
    dimension: str = Field(..., description="Dimension name (e.g. temporal, spatial, kinematic)")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized dimension score [0.0 - 1.0]")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="Dimension evidence confidence")
    indicators: List[str] = Field(default_factory=list, description="Specific triggers fired in this dimension")
    explanation: str = Field(..., description="Explainable description of the dimensional deviation")
    evidence_event_ids: List[str] = Field(default_factory=list, description="Underlying evidence events")


class MultiDimensionalScores(BaseModel):
    """8-dimensional anomaly assessment vector."""
    temporal: float = Field(default=0.0, ge=0.0, le=1.0, description="Temporal pattern deviation")
    spatial: float = Field(default=0.0, ge=0.0, le=1.0, description="Spatial & boundary deviation")
    kinematic: float = Field(default=0.0, ge=0.0, le=1.0, description="Kinematic & velocity deviation")
    frequency: float = Field(default=0.0, ge=0.0, le=1.0, description="Event density & cadence deviation")
    event_type: float = Field(default=0.0, ge=0.0, le=1.0, description="Taxonomy & novel event deviation")
    behavioral: float = Field(default=0.0, ge=0.0, le=1.0, description="Composite behavioral shift")
    relational: float = Field(default=0.0, ge=0.0, le=1.0, description="Network relationship shift")
    contextual: float = Field(default=0.0, ge=0.0, le=1.0, description="Sector context deviation")


class AnomalyAttributionFactor(BaseModel):
    """Mathematically consistent contribution factor to final anomaly score."""
    factor: str = Field(..., description="Dimension name")
    score: float = Field(..., ge=0.0, le=1.0, description="Raw dimensional score")
    weight: float = Field(..., ge=0.0, le=1.0, description="Applied dimensional weight")
    contribution: float = Field(..., ge=0.0, le=1.0, description="Mathematical contribution (score * weight)")
    description: str = Field(..., description="Factor narrative")


class AnomalyAttribution(BaseModel):
    """Explainable attribution breakdown of top anomaly drivers."""
    primary_dimension: str = Field(..., description="Single highest contributing dimension")
    top_factors: List[AnomalyAttributionFactor] = Field(default_factory=list, description="Ranked factor contributions")


class AnomalyTrend(BaseModel):
    """Rate and direction of anomaly score progression."""
    previous: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Previous evaluation score")
    current: float = Field(..., ge=0.0, le=1.0, description="Current evaluation score")
    delta: float = Field(..., description="Score change (current - previous)")
    rate_of_change: float = Field(default=0.0, description="Velocity of change per observation window")
    direction: TrendDirection = Field(..., description="Trend direction: INCREASE, DECREASE, STABLE, UNKNOWN")


class AnomalyPersistence(BaseModel):
    """Persistence and recurrence metrics across historical windows."""
    state: AnomalyPersistenceState = Field(..., description="Persistence state: TRANSIENT, PERSISTENT, RECURRING, ESCALATING, DECLINING")
    elevated_windows: int = Field(default=0, ge=0, description="Total windows where anomaly was elevated")
    consecutive_windows: int = Field(default=0, ge=0, description="Consecutive windows in elevated state")
    peak_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Peak anomaly score observed")
    average_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Mean anomaly score across evaluated windows")


class AnomalySummary(BaseModel):
    """High-level summary of entity anomaly status."""
    score: float = Field(..., ge=0.0, le=1.0, description="Calibrated multi-dimensional aggregate anomaly score")
    level: AnomalyLevel = Field(..., description="Categorical rating: NOMINAL, LOW, MODERATE, HIGH, CRITICAL")
    state: AnomalyPersistenceState = Field(..., description="Persistence state")
    confirmation: AnomalyConfirmationLevel = Field(..., description="Evidence confirmation quality")
    lifecycle: AnomalyLifecycle = Field(default=AnomalyLifecycle.ACTIVE, description="Lifecycle progression")


class EvidenceLineage(BaseModel):
    """Complete traceability audit metadata."""
    event_ids: List[str] = Field(default_factory=list, description="All evaluated event IDs")
    entity_ids: List[str] = Field(default_factory=list, description="Involved entity IDs")
    baseline_window: Dict[str, Any] = Field(default_factory=dict, description="Historical baseline window details")
    analysis_window: Dict[str, Any] = Field(default_factory=dict, description="Current evaluation window details")
    source_reliability: Dict[str, float] = Field(default_factory=dict, description="Source reliability scores")


class SectorAnomalyHeatIndex(BaseModel):
    """Analytical heat index for a operational sector."""
    sector_id: str = Field(..., description="Sector identifier")
    anomaly_index: float = Field(..., ge=0.0, le=1.0, description="Aggregate sector anomaly heat index")
    entity_count: int = Field(..., ge=0, description="Total entities evaluated in sector")
    high_anomaly_entities: int = Field(..., ge=0, description="Count of entities with HIGH or CRITICAL anomaly")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in sector heat estimate")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Sector audit metadata")


class AnomalyHotspot(BaseModel):
    """Geospatial cluster of elevated anomaly activity."""
    centroid: Coordinates = Field(..., description="Hotspot central coordinate")
    radius_km: float = Field(..., ge=0.0, description="Hotspot radius in km")
    event_count: int = Field(..., ge=1, description="Anomalous events in hotspot")
    anomaly_index: float = Field(..., ge=0.0, le=1.0, description="Cluster anomaly intensity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Hotspot assessment confidence")
    primary_dimensions: List[str] = Field(default_factory=list, description="Top anomalous dimensions driving hotspot")


class AnomalyHistoryItem(BaseModel):
    """Chronological point-in-time anomaly record."""
    timestamp: datetime = Field(..., description="Observation timestamp (UTC)")
    score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score")
    level: AnomalyLevel = Field(..., description="Anomaly level")
    primary_dimension: str = Field(..., description="Primary driving dimension")
    status: str = Field(default="ACTIVE", description="Operational status")
    evidence_event_ids: List[str] = Field(default_factory=list, description="Evidence events")


class AnomalyHistoryResponse(BaseModel):
    """Response payload for GET /api/v1/intelligence/entities/{entity_id}/anomalies."""
    entity_id: str = Field(..., description="Target entity ID")
    anomalies: List[AnomalyHistoryItem] = Field(default_factory=list, description="Chronological anomaly history")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")


class AnomalyAnalyzeRequest(BaseModel):
    """Request payload for POST /api/v1/intelligence/anomalies/analyze."""
    entity_id: str = Field(..., description="Target entity identifier")
    events: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional raw or canonical events to analyze")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional sector or population baseline context")
    as_of: Optional[datetime] = Field(default=None, description="Deterministic evaluation reference timestamp")


class AnomalyAnalyzeResponse(BaseModel):
    """
    Master Phase 4 Anomaly & Risk Analysis Response.
    Delivers deep multi-dimensional anomaly assessment, attribution, persistence, trend,
    phase4-v1 risk model, calibrated confidence, four-tier assessment, and data lineage.
    """
    analysis_id: str = Field(..., description="Unique deterministic analysis identifier")
    entity_id: str = Field(..., description="Target entity identifier")
    timestamp: datetime = Field(..., description="Execution timestamp (UTC)")
    anomaly: AnomalySummary = Field(..., description="High-level anomaly rating, persistence, and confirmation")
    dimensions: MultiDimensionalScores = Field(..., description="8-dimensional anomaly score vector")
    dimension_details: Dict[str, DimensionScoreItem] = Field(default_factory=dict, description="Detailed breakdown per dimension")
    attribution: AnomalyAttribution = Field(..., description="Explainable mathematical factor attribution")
    trend: AnomalyTrend = Field(..., description="Anomaly progression rate and direction")
    persistence: AnomalyPersistence = Field(..., description="Persistence and recurrence analysis")
    risk: Phase4RiskProfile = Field(..., description="Phase 4 analytical risk dossier (phase4-v1)")
    confidence: Dict[str, Any] = Field(default_factory=dict, description="Calibrated confidence metrics")
    assessment: FourTierAssessment = Field(..., description="Strict four-tier intelligence assessment")
    evidence: EvidenceLineage = Field(..., description="Full evidence traceability lineage")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Audit and performance metadata")
