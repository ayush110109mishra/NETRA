"""
Event Pattern Detection Engine for NETRA Intelligence Core.
Detects deterministic, explainable synthetic operational patterns across events:
- Sequential Escalation (e.g. MOVEMENT -> PATROL_DEVIATION -> PERIMETER_PROXIMITY)
- Temporal Bursts (rapid flurry of actions within short window)
- Multi-Entity Coordination (distinct entities operating synchronously in tight proximity)
- Periodic Recurrence (events repeated at regular intervals)
"""

from typing import List, Optional
from config import NetraConfig, default_config
from models.event_intelligence import CanonicalEvent, EventPattern
from events.temporal import TemporalIntelligence
from events.spatial import SpatialIntelligence


class PatternDetector:
    """Deterministic pattern recognition engine."""

    def __init__(self, config: Optional[NetraConfig] = None):
        self.cfg = config or default_config
        self.temporal_intel = TemporalIntelligence(self.cfg)
        self.spatial_intel = SpatialIntelligence(self.cfg)

    def detect_patterns(self, events: List[CanonicalEvent]) -> List[EventPattern]:
        """
        Identify operational patterns from a set of canonical events.
        """
        if len(events) < 2:
            return []

        patterns: List[EventPattern] = []
        sorted_events = sorted(events, key=lambda e: e.timestamp)

        # 1. Pattern 1: Sequential Escalation
        escalation_tiers = {
            "SENSOR_PING": 1,
            "COMMUNICATION": 1,
            "MOVEMENT": 2,
            "SUPPLY_CONVOY": 2,
            "PATROL_DEVIATION": 3,
            "RADAR_ANOMALY": 4,
            "PERIMETER_PROXIMITY": 5,
        }
        tiers = [escalation_tiers.get(e.event_type.upper(), 2) for e in sorted_events]
        # Check if strictly increasing escalation tiers with at least a jump of +2
        is_escalating = len(tiers) >= 2 and all(tiers[i] <= tiers[i+1] for i in range(len(tiers)-1))
        if is_escalating and (max(tiers) - min(tiers) >= 2):
            patterns.append(
                EventPattern(
                    pattern_detected=True,
                    pattern_type="SEQUENTIAL_ESCALATION",
                    confidence=0.88,
                    event_ids=[e.event_id for e in sorted_events],
                    description=(
                        f"Chronological activity escalation detected across {len(sorted_events)} events: "
                        f"{' -> '.join(e.event_type for e in sorted_events)}."
                    ),
                )
            )

        # 2. Pattern 2: Temporal Burst
        bursts = self.temporal_intel.detect_bursts(sorted_events)
        for burst in bursts:
            patterns.append(
                EventPattern(
                    pattern_detected=True,
                    pattern_type="TEMPORAL_BURST",
                    confidence=0.92,
                    event_ids=burst["event_ids"],
                    description=(
                        f"Temporal concentration of {burst['event_count']} events within "
                        f"{int(burst['duration_seconds'])} seconds."
                    ),
                )
            )

        # 3. Pattern 3: Multi-Entity Coordination
        unique_entities = list({ent for e in sorted_events for ent in e.entity_ids})
        if len(unique_entities) >= 2:
            # Check if all events happened within 30 mins and within 3 km
            duration = (sorted_events[-1].timestamp - sorted_events[0].timestamp).total_seconds()
            extent = self.spatial_intel.compute_spatial_extent([e.location for e in sorted_events])
            if duration <= 1800.0 and extent.get("bounding_radius_km", 99.0) <= 3.0:
                patterns.append(
                    EventPattern(
                        pattern_detected=True,
                        pattern_type="MULTI_ENTITY_COORDINATION",
                        confidence=0.85,
                        event_ids=[e.event_id for e in sorted_events],
                        description=(
                            f"Synchronized multi-entity activity observed: entities "
                            f"({', '.join(unique_entities)}) within {extent['bounding_radius_km']:.2f} km radius."
                        ),
                    )
                )

        # 4. Pattern 4: Periodic Recurrence
        recurrence = self.temporal_intel.detect_recurrence(sorted_events)
        if recurrence and recurrence.get("detected"):
            patterns.append(
                EventPattern(
                    pattern_detected=True,
                    pattern_type="PERIODIC_RECURRENCE",
                    confidence=recurrence["confidence"],
                    event_ids=[e.event_id for e in sorted_events],
                    description=(
                        f"Events recur at regular intervals of approximately "
                        f"{recurrence['interval_seconds']} seconds."
                    ),
                )
            )

        return patterns
