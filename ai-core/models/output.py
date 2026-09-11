"""
Output response models for NETRA Intelligence Core.
Defines strongly typed, machine-readable schemas consumed directly by the Operational Frontend.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from .common import ClassificationType, SeverityLevel, RiskLevel, RelationshipType


class RiskFactor(BaseModel):
    """An individual contributor to the explainable risk score."""
    factor: str = Field(..., description="Name of the risk factor (e.g. activity_deviation)")
    weight: float = Field(..., ge=0.0, le=1.0, description="Factor weight in the risk equation")
    contribution: float = Field(..., ge=0.0, le=1.0, description="Normalized score contribution (weight * normalized_value)")
    description: str = Field(..., description="Human-readable explanation of why this factor contributed")


class RiskBreakdown(BaseModel):
    """Explainable risk model output."""
    score: float = Field(..., ge=0.0, le=1.0, description="Aggregate risk score between 0.0 and 1.0")
    level: RiskLevel = Field(..., description="Categorical risk rating (LOW, MEDIUM, HIGH, CRITICAL)")
    factors: List[RiskFactor] = Field(default_factory=list, description="Explicit factor breakdown")


class ConfidenceBreakdown(BaseModel):
    """Component metrics supporting the overall confidence score."""
    data_completeness: float = Field(..., ge=0.0, le=1.0, description="Ratio of populated operational fields")
    historical_baseline_depth: float = Field(..., ge=0.0, le=1.0, description="Reliability score derived from sample size")
    signal_consistency: float = Field(..., ge=0.0, le=1.0, description="Logical consistency across sensors and telemetry")


class RelatedEntityOutput(BaseModel):
    """An entity related to the target situation with explicit relationship reasoning."""
    entity_id: str = Field(..., description="Identified entity ID")
    relationship: RelationshipType = Field(..., description="Type of detected relationship")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this detected link")
    details: Optional[str] = Field(default=None, description="Explanation for the association")


class RelatedEventOutput(BaseModel):
    """An event correlated with the target event."""
    event_id: str = Field(..., description="Correlated event ID")
    relationship: RelationshipType = Field(..., description="Nature of the correlation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the event relationship")
    details: Optional[str] = Field(default=None, description="Contextual note on correlation")


class IntelligenceAnalyzeResponse(BaseModel):
    """
    Primary output schema for NETRA Intelligence Core analysis.
    Machine-readable, schema-validated, and explainable for frontend and gateway consumption.
    """
    analysis_id: str = Field(..., description="Unique deterministic or traceable analysis identifier")
    timestamp: datetime = Field(..., description="Execution timestamp (UTC)")
    classification: ClassificationType = Field(..., description="Deterministic intelligence classification")
    severity: SeverityLevel = Field(..., description="Evaluated severity level")
    risk: RiskBreakdown = Field(..., description="Explainable risk breakdown")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Reliability of assessment given available data")
    confidence_breakdown: ConfidenceBreakdown = Field(..., description="Components of confidence score")
    related_entities: List[RelatedEntityOutput] = Field(default_factory=list, description="Detected entity relationships")
    related_events: List[RelatedEventOutput] = Field(default_factory=list, description="Detected event correlations")
    assessment: str = Field(..., description="Generated intelligence assessment distinguishing OBSERVED, INFERRED, UNCERTAIN")
    indicators: Dict[str, float] = Field(default_factory=dict, description="Normalized indicator metrics [0.0 - 1.0]")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Audit and operational metadata")
