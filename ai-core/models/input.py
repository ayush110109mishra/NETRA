"""
Input request models for NETRA Intelligence Core.
Defines strongly typed schemas with validation for events, entities, telemetry, and context.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from .common import Coordinates, Allegiance, SeverityLevel


class EventInput(BaseModel):
    """Input specification for an observed synthetic event."""
    event_id: str = Field(..., description="Unique event identifier (e.g., EVT-001)")
    event_type: str = Field(..., description="Event type classification (e.g., movement, sensor_ping, patrol_deviation)")
    description: str = Field(..., description="Detailed synthetic observation description")
    timestamp: datetime = Field(..., description="ISO-8601 observation timestamp")
    priority_hint: Optional[SeverityLevel] = Field(default=None, description="Optional upstream priority hint")


class EntityInput(BaseModel):
    """Input specification for an associated synthetic entity."""
    entity_id: str = Field(..., description="Unique entity identifier (e.g., ENTITY-047)")
    entity_type: str = Field(..., description="Entity platform type (e.g., vehicle, aircraft, patrol_unit, vessel)")
    callsign: Optional[str] = Field(default=None, description="Optional tactical callsign")
    allegiance: Allegiance = Field(default=Allegiance.UNKNOWN, description="Simulated allegiance marker")


class AttributesInput(BaseModel):
    """Realtime synthetic telemetry attributes."""
    speed: float = Field(0.0, ge=0.0, le=2000.0, description="Observed speed in km/h")
    activity_level: float = Field(..., ge=0.0, le=1.0, description="Normalized activity level [0.0 - 1.0]")
    heading_deg: Optional[float] = Field(default=None, ge=0.0, le=360.0, description="Heading in degrees")
    sensor_count: Optional[int] = Field(default=1, ge=0, description="Active sensor count observing this signature")
    signal_strength_dbm: Optional[float] = Field(default=None, description="Signal strength in dBm")
    extra: Optional[Dict[str, Any]] = Field(default=None, description="Flexible domain-specific attributes")


class HistoricalContextInput(BaseModel):
    """Baseline operational context for the entity and sector."""
    previous_activity: float = Field(..., ge=0.0, le=1.0, description="Historical baseline activity level [0.0 - 1.0]")
    historical_event_count: int = Field(..., ge=0, description="Total historical events recorded for this entity")
    baseline_speed: Optional[float] = Field(default=None, ge=0.0, le=2000.0, description="Expected baseline speed in km/h")
    deviation_history_count: Optional[int] = Field(default=0, ge=0, description="Past recorded anomalous deviations")


class ContextEntityInput(BaseModel):
    """Other known entity active in the operational sector (for relationship detection)."""
    entity_id: str
    entity_type: str
    location: Optional[Coordinates] = None
    last_seen: Optional[datetime] = None
    allegiance: Allegiance = Allegiance.UNKNOWN


class ContextEventInput(BaseModel):
    """Recent event in the operational sector (for event correlation)."""
    event_id: str
    event_type: str
    entity_id: Optional[str] = None
    location: Optional[Coordinates] = None
    timestamp: datetime
    severity: Optional[SeverityLevel] = None


class IntelligenceAnalyzeRequest(BaseModel):
    """
    Primary input payload for POST /api/v1/intelligence/analyze.
    Enforces required structured fields according to Section 4 of NETRA Master Prompt.
    """
    event: EventInput = Field(..., description="Observed event payload")
    entity: EntityInput = Field(..., description="Associated entity payload")
    timestamp: datetime = Field(..., description="Overall assessment timestamp")
    location: Coordinates = Field(..., description="Geospatial context")
    attributes: AttributesInput = Field(..., description="Telemetry and telemetry metrics")
    historical_context: HistoricalContextInput = Field(..., description="Historical baseline for deviation calculation")
    
    # Optional sector context for relationship detection
    context_entities: Optional[List[ContextEntityInput]] = Field(
        default_factory=list,
        description="Sector entity roster for relationship identification"
    )
    context_events: Optional[List[ContextEventInput]] = Field(
        default_factory=list,
        description="Recent sector events for correlation analysis"
    )
