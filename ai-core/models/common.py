"""
Common enumerations and base schemas for NETRA Intelligence Core.
Supports Phase 1, Phase 2, and Phase 3 specifications.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ClassificationType(str, Enum):
    """Deterministic intelligence classification taxonomy."""
    NORMAL = "NORMAL"
    UNUSUAL = "UNUSUAL"
    ANOMALOUS = "ANOMALOUS"
    HIGH_RISK = "HIGH_RISK"
    UNKNOWN = "UNKNOWN"


class SeverityLevel(str, Enum):
    """Operational severity levels."""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskLevel(str, Enum):
    """Calculated risk bands."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Allegiance(str, Enum):
    """Simulated allegiance classification."""
    FRIENDLY = "FRIENDLY"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"
    SIMULATED_HOSTILE = "SIMULATED_HOSTILE"


class EntityStatus(str, Enum):
    """Entity lifecycle activity states."""
    UNKNOWN = "UNKNOWN"
    ACTIVE = "ACTIVE"
    RECENTLY_ACTIVE = "RECENTLY_ACTIVE"
    INACTIVE = "INACTIVE"
    STALE = "STALE"


class RelationshipType(str, Enum):
    """Types of detected entity and event relationships."""
    SAME_ENTITY = "SAME_ENTITY"
    PARTIAL_ENTITY_OVERLAP = "PARTIAL_ENTITY_OVERLAP"
    SAME_LOCATION = "SAME_LOCATION"
    SPATIAL_PROXIMITY = "SPATIAL_PROXIMITY"
    SPATIAL_CLUSTER = "SPATIAL_CLUSTER"
    SPATIAL_ASSOCIATION = "SPATIAL_ASSOCIATION"
    TEMPORAL_ASSOCIATION = "TEMPORAL_ASSOCIATION"
    TEMPORAL_PROXIMITY = "TEMPORAL_PROXIMITY"
    TEMPORAL_BURST = "TEMPORAL_BURST"
    SIMILAR_TYPE = "SIMILAR_TYPE"
    SEQUENTIAL = "SEQUENTIAL"
    RECURRING_SEQUENCE = "RECURRING_SEQUENCE"
    CO_OCCURRENCE = "CO_OCCURRENCE"
    SHARED_EVENT = "SHARED_EVENT"
    SHARED_CLUSTER = "SHARED_CLUSTER"
    REPEATED_ASSOCIATION = "REPEATED_ASSOCIATION"


class RelationshipStrength(str, Enum):
    """Relationship strength bands."""
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


class EventSource(BaseModel):
    """Originating synthetic sensor/feed metadata for traceability."""
    source_id: str = Field(default="SYNTH-SOURCE-001", description="Identifier of the reporting source")
    source_type: str = Field(default="SIMULATION", description="Type of source (e.g., RADAR, OPTICAL, TELEMETRY, SIMULATION)")
    reliability: float = Field(default=0.90, ge=0.0, le=1.0, description="Assessed source reliability factor")


class Coordinates(BaseModel):
    """Geographic coordinates with validation."""
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees (-90 to +90)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees (-180 to +180)")
    altitude_m: Optional[float] = Field(default=None, description="Optional altitude above sea level in meters")
    sector_id: Optional[str] = Field(default=None, description="Operational sector designation (e.g. SECTOR_ALPHA)")
