"""
Entity Timeline Builder for NETRA Entity Intelligence.
Constructs chronological event streams for Focus Mode with filtering support
(time ranges, event types, severity levels, pagination/limits).
"""

from typing import List, Optional
from datetime import datetime
from models.common import SeverityLevel
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import EntityTimelineItem


class EntityTimelineBuilder:
    """Builds and filters chronological event timelines for an entity."""

    @staticmethod
    def build_timeline(
        events: List[CanonicalEvent],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[str] = None,
        severity: Optional[SeverityLevel] = None,
        limit: Optional[int] = None,
        reverse: bool = True,
    ) -> List[EntityTimelineItem]:
        """
        Build sorted chronological timeline items with optional server-side filters.
        Defaults to reverse=True (most recent first).
        """
        filtered_events = list(events)

        if start_time is not None:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]

        if end_time is not None:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]

        if event_type is not None:
            norm_type = event_type.strip().lower()
            filtered_events = [e for e in filtered_events if e.event_type.lower() == norm_type]

        # Sort chronologically
        filtered_events.sort(key=lambda x: x.timestamp, reverse=reverse)

        items: List[EntityTimelineItem] = []
        for e in filtered_events:
            # Map severity
            sev = EntityTimelineBuilder._resolve_severity(e)
            if severity is not None and sev != severity:
                continue

            # Map risk
            act = float(e.attributes.get("activity_level", 0.30))
            event_risk = round(min(1.0, 0.20 + 0.60 * act), 2)

            # Description
            desc = ""
            if e.raw_event and "description" in e.raw_event:
                desc = str(e.raw_event["description"])
            elif "description" in e.attributes:
                desc = str(e.attributes["description"])
            else:
                desc = f"Synthetic {e.event_type} observation at sector {e.location.sector_id or 'coordinates'}"

            items.append(
                EntityTimelineItem(
                    event_id=e.event_id,
                    event_type=e.event_type,
                    timestamp=e.timestamp,
                    location=e.location,
                    severity=sev,
                    risk=event_risk,
                    description=desc,
                )
            )

        if limit is not None and limit > 0:
            items = items[:limit]

        return items

    @staticmethod
    def _resolve_severity(event: CanonicalEvent) -> SeverityLevel:
        """Derive SeverityLevel from event attributes or taxonomy."""
        sev_attr = event.attributes.get("priority_hint") or event.attributes.get("severity")
        if sev_attr:
            s_str = str(sev_attr).upper()
            for level in SeverityLevel:
                if level.value.upper() == s_str:
                    return level

        # Default rules based on event type
        t = event.event_type.lower()
        if "deviation" in t or "lock" in t:
            return SeverityLevel.HIGH
        if "spoof" in t or "unknown" in t:
            return SeverityLevel.MEDIUM
        return SeverityLevel.LOW
