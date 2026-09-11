"""
Phase 7 Ask NETRA Data Models & API Schemas.
Defines query intents, epistemic tiers, query validation types, parsed queries,
execution plan steps, grounded claims, epistemic ledger, and API request/response contracts.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class QueryIntent(str, Enum):
    """16 Supported Natural Language Query Intents for Ask NETRA."""
    STATUS = "STATUS"
    ENTITY_PROFILE = "ENTITY_PROFILE"
    TIMELINE = "TIMELINE"
    WHAT_CHANGED = "WHAT_CHANGED"
    ANOMALY = "ANOMALY"
    RISK = "RISK"
    WHY = "WHY"
    TREND = "TREND"
    FORECAST = "FORECAST"
    SOURCE_SUPPORT = "SOURCE_SUPPORT"
    CONFLICT = "CONFLICT"
    EVIDENCE = "EVIDENCE"
    COMPARISON = "COMPARISON"
    RELATIONSHIP = "RELATIONSHIP"
    SCENARIO = "SCENARIO"
    HELP = "HELP"


class EpistemicTier(str, Enum):
    """5-Tier Epistemic Ledger for Claim Grounding."""
    OBSERVED = "OBSERVED"      # Direct raw sensor / event telemetry
    FUSED = "FUSED"            # Corroborated cross-sensor consensus observations
    INFERRED = "INFERRED"      # Derived analytical metrics (risk, anomaly scores, drift)
    PREDICTED = "PREDICTED"    # Future forecasts with horizons and probabilities
    UNCERTAIN = "UNCERTAIN"    # Information gaps, conflicting telemetry, cold starts


class QueryValidationStatus(str, Enum):
    """Query Validation and Gating Statuses."""
    VALID = "VALID"
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    AMBIGUOUS_QUERY = "AMBIGUOUS_QUERY"
    UNSUPPORTED_QUERY = "UNSUPPORTED_QUERY"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    TIME_WINDOW_INVALID = "TIME_WINDOW_INVALID"


class TimeRangeFilter(BaseModel):
    """Temporal filter parameters for query execution."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    relative_duration_seconds: Optional[float] = None
    label: Optional[str] = None


class StructuredFilters(BaseModel):
    """Attribute-based filters extracted from query phrasing."""
    severity_min: Optional[str] = None
    risk_min: Optional[float] = None
    anomaly_min: Optional[float] = None
    source_type: Optional[str] = None
    event_types: List[str] = Field(default_factory=list)
    limit: Optional[int] = 50


class ParsedQuery(BaseModel):
    """Structured intermediate representation of a natural language question."""
    query_id: str
    raw_query: str
    intent: QueryIntent
    intent_confidence: float = Field(ge=0.0, le=1.0)
    primary_entity_id: Optional[str] = None
    secondary_entity_id: Optional[str] = None
    sector_id: Optional[str] = None
    time_range: Optional[TimeRangeFilter] = None
    filters: StructuredFilters = Field(default_factory=StructuredFilters)
    is_followup: bool = False
    resolved_references: Dict[str, str] = Field(default_factory=dict)
    parsed_at: datetime


class QueryPlanStep(BaseModel):
    """Single execution step in a query plan."""
    step_id: str
    engine: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)


class QueryPlan(BaseModel):
    """Structured multi-step execution plan mapping intent to Phase 1-6 engines."""
    plan_id: str
    query_id: str
    intent: QueryIntent
    steps: List[QueryPlanStep] = Field(default_factory=list)
    validation_status: QueryValidationStatus = QueryValidationStatus.VALID
    validation_message: Optional[str] = None
    estimated_cost_ms: float = 0.0


class EvidenceReference(BaseModel):
    """Grounded citation pointing to concrete underlying evidence."""
    evidence_id: str
    epistemic_tier: EpistemicTier
    source: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ClaimItem(BaseModel):
    """Structured proposition or conclusion backed by evidence citations."""
    statement: str
    epistemic_tier: EpistemicTier
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class EpistemicLedger(BaseModel):
    """5-Tier classification ledger of all evidence surfaced during query answering."""
    observed: List[EvidenceReference] = Field(default_factory=list)
    fused: List[EvidenceReference] = Field(default_factory=list)
    inferred: List[EvidenceReference] = Field(default_factory=list)
    predicted: List[EvidenceReference] = Field(default_factory=list)
    uncertain: List[EvidenceReference] = Field(default_factory=list)

    @property
    def total_evidence_count(self) -> int:
        return (
            len(self.observed)
            + len(self.fused)
            + len(self.inferred)
            + len(self.predicted)
            + len(self.uncertain)
        )


class AskAnswer(BaseModel):
    """Structured, evidence-grounded response answering the operator's query."""
    headline: str
    summary: str
    key_findings: List[str] = Field(default_factory=list)
    claims: List[ClaimItem] = Field(default_factory=list)
    evidence_ledger: EpistemicLedger = Field(default_factory=EpistemicLedger)
    uncertainties: List[str] = Field(default_factory=list)
    caveats: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0.0, le=1.0, default=0.85)


class AskNetraRequest(BaseModel):
    """Operator request payload for Ask NETRA natural language intelligence."""
    query: str
    session_id: Optional[str] = None
    as_of: Optional[datetime] = None
    active_entity_id: Optional[str] = None
    context_override: Optional[Dict[str, Any]] = None


class AskNetraResponse(BaseModel):
    """Complete REST response payload for Ask NETRA query execution."""
    schema_version: str = "phase7-v1"
    query_id: str
    session_id: str
    as_of: datetime
    parsed_query: ParsedQuery
    execution_plan: QueryPlan
    answer: AskAnswer
    execution_time_ms: float
    provenance: Dict[str, Any] = Field(default_factory=dict)


class ParseResponse(BaseModel):
    """REST response payload for query parsing and execution planning without execution."""
    parsed_query: ParsedQuery
    execution_plan: QueryPlan
    validation_status: QueryValidationStatus
    validation_message: Optional[str] = None


class CapabilityItem(BaseModel):
    """Description of an individual Ask NETRA query capability."""
    intent: QueryIntent
    description: str
    supported_engines: List[str]
    example_queries: List[str]


class CapabilitiesResponse(BaseModel):
    """REST response enumerating Ask NETRA supported intents, tiers, and capabilities."""
    schema_version: str = "phase7-v1"
    supported_intents: List[CapabilityItem]
    epistemic_tiers: List[str]
    version: str = "7.0.0"


class ExampleQueryItem(BaseModel):
    """Single cataloged example operational query."""
    category: str
    query: str
    intent: QueryIntent
    description: str


class ExamplesResponse(BaseModel):
    """Catalog of operational query examples."""
    examples: List[ExampleQueryItem]
