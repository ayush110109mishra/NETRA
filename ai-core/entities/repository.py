"""
In-memory Entity and Event Repository for NETRA Entity Intelligence Engine.
Stores canonical events, derives and maintains canonical entities, and provides
indexed querying for operational analysis.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from models.common import EntityStatus, Allegiance, Coordinates
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity
from config import EntityConfig, default_config


class EntityRepository:
    """
    In-memory entity repository for NETRA.
    Manages canonical entities and their associated event streams.
    """

    def __init__(self, config: Optional[EntityConfig] = None):
        self.config = config or default_config.entity
        # entity_id -> CanonicalEntity
        self._entities: Dict[str, CanonicalEntity] = {}
        # entity_id -> List[CanonicalEvent]
        self._entity_events: Dict[str, List[CanonicalEvent]] = {}
        # event_id -> CanonicalEvent
        self._all_events: Dict[str, CanonicalEvent] = {}

    def add_event(self, event: CanonicalEvent) -> None:
        """Register a canonical event and update entity states."""
        self._all_events[event.event_id] = event

        for entity_id in event.entity_ids:
            if entity_id not in self._entity_events:
                self._entity_events[entity_id] = []
            
            # Avoid duplicate additions
            if not any(e.event_id == event.event_id for e in self._entity_events[entity_id]):
                self._entity_events[entity_id].append(event)
                # Keep sorted by timestamp ascending
                self._entity_events[entity_id].sort(key=lambda x: x.timestamp)

            self._update_entity_state(entity_id)

    def register_entity(self, entity: CanonicalEntity) -> None:
        """Explicitly register or overwrite a canonical entity."""
        self._entities[entity.entity_id] = entity
        if entity.entity_id not in self._entity_events:
            self._entity_events[entity.entity_id] = []

    def get_entity(self, entity_id: str, as_of: Optional[datetime] = None) -> Optional[CanonicalEntity]:
        """
        Retrieve canonical entity by ID.
        If not explicitly registered, derives state dynamically from its recorded events.
        """
        if entity_id in self._entities:
            self._refresh_entity_status(self._entities[entity_id], as_of)
            return self._entities[entity_id]

        if entity_id in self._entity_events and self._entity_events[entity_id]:
            self._update_entity_state(entity_id, as_of)
            return self._entities.get(entity_id)

        return None

    def list_entities(self, as_of: Optional[datetime] = None) -> List[CanonicalEntity]:
        """Return all known entities sorted by entity_id."""
        for entity_id in list(self._entity_events.keys()):
            if entity_id not in self._entities:
                self._update_entity_state(entity_id, as_of)
            else:
                self._refresh_entity_status(self._entities[entity_id], as_of)

        return sorted(list(self._entities.values()), key=lambda e: e.entity_id)

    def get_events_for_entity(self, entity_id: str) -> List[CanonicalEvent]:
        """Retrieve all events associated with an entity, sorted chronologically."""
        return list(self._entity_events.get(entity_id, []))

    def get_all_events(self) -> List[CanonicalEvent]:
        """Retrieve all registered canonical events."""
        return list(self._all_events.values())

    def get_reference_timestamp(self) -> datetime:
        """
        Derive reference timestamp from the latest event in the repository.
        Ensures strict deterministic calculations across testing runs.
        """
        if not self._all_events:
            return datetime.now(timezone.utc)
        return max(e.timestamp for e in self._all_events.values())

    def clear(self) -> None:
        """Clear all stored entities and events."""
        self._entities.clear()
        self._entity_events.clear()
        self._all_events.clear()

    def _update_entity_state(self, entity_id: str, as_of: Optional[datetime] = None) -> None:
        """Derive or refresh CanonicalEntity representation from its recorded events."""
        events = self._entity_events.get(entity_id, [])
        if not events:
            return

        first_obs = min(e.timestamp for e in events)
        last_obs = max(e.timestamp for e in events)
        ref_time = as_of or self.get_reference_timestamp()

        # Compute lifecycle operational state
        delta_hours = max(0.0, (ref_time - last_obs).total_seconds() / 3600.0)
        if delta_hours <= self.config.active_window_hours:
            status = EntityStatus.ACTIVE
        elif delta_hours <= self.config.recently_active_window_hours:
            status = EntityStatus.RECENTLY_ACTIVE
        elif delta_hours <= self.config.stale_window_hours:
            status = EntityStatus.INACTIVE
        else:
            status = EntityStatus.STALE

        # Extract attributes and platform type
        existing = self._entities.get(entity_id)
        entity_type = existing.entity_type if existing else "VEHICLE"
        callsign = existing.callsign if existing else None
        allegiance = existing.allegiance if existing else Allegiance.UNKNOWN
        attrs = dict(existing.attributes) if existing else {}

        # Synthesize from latest event attributes if available
        latest_event = events[-1]
        if latest_event.attributes:
            for k, v in latest_event.attributes.items():
                if k not in attrs:
                    attrs[k] = v
            if "entity_type" in latest_event.attributes and (not existing or existing.entity_type == "VEHICLE"):
                entity_type = str(latest_event.attributes["entity_type"]).upper()
            if "callsign" in latest_event.attributes and not callsign:
                callsign = str(latest_event.attributes["callsign"])
            if "allegiance" in latest_event.attributes:
                try:
                    allegiance = Allegiance(latest_event.attributes["allegiance"])
                except Exception:
                    pass

        canonical = CanonicalEntity(
            entity_id=entity_id,
            entity_type=entity_type,
            callsign=callsign,
            allegiance=allegiance,
            status=status,
            first_observed=first_obs,
            last_observed=last_obs,
            observation_count=len(events),
            event_count=len(events),
            attributes=attrs,
        )
        self._entities[entity_id] = canonical

    def _refresh_entity_status(self, entity: CanonicalEntity, as_of: Optional[datetime] = None) -> None:
        """Update entity lifecycle status based on elapsed time to reference timestamp."""
        ref_time = as_of or self.get_reference_timestamp()
        delta_hours = max(0.0, (ref_time - entity.last_observed).total_seconds() / 3600.0)
        if delta_hours <= self.config.active_window_hours:
            entity.status = EntityStatus.ACTIVE
        elif delta_hours <= self.config.recently_active_window_hours:
            entity.status = EntityStatus.RECENTLY_ACTIVE
        elif delta_hours <= self.config.stale_window_hours:
            entity.status = EntityStatus.INACTIVE
        else:
            entity.status = EntityStatus.STALE
