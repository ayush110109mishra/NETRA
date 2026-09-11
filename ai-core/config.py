"""
NETRA Intelligence Core - Configuration
Defines configurable thresholds, weights, and operational parameters for Phase 1, Phase 2, and Phase 3.
All scoring logic references these settings to allow fine-tuning without hardcoding.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class ClassificationThresholds:
    """Thresholds for intelligence classification based on combined indicator score."""
    normal_max: float = 0.25
    unusual_max: float = 0.50
    anomalous_max: float = 0.75
    min_confidence_for_definitive: float = 0.35  # Below this, evaluates to UNKNOWN


@dataclass(frozen=True)
class SeverityThresholds:
    """Thresholds for severity level mapping."""
    info_max: float = 0.20
    low_max: float = 0.40
    medium_max: float = 0.65
    high_max: float = 0.85


@dataclass(frozen=True)
class RiskWeights:
    """Weights for the explainable risk factors. Must sum to 1.0."""
    activity_deviation: float = 0.35
    speed_anomaly: float = 0.25
    event_severity_baseline: float = 0.20
    relationship_density: float = 0.20

    def validate(self) -> None:
        total = (
            self.activity_deviation
            + self.speed_anomaly
            + self.event_severity_baseline
            + self.relationship_density
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Risk weights must sum to 1.0, got {total}")


@dataclass(frozen=True)
class ConfidenceWeights:
    """Weights for confidence calculation. Must sum to 1.0."""
    data_completeness: float = 0.40
    historical_baseline_depth: float = 0.35
    signal_consistency: float = 0.25

    def validate(self) -> None:
        total = (
            self.data_completeness
            + self.historical_baseline_depth
            + self.signal_consistency
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Confidence weights must sum to 1.0, got {total}")


# --- Phase 2: Multi-Event Intelligence Configurations ---

@dataclass(frozen=True)
class CorrelationWeights:
    """Weights for multi-dimensional event correlation. Must sum to 1.0."""
    temporal: float = 0.25
    spatial: float = 0.20
    entity: float = 0.30
    type_similarity: float = 0.15
    attribute_similarity: float = 0.10

    def validate(self) -> None:
        total = (
            self.temporal
            + self.spatial
            + self.entity
            + self.type_similarity
            + self.attribute_similarity
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Correlation weights must sum to 1.0, got {total}")


@dataclass(frozen=True)
class TemporalConfig:
    """Temporal analysis windows and thresholds."""
    proximity_window_seconds: float = 7200.0      # 2 hours max proximity window
    sequence_window_seconds: float = 1800.0       # 30 mins sequential window
    burst_window_seconds: float = 600.0           # 10 mins burst window
    burst_min_events: int = 3                     # Min events to classify as burst
    periodic_tolerance_seconds: float = 120.0     # 2 mins interval tolerance for recurrence


@dataclass(frozen=True)
class SpatialConfig:
    """Spatial intelligence thresholds (in kilometers)."""
    same_location_km: float = 0.20                # Points within 200m are same location
    proximity_km: float = 15.0                    # Proximity boundary for candidate pairs
    max_cluster_distance_km: float = 20.0         # Spatial boundary for single cluster


@dataclass(frozen=True)
class DeduplicationConfig:
    """Event deduplication parameters."""
    enabled: bool = True
    exact_time_window_seconds: float = 5.0        # Time window for exact duplicates
    near_time_window_seconds: float = 60.0        # Time window for near duplicates
    exact_distance_km: float = 0.05               # 50m for exact duplicate
    near_distance_km: float = 0.20                # 200m for near duplicate


@dataclass(frozen=True)
class ClusteringConfig:
    """Event clustering parameters."""
    min_correlation_for_link: float = 0.60        # Min correlation score to form link
    min_cluster_size: int = 2                     # Min events to form a cluster


@dataclass(frozen=True)
class RelationshipStrengthBands:
    """Relationship strength bands."""
    very_weak_max: float = 0.24
    weak_max: float = 0.49
    moderate_max: float = 0.74
    strong_max: float = 0.89


# --- Phase 3: Entity Intelligence Configurations ---

@dataclass(frozen=True)
class EntityConfig:
    """Entity lifecycle, observation thresholds, and window parameters."""
    min_observations_for_baseline: int = 3       # Cold start threshold (< 3 is INSUFFICIENT_HISTORY)
    active_window_hours: float = 48.0             # Observed within 48h -> ACTIVE
    recently_active_window_hours: float = 96.0    # Observed within 96h -> RECENTLY_ACTIVE
    stale_window_hours: float = 168.0             # Observed within 7 days -> INACTIVE, beyond -> STALE
    recent_analysis_window_hours: float = 24.0    # Window for detecting recent behavioral shifts
    spatial_expansion_threshold_ratio: float = 1.5 # Radius expansion factor triggering spatial anomaly


@dataclass(frozen=True)
class EntityRiskWeights:
    """Weights for the explainable entity risk model. Must sum to 1.0."""
    event_risk: float = 0.30
    behavioral_deviation: float = 0.25
    anomaly_score: float = 0.25
    cluster_context: float = 0.20

    def validate(self) -> None:
        total = (
            self.event_risk
            + self.behavioral_deviation
            + self.anomaly_score
            + self.cluster_context
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Entity risk weights must sum to 1.0, got {total}")


@dataclass(frozen=True)
class EntityConfidenceWeights:
    """Weights for the entity confidence model. Must sum to 1.0."""
    observation_depth: float = 0.35
    time_span_depth: float = 0.25
    completeness: float = 0.25
    source_reliability: float = 0.15

    def validate(self) -> None:
        total = (
            self.observation_depth
            + self.time_span_depth
            + self.completeness
            + self.source_reliability
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Entity confidence weights must sum to 1.0, got {total}")


# --- Phase 4: Advanced Anomaly & Risk Configurations ---

@dataclass(frozen=True)
class AnomalyDimensionWeights:
    """Weights for 8-dimensional anomaly aggregation. Must sum to 1.0."""
    temporal: float = 0.12
    spatial: float = 0.18
    kinematic: float = 0.18
    frequency: float = 0.12
    event_type: float = 0.10
    behavioral: float = 0.12
    relational: float = 0.10
    contextual: float = 0.08

    def validate(self) -> None:
        total = (
            self.temporal
            + self.spatial
            + self.kinematic
            + self.frequency
            + self.event_type
            + self.behavioral
            + self.relational
            + self.contextual
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Anomaly dimension weights must sum to 1.0, got {total}")


@dataclass(frozen=True)
class AnomalyClassificationThresholds:
    """Configurable categorical thresholds for anomaly normalization."""
    nominal_max: float = 0.24
    low_max: float = 0.49
    moderate_max: float = 0.74
    high_max: float = 0.89
    critical_min: float = 0.90


@dataclass(frozen=True)
class Phase4RiskWeights:
    """Weights for Phase 4 explainable risk model (phase4-v1). Must sum to 1.0."""
    event_risk: float = 0.20
    behavioral_deviation: float = 0.15
    anomaly_score: float = 0.25
    cluster_context: float = 0.15
    anomaly_persistence: float = 0.10
    anomaly_trend: float = 0.10
    evidence_quality: float = 0.05

    def validate(self) -> None:
        total = (
            self.event_risk
            + self.behavioral_deviation
            + self.anomaly_score
            + self.cluster_context
            + self.anomaly_persistence
            + self.anomaly_trend
            + self.evidence_quality
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Phase 4 risk weights must sum to 1.0, got {total}")


@dataclass(frozen=True)
class PersistenceConfig:
    """Thresholds for assessing anomaly persistence and recurrence."""
    transient_max_windows: int = 1
    persistent_min_windows: int = 2
    escalating_rate_threshold: float = 0.15
    declining_rate_threshold: float = -0.15


@dataclass(frozen=True)
class HysteresisConfig:
    """Buffer to prevent rapid oscillation in risk state machine transitions."""
    buffer: float = 0.03


# --- Phase 5: Multi-Source Intelligence Fusion Configurations ---

@dataclass(frozen=True)
class SourceReliabilityWeights:
    """Weights for calculating source reliability. Must sum to 1.0."""
    declared_reliability: float = 0.35
    historical_consistency: float = 0.25
    observation_completeness: float = 0.20
    stability: float = 0.20

    def validate(self) -> None:
        total = (
            self.declared_reliability
            + self.historical_consistency
            + self.observation_completeness
            + self.stability
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Source reliability weights must sum to 1.0, got {total}")


@dataclass(frozen=True)
class FusionWeights:
    """Weights for the explainable evidence fusion model. Must sum to 1.0."""
    source_reliability: float = 0.25
    temporal_agreement: float = 0.20
    spatial_agreement: float = 0.20
    corroboration: float = 0.15
    evidence_quality: float = 0.10
    completeness: float = 0.10

    def validate(self) -> None:
        total = (
            self.source_reliability
            + self.temporal_agreement
            + self.spatial_agreement
            + self.corroboration
            + self.evidence_quality
            + self.completeness
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Fusion weights must sum to 1.0, got {total}")


@dataclass(frozen=True)
class TemporalAlignmentConfig:
    """Temporal fusion thresholds and tolerances."""
    max_fusion_window_seconds: float = 300.0      # 5 minutes maximum fusion window
    near_alignment_window_seconds: float = 60.0   # 1 minute for near-simultaneous fusion
    clock_skew_tolerance_seconds: float = 10.0    # 10s allowable clock skew
    stale_observation_threshold_seconds: float = 3600.0  # 1 hour stale threshold


@dataclass(frozen=True)
class SpatialAlignmentConfig:
    """Spatial alignment thresholds in kilometers."""
    agreement_max_distance_km: float = 0.50       # 500m agreement threshold
    partial_agreement_max_distance_km: float = 5.0 # 5km partial agreement threshold
    conflict_min_distance_km: float = 5.0          # Distances > 5km indicate spatial conflict


@dataclass(frozen=True)
class EntityResolutionConfig:
    """Entity resolution match thresholds."""
    match_threshold: float = 0.70                 # Below 0.70 -> UNRESOLVED
    ambiguity_margin: float = 0.10                # Difference between top 2 candidates < 0.10 -> AMBIGUOUS


@dataclass(frozen=True)
class ConflictThresholds:
    """Discrepancy thresholds for multi-source contradiction detection."""
    position_conflict_km: float = 5.0
    speed_conflict_kmh: float = 40.0
    heading_conflict_deg: float = 60.0


# --- Phase 6: Predictive Intelligence & Forecasting Configurations ---

@dataclass(frozen=True)
class PredictionWeights:
    """Weights for the explainable forecast probability model. Must sum to 1.0."""
    recurrence: float = 0.25
    trend_strength: float = 0.20
    persistence: float = 0.15
    evidence_quality: float = 0.15
    fusion_confidence: float = 0.10
    data_completeness: float = 0.10
    model_agreement: float = 0.05

    def validate(self) -> None:
        total = (
            self.recurrence
            + self.trend_strength
            + self.persistence
            + self.evidence_quality
            + self.fusion_confidence
            + self.data_completeness
            + self.model_agreement
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Prediction weights must sum to 1.0, got {total}")


@dataclass(frozen=True)
class PredictionHorizonConfig:
    """Configurable analytical simulation horizons in seconds."""
    short_horizon_seconds: float = 1800.0     # 30 minutes
    medium_horizon_seconds: float = 21600.0   # 6 hours
    long_horizon_seconds: float = 86400.0     # 24 hours


@dataclass(frozen=True)
class PredictionGatingConfig:
    """Evidence sufficiency, cold start, and regime change thresholds."""
    cold_start_threshold: int = 3             # Observations < 3 -> UNKNOWN
    limited_history_threshold: int = 5        # Observations 3-5 -> LIMITED
    volatility_threshold: float = 0.25        # High volatility threshold
    regime_change_slope_delta: float = 0.20   # Recent vs historical slope delta triggering REGIME_CHANGE


@dataclass(frozen=True)
class PredictionHysteresisConfig:
    """Buffer to prevent forecast oscillation around boundary thresholds."""
    buffer: float = 0.03


@dataclass
class NetraConfig:
    """Master configuration container for NETRA Intelligence Core."""
    app_name: str = "NETRA Intelligence Core"
    version: str = "6.0.0"
    mode: str = "SIMULATION"
    data_classification: str = "SYNTHETIC"
    
    # Phase 1 components
    classification: ClassificationThresholds = field(default_factory=ClassificationThresholds)
    severity: SeverityThresholds = field(default_factory=SeverityThresholds)
    risk_weights: RiskWeights = field(default_factory=RiskWeights)
    confidence_weights: ConfidenceWeights = field(default_factory=ConfidenceWeights)
    spatial_proximity_km_threshold: float = 15.0
    temporal_proximity_seconds_threshold: float = 7200.0

    # Phase 2 components
    correlation_weights: CorrelationWeights = field(default_factory=CorrelationWeights)
    temporal: TemporalConfig = field(default_factory=TemporalConfig)
    spatial: SpatialConfig = field(default_factory=SpatialConfig)
    deduplication: DeduplicationConfig = field(default_factory=DeduplicationConfig)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    relationship_strength: RelationshipStrengthBands = field(default_factory=RelationshipStrengthBands)

    # Phase 3 components
    entity: EntityConfig = field(default_factory=EntityConfig)
    entity_risk_weights: EntityRiskWeights = field(default_factory=EntityRiskWeights)
    entity_confidence_weights: EntityConfidenceWeights = field(default_factory=EntityConfidenceWeights)

    # Phase 4 components
    anomaly_weights: AnomalyDimensionWeights = field(default_factory=AnomalyDimensionWeights)
    anomaly_thresholds: AnomalyClassificationThresholds = field(default_factory=AnomalyClassificationThresholds)
    phase4_risk_weights: Phase4RiskWeights = field(default_factory=Phase4RiskWeights)
    persistence: PersistenceConfig = field(default_factory=PersistenceConfig)
    hysteresis: HysteresisConfig = field(default_factory=HysteresisConfig)

    # Phase 5 components
    source_reliability_weights: SourceReliabilityWeights = field(default_factory=SourceReliabilityWeights)
    fusion_weights: FusionWeights = field(default_factory=FusionWeights)
    temporal_alignment: TemporalAlignmentConfig = field(default_factory=TemporalAlignmentConfig)
    spatial_alignment: SpatialAlignmentConfig = field(default_factory=SpatialAlignmentConfig)
    entity_resolution: EntityResolutionConfig = field(default_factory=EntityResolutionConfig)
    conflict: ConflictThresholds = field(default_factory=ConflictThresholds)

    # Phase 6 components
    prediction_weights: PredictionWeights = field(default_factory=PredictionWeights)
    prediction_horizons: PredictionHorizonConfig = field(default_factory=PredictionHorizonConfig)
    prediction_gating: PredictionGatingConfig = field(default_factory=PredictionGatingConfig)
    prediction_hysteresis: PredictionHysteresisConfig = field(default_factory=PredictionHysteresisConfig)

    def __post_init__(self):
        self.risk_weights.validate()
        self.confidence_weights.validate()
        self.correlation_weights.validate()
        self.entity_risk_weights.validate()
        self.entity_confidence_weights.validate()
        self.anomaly_weights.validate()
        self.phase4_risk_weights.validate()
        self.source_reliability_weights.validate()
        self.fusion_weights.validate()
        self.prediction_weights.validate()


# Global default configuration instance
default_config = NetraConfig()


