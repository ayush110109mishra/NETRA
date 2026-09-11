"""
Canonical Event Normalization Layer for NETRA Intelligence Core.
Transforms heterogeneous raw synthetic inputs (diverse aliases, timestamp representations,
coordinate formats, and entity references) into standardized CanonicalEvent objects.
Preserves raw input and normalization metadata for auditability.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Union
import dateutil.parser

from models.common import Coordinates, EventSource
from models.event_intelligence import CanonicalEvent

# Event type taxonomy and alias mapping
EVENT_TYPE_ALIASES: Dict[str, str] = {
    # Movement aliases
    "movement": "MOVEMENT",
    "move": "MOVEMENT",
    "vehicle_move": "MOVEMENT",
    "vehicle-movement": "MOVEMENT",
    "movement_vehicle": "MOVEMENT",
    "convoy_transit": "MOVEMENT",
    "transit": "MOVEMENT",
    # Patrol deviation aliases
    "patrol_deviation": "PATROL_DEVIATION",
    "patrol-deviation": "PATROL_DEVIATION",
    "deviation": "PATROL_DEVIATION",
    "route_deviation": "PATROL_DEVIATION",
    "off_course": "PATROL_DEVIATION",
    # Radar anomaly aliases
    "radar_anomaly": "RADAR_ANOMALY",
    "radar-anomaly": "RADAR_ANOMALY",
    "rf_spike": "RADAR_ANOMALY",
    "radar_spike": "RADAR_ANOMALY",
    "unidentified_radar": "RADAR_ANOMALY",
    # Sensor ping aliases
    "sensor_ping": "SENSOR_PING",
    "sensor-ping": "SENSOR_PING",
    "ping": "SENSOR_PING",
    "telemetry_ping": "SENSOR_PING",
    "beacon": "SENSOR_PING",
    # Communication aliases
    "communication": "COMMUNICATION",
    "comm_burst": "COMMUNICATION",
    "rf_transmission": "COMMUNICATION",
    # Supply convoy aliases
    "supply_convoy": "SUPPLY_CONVOY",
    "logistics": "SUPPLY_CONVOY",
    # Perimeter proximity aliases
    "perimeter_proximity": "PERIMETER_PROXIMITY",
    "perimeter_breach": "PERIMETER_PROXIMITY",
    "boundary_approach": "PERIMETER_PROXIMITY",
    "intrusion": "PERIMETER_PROXIMITY",
}


class EventNormalizer:
    """Canonical event normalization engine."""

    @staticmethod
    def normalize_event_type(raw_type: str) -> str:
        """Map raw event type alias to canonical uppercase category."""
        if not raw_type:
            return "UNKNOWN"
        cleaned = raw_type.strip().lower().replace(" ", "_")
        return EVENT_TYPE_ALIASES.get(cleaned, cleaned.upper())

    @staticmethod
    def normalize_timestamp(raw_ts: Union[str, datetime, int, float]) -> datetime:
        """Parse diverse timestamp formats into a timezone-aware UTC datetime."""
        if isinstance(raw_ts, datetime):
            if raw_ts.tzinfo is None:
                return raw_ts.replace(tzinfo=timezone.utc)
            return raw_ts.astimezone(timezone.utc)
        if isinstance(raw_ts, (int, float)):
            return datetime.fromtimestamp(raw_ts, tz=timezone.utc)
        if isinstance(raw_ts, str):
            parsed = dateutil.parser.parse(raw_ts)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        raise ValueError(f"Cannot parse timestamp of type {type(raw_ts)}: {raw_ts}")

    @staticmethod
    def normalize_location(raw_loc: Union[Coordinates, Dict[str, Any]]) -> Coordinates:
        """Extract and validate coordinates from dict or model."""
        if isinstance(raw_loc, Coordinates):
            return raw_loc
        if isinstance(raw_loc, dict):
            lat = raw_loc.get("latitude") if "latitude" in raw_loc else raw_loc.get("lat")
            lon = raw_loc.get("longitude") if "longitude" in raw_loc else raw_loc.get("lon")
            if lat is None or lon is None:
                raise ValueError(f"Location missing latitude/longitude in: {raw_loc}")
            alt = raw_loc.get("altitude_m") or raw_loc.get("alt")
            sec = raw_loc.get("sector_id") or raw_loc.get("sector")
            return Coordinates(
                latitude=float(lat),
                longitude=float(lon),
                altitude_m=float(alt) if alt is not None else None,
                sector_id=str(sec) if sec is not None else None,
            )
        raise ValueError(f"Invalid location format: {raw_loc}")

    @staticmethod
    def normalize_entity_ids(raw_event: Dict[str, Any]) -> List[str]:
        """Extract clean list of entity IDs."""
        if "entity_ids" in raw_event and isinstance(raw_event["entity_ids"], list):
            return [str(e) for e in raw_event["entity_ids"] if e]
        if "entity_id" in raw_event and raw_event["entity_id"]:
            return [str(raw_event["entity_id"])]
        if "entity" in raw_event and isinstance(raw_event["entity"], dict):
            e_id = raw_event["entity"].get("entity_id")
            if e_id:
                return [str(e_id)]
        return []

    @classmethod
    def normalize(cls, raw: Union[CanonicalEvent, Dict[str, Any]]) -> CanonicalEvent:
        """Normalize a single raw event dictionary or CanonicalEvent."""
        if isinstance(raw, CanonicalEvent):
            return raw

        raw_dict = dict(raw)

        # 1. Event ID
        event_id = str(raw_dict.get("event_id") or raw_dict.get("id") or "EVT-UNKNOWN")

        # 2. Event Type
        event_type = cls.normalize_event_type(
            raw_dict.get("event_type") or raw_dict.get("type") or "UNKNOWN"
        )

        # 3. Timestamp
        raw_ts = raw_dict.get("timestamp") or raw_dict.get("time") or datetime.now(timezone.utc)
        timestamp = cls.normalize_timestamp(raw_ts)

        # 4. Location
        raw_loc = raw_dict.get("location") or raw_dict.get("coords")
        if not raw_loc:
            raise ValueError(f"Event {event_id} missing mandatory location.")
        location = cls.normalize_location(raw_loc)

        # 5. Entity IDs
        entity_ids = cls.normalize_entity_ids(raw_dict)

        # 6. Attributes
        attributes = raw_dict.get("attributes", {})
        if not isinstance(attributes, dict):
            attributes = {}

        # 7. Source
        raw_src = raw_dict.get("source")
        if isinstance(raw_src, EventSource):
            source = raw_src
        elif isinstance(raw_src, dict):
            source = EventSource(
                source_id=str(raw_src.get("source_id", "SYNTH-SOURCE-001")),
                source_type=str(raw_src.get("source_type", "SIMULATION")),
                reliability=float(raw_src.get("reliability", 0.90)),
            )
        else:
            source = EventSource()

        return CanonicalEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=timestamp,
            location=location,
            entity_ids=entity_ids,
            attributes=attributes,
            source=source,
            raw_event=raw_dict,
            normalization_version="2.0.0",
        )

    @classmethod
    def normalize_batch(cls, raw_events: List[Union[CanonicalEvent, Dict[str, Any]]]) -> List[CanonicalEvent]:
        """Normalize a list of raw event objects."""
        return [cls.normalize(e) for e in raw_events]
