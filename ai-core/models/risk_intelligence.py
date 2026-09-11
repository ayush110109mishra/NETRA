"""
Phase 4 Risk Intelligence Data Schemas for NETRA.
Defines versioned Phase 4 risk models (phase4-v1), factor breakdowns,
hysteresis risk states, risk persistence, and historical risk timelines.
"""

from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

from models.common import RiskLevel


class RiskTrendDirection(str, Enum):
    """Directional trend of analytical risk over time."""
    RISING = "RISING"
    FALLING = "FALLING"
    STABLE = "STABLE"
    VOLATILE = "VOLATILE"
    UNKNOWN = "UNKNOWN"


class RiskState(str, Enum):
    """Hysteresis-buffered operational risk state."""
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class Phase4RiskFactor(BaseModel):
    """Individual factor contribution to phase4-v1 risk model."""
    name: str = Field(..., description="Factor name (e.g. anomaly, behavioral_deviation, persistence)")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized factor score [0.0 - 1.0]")
    weight: float = Field(..., ge=0.0, le=1.0, description="Configured factor weight")
    contribution: float = Field(..., ge=0.0, le=1.0, description="Weighted contribution to final risk")
    description: str = Field(..., description="Explainable description of the factor's impact")


class RiskTrendProfile(BaseModel):
    """Trend and volatility analysis of analytical risk."""
    direction: RiskTrendDirection = Field(..., description="Overall trend direction")
    delta: float = Field(..., description="Risk score change from previous evaluation")
    volatility: float = Field(default=0.0, ge=0.0, le=1.0, description="Standard deviation / volatility of recent scores")
    previous_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Previous evaluation score")
    current_score: float = Field(..., ge=0.0, le=1.0, description="Current evaluation score")


class RiskPersistenceProfile(BaseModel):
    """Duration and consistency of elevated risk conditions."""
    elevated_windows: int = Field(default=0, ge=0, description="Total windows where risk exceeded normal threshold")
    consecutive_windows: int = Field(default=0, ge=0, description="Consecutive elevated risk windows")
    peak_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Maximum risk score observed across history")
    average_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="Mean risk score across evaluation windows")
    duration_hours: float = Field(default=0.0, ge=0.0, description="Estimated duration of current risk state in hours")


class Phase4RiskProfile(BaseModel):
    """Complete Phase 4 analytical risk dossier (phase4-v1)."""
    score: float = Field(..., ge=0.0, le=1.0, description="Aggregate calibrated risk score [0.0 - 1.0]")
    level: RiskLevel = Field(..., description="Categorical risk level: LOW, MEDIUM, HIGH, CRITICAL")
    state: RiskState = Field(..., description="Hysteresis-buffered risk state: NORMAL, ELEVATED, HIGH, CRITICAL")
    trend: RiskTrendDirection = Field(..., description="Risk trend: RISING, FALLING, STABLE, VOLATILE")
    model_version: str = Field(default="phase4-v1", description="Risk model algorithm version")
    factors: List[Phase4RiskFactor] = Field(default_factory=list, description="Mathematically consistent factor breakdown")
    persistence: RiskPersistenceProfile = Field(..., description="Risk persistence metrics")


class RiskHistoryItem(BaseModel):
    """Chronological point-in-time risk snapshot for timeline rendering."""
    timestamp: datetime = Field(..., description="Evaluation timestamp (UTC)")
    risk: float = Field(..., ge=0.0, le=1.0, description="Analytical risk score")
    anomaly: float = Field(..., ge=0.0, le=1.0, description="Co-occurring anomaly score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Evidence confidence score")
    state: RiskState = Field(default=RiskState.NORMAL, description="Risk state at evaluation time")


class RiskHistoryResponse(BaseModel):
    """Response payload for GET /api/v1/intelligence/entities/{entity_id}/risk-history."""
    entity_id: str = Field(..., description="Target entity ID")
    history: List[RiskHistoryItem] = Field(default_factory=list, description="Chronological risk history points")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
