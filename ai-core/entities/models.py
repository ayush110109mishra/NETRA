"""
Internal entity representations and classifications.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel
from models.common import Allegiance, Coordinates


class PlatformCategory(str, Enum):
    VEHICLE = "vehicle"
    AIRCRAFT = "aircraft"
    VESSEL = "vessel"
    RADAR_STATION = "radar_station"
    PATROL_UNIT = "patrol_unit"
    OUTPOST = "outpost"
    UNKNOWN = "unknown"


class EntityBase(BaseModel):
    entity_id: str
    entity_type: str
    callsign: Optional[str] = None
    allegiance: Allegiance = Allegiance.UNKNOWN
    location: Optional[Coordinates] = None
