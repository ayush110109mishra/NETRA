"""
Deterministic event relationship and correlation detection.
Never fabricates relationships; evaluates explicit temporal, spatial, and attribution criteria.
"""

from typing import List, Optional
from datetime import datetime
from models.common import RelationshipType, Coordinates
from models.input import EventInput, ContextEventInput
from models.output import RelatedEventOutput
from models.geo import haversine_distance_km


def detect_event_relationships(
    primary_event: EventInput,
    primary_entity_id: str,
    primary_location: Coordinates,
    context_events: Optional[List[ContextEventInput]],
    temporal_threshold_seconds: float = 7200.0,
    spatial_threshold_km: float = 2.0,
) -> List[RelatedEventOutput]:
    """
    Detect deterministic relationships between the primary event and context events.
    """
    if not context_events:
        return []

    results: List[RelatedEventOutput] = []

    for ce in context_events:
        if ce.event_id == primary_event.event_id:
            continue  # Skip self

        # Calculate time delta in seconds
        time_diff = abs((primary_event.timestamp - ce.timestamp).total_seconds())

        # Check 1: SEQUENTIAL (Same entity and within 30 minutes)
        if ce.entity_id == primary_entity_id and time_diff <= 1800.0:
            confidence = round(0.95 - (time_diff / 1800.0) * 0.1, 2)
            results.append(
                RelatedEventOutput(
                    event_id=ce.event_id,
                    relationship=RelationshipType.SEQUENTIAL,
                    confidence=confidence,
                    details=f"Sequential action by same entity ({primary_entity_id}) within {int(time_diff/60)} mins",
                )
            )
            continue

        # Check 2: SAME_ENTITY
        if ce.entity_id == primary_entity_id:
            results.append(
                RelatedEventOutput(
                    event_id=ce.event_id,
                    relationship=RelationshipType.SAME_ENTITY,
                    confidence=0.92,
                    details=f"Event associated with the same target entity ({primary_entity_id})",
                )
            )
            continue

        # Check 3: SAME_LOCATION / SPATIAL_PROXIMITY
        if ce.location is not None:
            dist = haversine_distance_km(primary_location, ce.location)
            if dist <= spatial_threshold_km:
                confidence = round(max(0.6, 0.90 - (dist / spatial_threshold_km) * 0.3), 2)
                rel_type = (
                    RelationshipType.SAME_LOCATION
                    if dist <= 0.2
                    else RelationshipType.SPATIAL_PROXIMITY
                )
                results.append(
                    RelatedEventOutput(
                        event_id=ce.event_id,
                        relationship=rel_type,
                        confidence=confidence,
                        details=f"Co-located within {dist:.2f} km of primary event coordinates",
                    )
                )
                continue

        # Check 4: TEMPORAL_ASSOCIATION (Close in time)
        if time_diff <= temporal_threshold_seconds:
            confidence = round(max(0.5, 0.85 - (time_diff / temporal_threshold_seconds) * 0.35), 2)
            results.append(
                RelatedEventOutput(
                    event_id=ce.event_id,
                    relationship=RelationshipType.TEMPORAL_ASSOCIATION,
                    confidence=confidence,
                    details=f"Temporal proximity within {int(time_diff / 60)} minutes",
                )
            )
            continue

        # Check 5: SIMILAR_TYPE in reasonable window (4 hours)
        if ce.event_type.lower() == primary_event.event_type.lower() and time_diff <= 14400.0:
            results.append(
                RelatedEventOutput(
                    event_id=ce.event_id,
                    relationship=RelationshipType.SIMILAR_TYPE,
                    confidence=0.68,
                    details=f"Identical synthetic event type '{ce.event_type}' within 4 hours",
                )
            )

    return results
