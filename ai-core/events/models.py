"""
Internal event representations and event taxonomy.
"""

from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel
from models.common import Coordinates, SeverityLevel


class EventCategory(str, Enum):
    MOVEMENT = "movement"
    SENSOR_PING = "sensor_ping"
    COMMUNICATION = "communication"
    PATROL_DEVIATION = "patrol_deviation"
    SUPPLY_CONVOY = "supply_convoy"
    RADAR_ANOMALY = "radar_anomaly"
    PERIMETER_PROXIMITY = "perimeter_proximity"
    UNKNOWN = "unknown"


# Mapping from synthetic event types to baseline severity scores [0.0 - 1.0]
EVENT_TYPE_SEVERITY_BASELINE: Dict[str, float] = {
    "movement": 0.15,
    "sensor_ping": 0.10,
    "communication": 0.12,
    "supply_convoy": 0.20,
    "patrol_deviation": 0.55,
    "radar_anomaly": 0.65,
    "perimeter_proximity": 0.75,
    "unknown": 0.25,
}


class EventBase(BaseModel):
    event_id: str
    event_type: str
    description: str
    location: Optional[Coordinates] = None
    severity: Optional[SeverityLevel] = None
