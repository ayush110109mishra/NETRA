"""
Phase 6 Predictive Intelligence & Forecasting Data Schemas for NETRA.
Defines predictive targets, horizons, feature items, temporal state points,
trend metrics, forecast strategies, probabilistic estimates, uncertainty intervals,
explainability dossiers, and REST API contracts.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PredictiveTarget(str, Enum):
    """Supported analytical predictive forecast dimensions."""
    ACTIVITY_STATE = "ACTIVITY_STATE"
    ANOMALY_STATE = "ANOMALY_STATE"
    RISK_TREND = "RISK_TREND"
    SPATIAL_STATE = "SPATIAL_STATE"
    EVENT_TYPE_RECURRENCE = "EVENT_TYPE_RECURRENCE"
    BEHAVIORAL_STATE = "BEHAVIORAL_STATE"


class ForecastHorizon(str, Enum):
    """Analytical simulation horizons for forecast validity."""
    SHORT = "SHORT"    # 15–30 minutes
    MEDIUM = "MEDIUM"  # 1–6 hours
    LONG = "LONG"      # 12–24 hours


class ForecastState(str, Enum):
    """Categorical future states predicted by Phase 6."""
    # Activity & General
    STABLE = "STABLE"
    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    VOLATILE = "VOLATILE"
    # Anomaly
    NORMAL = "NORMAL"
    PERSISTENT = "PERSISTENT"
    ESCALATING = "ESCALATING"
    RESOLVING = "RESOLVING"
    # Risk
    RISING = "RISING"
    FALLING = "FALLING"
    # Spatial
    STABLE_REGION = "STABLE_REGION"
    EXPANDING = "EXPANDING"
    CONTRACTING = "CONTRACTING"
    SHIFTING = "SHIFTING"
    # Behavioral
    CONTINUATION = "CONTINUATION"
    REGIME_CHANGE = "REGIME_CHANGE"
    # Recurrence
    RECURRING = "RECURRING"
    NON_RECURRING = "NON_RECURRING"
    # Cold-Start / Fallback
    UNKNOWN = "UNKNOWN"


class ForecastLifecycleState(str, Enum):
    """Lifecycle status of an active or evaluated forecast."""
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    UPDATED = "UPDATED"
    EXPIRED = "EXPIRED"
    EVALUATED = "EVALUATED"


class DataSufficiency(str, Enum):
    """Sufficiency of historical evidence underpinning forecast."""
    INSUFFICIENT = "INSUFFICIENT"  # < 3 events -> UNKNOWN
    LIMITED = "LIMITED"            # 3-5 events -> Capped confidence
    SUFFICIENT = "SUFFICIENT"      # > 5 events -> Normal forecasting


class EpistemicStatus(str, Enum):
    """Epistemic boundary categorization."""
    OBSERVED = "OBSERVED"
    FUSED = "FUSED"
    INFERRED = "INFERRED"
    PREDICTED = "PREDICTED"
    UNCERTAIN = "UNCERTAIN"


class FeatureItem(BaseModel):
    """Single engineered analytical feature with provenance."""
    feature_name: str = Field(..., description="Feature identifier (e.g. activity_trend_slope)")
    value: float = Field(..., description="Raw computed feature value")
    normalized_value: float = Field(..., ge=0.0, le=1.0, description="Value normalized to [0.0 - 1.0]")
    derived_from: List[str] = Field(default_factory=list, description="IDs of source events/entities/fusions")
    source_evidence: List[str] = Field(default_factory=list, description="IDs of underlying raw observations")


class TemporalStatePoint(BaseModel):
    """Point-in-time state measurement in an irregular time sequence."""
    timestamp: datetime = Field(..., description="UTC timestamp of state observation")
    value: float = Field(..., description="Observed quantitative metric")
    state: str = Field(..., description="State label at this timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Contextual telemetry")


class TemporalStateSequence(BaseModel):
    """Irregular time-series sequence for an entity or sector."""
    entity_id: str = Field(..., description="Target entity ID")
    points: List[TemporalStatePoint] = Field(default_factory=list, description="Chronologically ordered state points")
    sample_count: int = Field(default=0, ge=0, description="Total points in sequence")
    sampling_regularity: float = Field(default=1.0, ge=0.0, le=1.0, description="Index of interval regularity")


class TrendMetrics(BaseModel):
    """Mathematical trend indicators across historical observations."""
    slope: float = Field(..., description="Linear regression slope across observation sequence")
    direction: str = Field(..., description="Trend direction (RISING, FALLING, STABLE, VOLATILE)")
    strength: float = Field(..., ge=0.0, le=1.0, description="Normalized trend strength [0.0 - 1.0]")
    persistence: float = Field(..., ge=0.0, le=1.0, description="Trend persistence ratio across windows")
    acceleration: float = Field(default=0.0, description="Second derivative / rate of change acceleration")
    volatility: float = Field(..., ge=0.0, le=1.0, description="Standard deviation volatility index")
    is_regime_change: bool = Field(default=False, description="Whether recent trend breaks historical regime")


class ForecastInterval(BaseModel):
    """Quantified forecast confidence interval."""
    lower: float = Field(..., ge=0.0, le=1.0, description="Lower heuristic confidence bound")
    upper: float = Field(..., ge=0.0, le=1.0, description="Upper heuristic confidence bound")
    interval_type: str = Field(default="heuristic", description="Interval methodology (heuristic or statistical)")


class PredictiveForecast(BaseModel):
    """Core future-state projection with probability and uncertainty."""
    target: PredictiveTarget = Field(..., description="Target analytical dimension")
    current_state: str = Field(..., description="Observed current analytical state")
    forecast_state: str = Field(..., description="Projected future analytical state")
    horizon: ForecastHorizon = Field(..., description="Forecast horizon (SHORT, MEDIUM, LONG)")
    probability: float = Field(..., ge=0.0, le=1.0, description="Estimated probability of projected state")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Calibrated confidence score [0.0 - 1.0]")
    uncertainty: float = Field(..., ge=0.0, le=1.0, description="Quantified residual uncertainty [0.0 - 1.0]")
    interval: ForecastInterval = Field(..., description="Confidence interval bounds")
    model_agreement: float = Field(default=1.0, ge=0.0, le=1.0, description="Ensemble agreement ratio [0.0 - 1.0]")
    strategy_used: str = Field(..., description="Primary forecasting strategy employed")
    data_sufficiency: DataSufficiency = Field(..., description="Sufficiency of historical data")
    lifecycle_state: ForecastLifecycleState = Field(default=ForecastLifecycleState.ACTIVE, description="Lifecycle state")


class PredictiveAssessment(BaseModel):
    """Epistemic five-tier intelligence assessment (adding PREDICTED)."""
    summary: str = Field(..., description="Operational summary of forecast conclusions")
    observed: List[str] = Field(default_factory=list, description="Direct telemetry observations")
    fused: List[str] = Field(default_factory=list, description="Cross-source corroborated findings")
    inferred: List[str] = Field(default_factory=list, description="Analytical patterns and trend inferences")
    predicted: List[str] = Field(default_factory=list, description="Probabilistic future-state forecasts")
    uncertain: List[str] = Field(default_factory=list, description="Known uncertainties, gaps, or contradictions")
    epistemic_ledger: Dict[str, List[str]] = Field(default_factory=dict, description="Category map of all statements")


class PredictionExplanation(BaseModel):
    """Structured explainability dossier answering Why, What Supports, and What Invalidates."""
    assessment: str = Field(..., description="Narrative rationale for the forecast")
    supporting_factors: List[str] = Field(default_factory=list, description="Key signals supporting forecast")
    limiting_factors: List[str] = Field(default_factory=list, description="Factors dampening confidence or probability")
    invalidation_conditions: List[str] = Field(default_factory=list, description="Conditions that would invalidate forecast")
    feature_importance: Dict[str, float] = Field(default_factory=dict, description="Mathematical contribution by feature")


class PredictionAnalyzeRequest(BaseModel):
    """Request payload for entity predictive intelligence analysis."""
    entity_id: str = Field(..., description="Target synthetic entity identifier")
    target: PredictiveTarget = Field(default=PredictiveTarget.ACTIVITY_STATE, description="Forecasting target")
    horizon: ForecastHorizon = Field(default=ForecastHorizon.SHORT, description="Forecasting horizon")
    as_of: Optional[datetime] = Field(default=None, description="Deterministic reference evaluation timestamp")
    include_phase5_fusion: bool = Field(default=True, description="Whether to include multi-source fused evidence")
    custom_events: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional synthetic events override")


class PredictionAnalyzeResponse(BaseModel):
    """Master Phase 6 Predictive Intelligence Response Envelope."""
    schema_version: str = Field(default="phase6-v1", description="Phase 6 response schema version")
    prediction_id: str = Field(..., description="Deterministic prediction run identifier")
    status: str = Field(default="SUCCESS", description="Execution status")
    entity_id: str = Field(..., description="Analyzed entity ID")
    target: PredictiveTarget = Field(..., description="Target analytical dimension")
    horizon: ForecastHorizon = Field(..., description="Analytical horizon")
    forecast: PredictiveForecast = Field(..., description="Probabilistic future state forecast")
    assessment: PredictiveAssessment = Field(..., description="Five-tier epistemic intelligence assessment")
    features: List[FeatureItem] = Field(default_factory=list, description="Engineered features with provenance")
    trend_metrics: TrendMetrics = Field(..., description="Mathematical trend indicators")
    explanation: PredictionExplanation = Field(..., description="Explainable factor attribution dossier")
    candidate_model_forecasts: Dict[str, str] = Field(default_factory=dict, description="Candidate strategy outputs")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Execution and audit metadata")


class EntityForecastResponse(BaseModel):
    """Multi-target forecast summary for an entity dashboard."""
    entity_id: str = Field(..., description="Entity identifier")
    current_forecasts: Dict[str, PredictiveForecast] = Field(default_factory=dict, description="Forecasts keyed by target")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Mean forecast confidence")
    overall_uncertainty: float = Field(..., ge=0.0, le=1.0, description="Mean forecast uncertainty")
    as_of: datetime = Field(..., description="Evaluation timestamp")


class EntityPredictionsHistoryResponse(BaseModel):
    """Historical timeline of generated predictions for an entity."""
    entity_id: str = Field(..., description="Entity identifier")
    predictions: List[PredictionAnalyzeResponse] = Field(default_factory=list, description="Chronological predictions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="History metadata")


class ForecastEvaluationItem(BaseModel):
    """Synthetic accuracy evaluation record comparing forecast against actual outcome."""
    prediction_id: str = Field(..., description="Prediction identifier")
    target: str = Field(..., description="Forecast target")
    forecast_state: str = Field(..., description="Predicted state")
    actual_state: str = Field(..., description="Observed outcome state")
    is_directionally_correct: bool = Field(..., description="Whether trajectory direction matched")
    absolute_error: float = Field(..., ge=0.0, description="Quantitative absolute error")


class ForecastEvaluationResponse(BaseModel):
    """Aggregated synthetic forecasting performance metrics."""
    total_evaluated: int = Field(default=0, ge=0, description="Number of evaluated synthetic forecasts")
    mean_absolute_error: float = Field(default=0.0, ge=0.0, description="Mean absolute error")
    directional_accuracy: float = Field(default=1.0, ge=0.0, le=1.0, description="Directional accuracy ratio")
    evaluations: List[ForecastEvaluationItem] = Field(default_factory=list, description="Evaluation items")
